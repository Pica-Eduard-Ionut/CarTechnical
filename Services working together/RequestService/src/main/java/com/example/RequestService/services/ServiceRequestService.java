package com.example.RequestService.services;

import com.example.RequestService.dto.CreateServiceRequestDTO;
import com.example.RequestService.models.ServiceRequest;

import java.util.List;
import java.util.Optional;

public interface ServiceRequestService {

    // Method to create a new service request
    ServiceRequest createServiceRequest(CreateServiceRequestDTO dto);

    // Method to get a service request by ID
    Optional<ServiceRequest> getServiceRequestById(Long id);

    // Optional: Method to get service requests by vehicle ID (or any other parameter)
    List<ServiceRequest> getServiceRequestsByVehicleId(Long vehicleId);

    // Optional: Method to get service requests by status (for filtering)
    List<ServiceRequest> getServiceRequestsByStatus(String status);

    // New method to assign mechanic ID to an existing service request
    ServiceRequest assignMechanicToRequest(Long requestId, Long mechanicId);
}
