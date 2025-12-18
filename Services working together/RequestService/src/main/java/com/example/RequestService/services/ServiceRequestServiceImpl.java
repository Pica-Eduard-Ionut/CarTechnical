package com.example.RequestService.services;

import com.example.RequestService.dto.CreateServiceRequestDTO;
import com.example.RequestService.models.*;
import com.example.RequestService.repositories.ServiceRequestRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class ServiceRequestServiceImpl implements ServiceRequestService {

    private final WebClient webClient;
    private final WebClient notificationWebClient;
    private final ServiceRequestRepository serviceRequestRepository;
    private final RequestProducer requestProducer;

    @Autowired
    public ServiceRequestServiceImpl(WebClient.Builder webClientBuilder,
                                     ServiceRequestRepository serviceRequestRepository,
                                     RequestProducer requestProducer) {
        String userServiceUrl = System.getenv().getOrDefault("USER_SERVICE_URL", "http://localhost:8081");
        String notificationServiceUrl = System.getenv().getOrDefault("NOTIFICATION_SERVICE_URL", "http://localhost:8083");
        this.webClient = webClientBuilder.baseUrl(userServiceUrl).build();
        this.notificationWebClient = webClientBuilder.baseUrl(notificationServiceUrl).build();
        this.serviceRequestRepository = serviceRequestRepository;
        this.requestProducer = requestProducer;
    }

    @Override
    public ServiceRequest createServiceRequest(CreateServiceRequestDTO dto) {
        // Validate vehicle and owner by making requests to other microservices
        String vehicleUrl = "/vehicles/" + dto.vehicleId();
        String ownerUrl = "/users/" + dto.ownerId();

        // Fetch vehicle details from the Vehicle service
        Object vehicle = null;
        try {
            vehicle = webClient.get()
                    .uri(vehicleUrl)
                    .retrieve()
                    .bodyToMono(Object.class)
                    .block();  // Wait for the response synchronously
        } catch (WebClientResponseException e) {
            throw new RuntimeException("Vehicle not found: " + e.getMessage());
        }

        // Fetch owner details from the User service
        Object owner = null;
        try {
            owner = webClient.get()
                    .uri(ownerUrl)
                    .retrieve()
                    .bodyToMono(Object.class)
                    .block();  // Wait for the response synchronously
        } catch (WebClientResponseException e) {
            throw new RuntimeException("Owner not found: " + e.getMessage());
        }

        // Create the service request using the appropriate factory
        ServiceRequestFactory factory = ServiceRequestFactory.getFactory(ServiceType.valueOf(dto.serviceType()));
        ServiceRequest serviceRequest = factory.createRequest(
                dto.vehicleId(),
                dto.ownerId(),
                dto.requestedFrom(),
                dto.requestedTo(),
                Priority.valueOf(dto.priority()),
                ServiceType.valueOf(dto.serviceType())
        );

        // Save the service request to the database
        ServiceRequest savedRequest = serviceRequestRepository.save(serviceRequest);
        
        // Notify NotificationService about the created request
        notifyRequestCreated(savedRequest, owner);
        
        return savedRequest;
    }
    
    @Override
    public Optional<ServiceRequest> getServiceRequestById(Long id) {
        return serviceRequestRepository.findById(id);
    }

    @Override
    public List<ServiceRequest> getServiceRequestsByVehicleId(Long vehicleId) {
        // Placeholder for actual implementation
        return serviceRequestRepository.findByVehicleId(vehicleId);
    }

    @Override
    public List<ServiceRequest> getServiceRequestsByStatus(String status) {
        // Placeholder for actual implementation
        return serviceRequestRepository.findByStatus(ServiceStatus.valueOf(status));
    }

    // New method to assign mechanic ID to an existing service request
    @Override
    public ServiceRequest assignMechanicToRequest(Long requestId, Long mechanicId) {
        // Fetch the service request from the DB
        ServiceRequest serviceRequest = serviceRequestRepository.findById(requestId)
                .orElseThrow(() -> new RuntimeException("Service request not found"));

        // Update the mechanic ID
        serviceRequest.setMechanicId(mechanicId);

        // Save the updated service request
        ServiceRequest updatedRequest = serviceRequestRepository.save(serviceRequest);
        
        // Notify NotificationService about the status change
        notifyRequestUpdated(updatedRequest);
        
        return updatedRequest;
    }
    
    /**
     * Notify NotificationService when a service request is created
     */
    private void notifyRequestCreated(ServiceRequest request, Object ownerData) {
        try {
            // Prepare notification payload
            Map<String, Object> notificationPayload = new HashMap<>();
            notificationPayload.put("requestId", request.getId());
            notificationPayload.put("ownerId", request.getOwnerId());
            notificationPayload.put("eventType", "request-created");
            
            // Extract owner email and name from ownerData
            if (ownerData instanceof Map) {
                Map<?, ?> ownerMap = (Map<?, ?>) ownerData;
                Object email = ownerMap.get("email");
                Object name = ownerMap.get("name");
                if (email != null) notificationPayload.put("ownerEmail", email.toString());
                if (name != null) notificationPayload.put("ownerName", name.toString());
            }
            notificationPayload.put("status", request.getStatus() != null ? request.getStatus().name() : "PENDING");
            notificationPayload.put("serviceType", request.getServiceType() != null ? request.getServiceType().name() : "N/A");
            notificationPayload.put("priority", request.getPriority() != null ? request.getPriority().name() : "N/A");

            // Convert to JSON string
            String message = new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(notificationPayload);

            // Send via RabbitMQ
            requestProducer.sendRequestNotification(message);

            System.out.println("Request message sent to RabbitMQ for request " + request.getId());
        } catch (Exception e) {
            System.err.println("Failed to send request notification: " + e.getMessage());
        }
    }


    /**
     * Notify NotificationService when a service request is updated
     */
    private void notifyRequestUpdated(ServiceRequest request) {
        try {
            // Fetch owner info from UserService
            Object owner = null;
            try {
                owner = webClient.get()
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
            notificationPayload.put("newStatus", request.getStatus() != null ? request.getStatus().name() : "PENDING");

            // Convert payload to JSON
            String message = new com.fasterxml.jackson.databind.ObjectMapper()
                    .writeValueAsString(notificationPayload);

            // Send via RabbitMQ
            requestProducer.sendRequestNotification(message);

            System.out.println("Status update message sent to RabbitMQ for request " + request.getId());
        } catch (Exception e) {
            System.err.println("Failed to send status update notification: " + e.getMessage());
        }
    }
}
