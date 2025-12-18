package com.example.RequestService.models;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "service_reports")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ServiceReport {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "service_request_id")
    private ServiceRequest serviceRequest;

    private LocalDateTime performedAt;
    private String summary;
    private String partsUsed;
    private Double totalCost;

    // Access mechanicId from the associated ServiceRequest
    public Long getMechanicId() {
        return serviceRequest.getMechanicId();
    }
}
