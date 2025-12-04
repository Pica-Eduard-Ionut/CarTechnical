package com.example.RequestService.services;

import com.example.RequestService.models.ServiceRequest;
import com.example.RequestService.strategies.SchedulingStrategy;
import com.example.RequestService.repositories.ServiceRequestRepository;
import com.example.RequestService.models.ServiceStatus;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SchedulingService {

    private final ServiceRequestRepository serviceRequestRepository;

    @Autowired
    public SchedulingService(ServiceRequestRepository serviceRequestRepository) {
        this.serviceRequestRepository = serviceRequestRepository;
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
        return serviceRequestRepository.save(scheduledRequest);
    }
}
