package com.example.RequestService.events;

import com.example.RequestService.models.ServiceRequest;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class RequestEventPublisher {

    @Autowired
    private ApplicationEventPublisher applicationEventPublisher;

    // Method to publish an event when the status of a service request changes
    public void publishStatusChangedEvent(ServiceRequest serviceRequest, String newStatus) {
        RequestStatusChangedEvent event = new RequestStatusChangedEvent(serviceRequest, newStatus);
        applicationEventPublisher.publishEvent(event);
    }
}
