package com.example.RequestService.models;

import java.time.LocalDateTime;

public abstract class ServiceRequestFactory {

    // Now accepts vehicleId instead of Vehicle
    public abstract ServiceRequest createRequest(
            Long vehicleId,
            Long ownerId,
            LocalDateTime from,
            LocalDateTime to,
            Priority priority,
            ServiceType serviceType
    );

    public static ServiceRequestFactory getFactory(ServiceType type) {
        return switch (type) {
            case MAINTENANCE -> new MaintenanceRequestFactory();
            case REPAIR -> new RepairRequestFactory();
            case OIL_CHANGE -> new OilChangeRequestFactory();
            case INSPECTION -> new InspectionRequestFactory();
        };
    }
}
class MaintenanceRequestFactory extends ServiceRequestFactory {
    @Override
    public ServiceRequest createRequest(Long vehicleId, Long ownerId, LocalDateTime from, LocalDateTime to, Priority p, ServiceType serviceType) {
        return ServiceRequest.builder()
                .vehicleId(vehicleId)
                .ownerId(ownerId)
                .serviceType(serviceType)  // Pass enum directly
                .requestedFrom(from)
                .requestedTo(to)
                .priority(p)
                .status(ServiceStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .build();
    }
}

class RepairRequestFactory extends ServiceRequestFactory {
    @Override
    public ServiceRequest createRequest(Long vehicleId, Long ownerId, LocalDateTime from, LocalDateTime to, Priority p, ServiceType serviceType) {
        return ServiceRequest.builder()
                .vehicleId(vehicleId)
                .ownerId(ownerId)
                .serviceType(serviceType)  // Pass enum directly
                .requestedFrom(from)
                .requestedTo(to)
                .priority(p)
                .status(ServiceStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .build();
    }
}

class InspectionRequestFactory extends ServiceRequestFactory {
    @Override
    public ServiceRequest createRequest(Long vehicleId, Long ownerId, LocalDateTime from, LocalDateTime to, Priority p, ServiceType serviceType) {
        return ServiceRequest.builder()
                .vehicleId(vehicleId)
                .ownerId(ownerId)
                .serviceType(serviceType)  // Pass enum directly
                .requestedFrom(from)
                .requestedTo(to)
                .priority(p)
                .status(ServiceStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .build();
    }
}

class OilChangeRequestFactory extends ServiceRequestFactory {
    @Override
    public ServiceRequest createRequest(Long vehicleId, Long ownerId, LocalDateTime from, LocalDateTime to, Priority p, ServiceType serviceType) {
        return ServiceRequest.builder()
                .vehicleId(vehicleId)
                .ownerId(ownerId)
                .serviceType(serviceType)  // Pass enum directly
                .requestedFrom(from)
                .requestedTo(to)
                .priority(p)
                .status(ServiceStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .build();
    }
}

