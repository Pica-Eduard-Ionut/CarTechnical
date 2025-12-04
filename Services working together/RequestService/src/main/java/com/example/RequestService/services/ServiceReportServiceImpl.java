package com.example.RequestService.services;

import com.example.RequestService.dto.CreateServiceReportDTO;
import com.example.RequestService.models.ServiceReport;
import com.example.RequestService.models.ServiceRequest;
import com.example.RequestService.repositories.ServiceRequestRepository;
import com.example.RequestService.repositories.ServiceReportRepository; // Import the ServiceReportRepository
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.HashMap;
import java.util.Map;

@Service
public class ServiceReportServiceImpl implements ServiceReportService {

    @Autowired
    private ServiceRequestRepository serviceRequestRepository;

    @Autowired
    private ServiceReportRepository serviceReportRepository; // Inject ServiceReportRepository
    
    private final WebClient notificationWebClient;
    private final WebClient userServiceWebClient;

    @Autowired
    public ServiceReportServiceImpl(WebClient.Builder webClientBuilder) {
        String notificationServiceUrl = System.getenv().getOrDefault("NOTIFICATION_SERVICE_URL", "http://localhost:8083");
        String userServiceUrl = System.getenv().getOrDefault("USER_SERVICE_URL", "http://localhost:8081");
        this.notificationWebClient = webClientBuilder.baseUrl(notificationServiceUrl).build();
        this.userServiceWebClient = webClientBuilder.baseUrl(userServiceUrl).build();
    }

    @Override
    public ServiceReport createServiceReport(CreateServiceReportDTO dto) {
        // Fetch the service request details to validate it exists
        ServiceRequest serviceRequest = serviceRequestRepository.findById(dto.getServiceRequestId())
                .orElseThrow(() -> new RuntimeException("Service request not found"));

        // Create the service report
        ServiceReport serviceReport = ServiceReport.builder()
                .serviceRequest(serviceRequest) // Set the ServiceRequest object directly
                .performedAt(dto.getPerformedAt())
                .summary(dto.getSummary())
                .partsUsed(dto.getPartsUsed())
                .totalCost(dto.getTotalCost())
                .build();

        // Save the service report to the database
        ServiceReport savedReport = serviceReportRepository.save(serviceReport);
        
        // Update service request status to COMPLETED and notify
        serviceRequest.setStatus(com.example.RequestService.models.ServiceStatus.COMPLETED);
        serviceRequestRepository.save(serviceRequest);
        
        // Notify NotificationService about the completed service
        notifyServiceCompleted(serviceRequest, savedReport);
        
        return savedReport;
    }
    
    /**
     * Notify NotificationService when a service is completed (report created)
     */
    private void notifyServiceCompleted(ServiceRequest request, ServiceReport report) {
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
                ownerEmail = (String) ownerMap.get("email");
                ownerName = (String) ownerMap.get("name");
            }
            
            // Prepare notification payload
            Map<String, Object> notificationPayload = new HashMap<>();
            notificationPayload.put("requestId", request.getId());
            notificationPayload.put("ownerId", request.getOwnerId());
            if (ownerEmail != null) notificationPayload.put("ownerEmail", ownerEmail);
            if (ownerName != null) notificationPayload.put("ownerName", ownerName);
            notificationPayload.put("newStatus", "COMPLETED");
            notificationPayload.put("mechanicNotes", report.getSummary());
            notificationPayload.put("totalCost", report.getTotalCost());
            notificationPayload.put("partsUsed", report.getPartsUsed());
            
            // Send notification asynchronously (fire and forget)
            notificationWebClient.post()
                    .uri("/notifications/request-updated")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(notificationPayload)
                    .retrieve()
                    .bodyToMono(String.class)
                    .subscribe(
                            result -> System.out.println("Service completion notification sent for request " + request.getId()),
                            error -> System.err.println("Failed to send service completion notification: " + error.getMessage())
                    );
        } catch (Exception e) {
            // Log but don't fail the report creation if notification fails
            System.err.println("Error sending service completion notification: " + e.getMessage());
        }
    }
}
