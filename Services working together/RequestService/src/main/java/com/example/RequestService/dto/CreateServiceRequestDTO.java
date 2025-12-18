package com.example.RequestService.dto;

import java.time.LocalDateTime;

public record CreateServiceRequestDTO(Long vehicleId, Long ownerId, LocalDateTime requestedFrom, LocalDateTime requestedTo,
                                      String serviceType, String priority) {}
