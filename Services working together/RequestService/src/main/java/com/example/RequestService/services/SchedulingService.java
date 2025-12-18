package com.example.RequestService.services;

import com.example.RequestService.models.ServiceRequest;
import com.example.RequestService.strategies.SchedulingStrategy;
import com.example.RequestService.repositories.ServiceRequestRepository;
import com.example.RequestService.models.ServiceStatus;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SchedulingService {

    private final ServiceRequestRepository serviceRequestRepository;
    private final RequestProducer requestProducer;
    private final WebClient userServiceWebClient;

    @Autowired
    public SchedulingService(ServiceRequestRepository serviceRequestRepository, 
                           RequestProducer requestProducer,
                           WebClient.Builder webClientBuilder) {
        this.serviceRequestRepository = serviceRequestRepository;
        this.requestProducer = requestProducer;
        String userServiceUrl = System.getenv().getOrDefault("USER_SERVICE_URL", "http://localhost:8081");
        this.userServiceWebClient = webClientBuilder.baseUrl(userServiceUrl).build();
    }

    // Schedule the next service request based on the selected strategy
    public ServiceRequest scheduleNextServiceRequest(SchedulingStrategy strategy) {
        // Fetch pending requests (You may want to filter based on status or other criteria)
        List<ServiceRequest> pendingRequests = serviceRequestRepository.findByStatus(ServiceStatus.PENDING);

        if (pendingRequests.isEmpty()) {
            throw new RuntimeException("No pending service requests to schedule.");
        }

        // Use the selected strategy to determine which request to schedule
        ServiceRequest scheduledRequest = strategy.schedule(pendingRequests);

        // Update the status of the scheduled request to "SCHEDULED"
        scheduledRequest.setStatus(ServiceStatus.SCHEDULED);

        // Save the updated service request
        ServiceRequest savedRequest = serviceRequestRepository.save(scheduledRequest);
        
        // Notify about the status change
        notifyRequestScheduled(savedRequest);
        
        return savedRequest;
    }
    
    /**
     * Notify NotificationService when a service request is scheduled
     */
    private void notifyRequestScheduled(ServiceRequest request) {
        try {
            // Fetch owner info from UserService
            Object owner = null;
            try {
                owner = userServiceWebClient.get()
                        .uri("/users/" + request.getOwnerId())
                        .retrieve()
                        .bodyToMono(Object.class)
                        .block();
            } catch (Exception e) {
                System.err.println("Failed to fetch owner info for notification: " + e.getMessage());
            }

            String ownerEmail = null;
            String ownerName = null;
            if (owner instanceof Map) {
                Map<?, ?> ownerMap = (Map<?, ?>) owner;
                Object email = ownerMap.get("email");
                Object name = ownerMap.get("name");
                if (email != null) ownerEmail = email.toString();
                if (name != null) ownerName = name.toString();
            }

            // Prepare notification payload
            Map<String, Object> notificationPayload = new HashMap<>();
            notificationPayload.put("requestId", request.getId());
            notificationPayload.put("ownerId", request.getOwnerId());
            notificationPayload.put("eventType", "request-updated");
            if (ownerEmail != null) notificationPayload.put("ownerEmail", ownerEmail);
            if (ownerName != null) notificationPayload.put("ownerName", ownerName);
            notificationPayload.put("newStatus", "SCHEDULED");

            // Convert payload to JSON
            String message = new com.fasterxml.jackson.databind.ObjectMapper()
                    .writeValueAsString(notificationPayload);

            // Send via RabbitMQ
            requestProducer.sendRequestNotification(message);

            System.out.println("Schedule notification sent to RabbitMQ for request " + request.getId());
        } catch (Exception e) {
            System.err.println("Failed to send schedule notification: " + e.getMessage());
        }
    }
}
