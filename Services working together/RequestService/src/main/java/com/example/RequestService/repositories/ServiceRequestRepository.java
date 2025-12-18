package com.example.RequestService.repositories;

import com.example.RequestService.models.ServiceRequest;
import com.example.RequestService.models.ServiceStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ServiceRequestRepository extends JpaRepository<ServiceRequest, Long> {

    List<ServiceRequest> findByStatus(ServiceStatus status);

    List<ServiceRequest> findByOwnerId(Long ownerId);

    // Query for requests by mechanicId directly
    List<ServiceRequest> findByMechanicId(Long mechanicId);
    List<ServiceRequest> findByVehicleId(Long vehicleId);
}
