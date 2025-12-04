package com.example.RequestService.models;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "service_requests")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ServiceRequest {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long vehicleId;
    private Long ownerId;

    private LocalDateTime requestedFrom;
    private LocalDateTime requestedTo;

    @Enumerated(EnumType.STRING)
    private ServiceType serviceType;

    @Enumerated(EnumType.STRING)
    private Priority priority;

    @Enumerated(EnumType.STRING)
    private ServiceStatus status;

    private LocalDateTime createdAt;

    private Long mechanicId;  // mechanicId as Long directly here

    public void setMechanicId(Long mechanicId) {
        this.mechanicId = mechanicId;
    }
}
