package com.example.RequestService.strategies;

import com.example.RequestService.models.ServiceRequest;
import java.util.Comparator;
import java.util.List;

public class PriorityBasedStrategy implements SchedulingStrategy {
    @Override
    public ServiceRequest schedule(List<ServiceRequest> pending) {
        return pending.stream()
                .max(Comparator.comparing(req -> req.getPriority().ordinal())) // Use max instead of min
                .orElse(null);
    }
}
