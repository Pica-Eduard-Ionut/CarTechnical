package com.example.UserService.controllers;

import com.example.UserService.dto.CreateUserDTO;
import com.example.UserService.dto.UserDTO;
import com.example.UserService.models.User; // <-- Correct import
import com.example.UserService.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService service;

    @PostMapping
    public ResponseEntity<?> create(@RequestBody CreateUserDTO dto) {
        try {
            UserDTO userDTO = service.createUser(dto);
            return ResponseEntity.status(HttpStatus.CREATED).body(userDTO);
        } catch (IllegalArgumentException e) {
            // Handle duplicate email or validation errors
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", e.getMessage());
            errorResponse.put("status", HttpStatus.CONFLICT.value());
            return ResponseEntity.status(HttpStatus.CONFLICT).body(errorResponse);
        } catch (Exception e) {
            // Handle other errors
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to create user: " + e.getMessage());
            errorResponse.put("status", HttpStatus.INTERNAL_SERVER_ERROR.value());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    @GetMapping("/{id}")
    public UserDTO getById(@PathVariable Long id) {
        User u = service.getById(id); // <-- Correct entity type
        if (u == null) return null;
        return new UserDTO(u.getId(), u.getName(), u.getEmail(), u.getRole().name());
    }
}
