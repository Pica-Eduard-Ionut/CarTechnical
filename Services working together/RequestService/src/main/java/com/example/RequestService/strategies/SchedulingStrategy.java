package com.example.RequestService.strategies;

import com.example.RequestService.models.ServiceRequest;

import java.util.List;

public interface SchedulingStrategy {
    ServiceRequest schedule(List<ServiceRequest> pendingRequests);
}
