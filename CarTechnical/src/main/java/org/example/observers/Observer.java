package org.example.observers;

import org.example.models.ServiceRequest;

public interface Observer {
    void update(ServiceRequest request);
}