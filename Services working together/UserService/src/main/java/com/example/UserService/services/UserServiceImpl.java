package com.example.UserService.services;

import com.example.UserService.dto.CreateUserDTO;
import com.example.UserService.dto.UserDTO;
import com.example.UserService.models.Role;
import com.example.UserService.models.User; // <-- Correct import
import com.example.UserService.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Service
public class UserServiceImpl implements UserService {

    private final UserRepository repo;
    private final WebClient notificationWebClient;

    public UserServiceImpl(UserRepository repo, WebClient.Builder webClientBuilder) {
        this.repo = repo;
        String notificationServiceUrl = System.getenv().getOrDefault("NOTIFICATION_SERVICE_URL", "http://localhost:8083");
        this.notificationWebClient = webClientBuilder.baseUrl(notificationServiceUrl).build();
    }

    @Override
    public UserDTO createUser(CreateUserDTO dto) {
        // Check if user with this email already exists
        Optional<User> existingUser = repo.findByEmail(dto.email());
        if (existingUser.isPresent()) {
            throw new IllegalArgumentException("User with email '" + dto.email() + "' already exists");
        }
        
        User u = User.builder()
                .name(dto.name())
                .email(dto.email())
                .role(Role.valueOf(dto.role()))
                .build();

        try {
            repo.save(u);
        } catch (DataIntegrityViolationException e) {
            // Handle duplicate email constraint violation
            if (e.getMessage() != null && e.getMessage().contains("Duplicate entry")) {
                throw new IllegalArgumentException("User with email '" + dto.email() + "' already exists");
            }
            throw e;
        }

        UserDTO userDTO = new UserDTO(u.getId(), u.getName(), u.getEmail(), u.getRole().name());
        
        // Optionally notify NotificationService about new user creation (for welcome emails, etc.)
        // This is commented out by default, but can be enabled if needed
        // notifyUserCreated(userDTO);
        
        return userDTO;
    }
    
    /**
     * Notify NotificationService when a user is created (optional - for welcome emails)
     */
    private void notifyUserCreated(UserDTO user) {
        try {
            Map<String, Object> notificationPayload = new HashMap<>();
            notificationPayload.put("userId", user.id());
            notificationPayload.put("userName", user.name());
            notificationPayload.put("userEmail", user.email());
            notificationPayload.put("role", user.role());
            
            // Send notification asynchronously (fire and forget)
            notificationWebClient.post()
                    .uri("/notifications/user-created") // This endpoint would need to be added to NotificationService if used
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(notificationPayload)
                    .retrieve()
                    .bodyToMono(String.class)
                    .subscribe(
                            result -> System.out.println("User creation notification sent for user " + user.id()),
                            error -> System.err.println("Failed to send user creation notification: " + error.getMessage())
                    );
        } catch (Exception e) {
            // Log but don't fail user creation if notification fails
            System.err.println("Error sending user creation notification: " + e.getMessage());
        }
    }

    @Override
    public User getById(Long id) {
        return repo.findById(id).orElse(null);
    }
}
