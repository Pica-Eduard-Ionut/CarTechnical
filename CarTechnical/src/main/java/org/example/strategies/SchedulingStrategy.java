package org.example.strategies;

import org.example.models.ServiceRequest;
import java.util.List;

public interface SchedulingStrategy {
    ServiceRequest schedule(List<ServiceRequest> pendingRequests);
}
