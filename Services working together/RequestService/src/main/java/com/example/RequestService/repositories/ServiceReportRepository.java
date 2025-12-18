package com.example.RequestService.repositories;

import com.example.RequestService.models.ServiceReport;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface ServiceReportRepository extends JpaRepository<ServiceReport, Long> {

    // Query reports based on mechanicId from the associated ServiceRequest
    @Query("SELECT sr FROM ServiceReport sr WHERE sr.serviceRequest.mechanicId = :mechanicId")
    List<ServiceReport> findByMechanicId(Long mechanicId);

    // Query by ServiceRequest OwnerId
    List<ServiceReport> findByServiceRequestOwnerId(Long ownerId);
}
