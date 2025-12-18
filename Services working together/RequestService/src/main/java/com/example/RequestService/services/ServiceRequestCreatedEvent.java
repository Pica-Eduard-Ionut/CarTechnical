package com.example.RequestService.services;

import com.example.RequestService.models.ServiceRequest;
import lombok.Getter;
import org.springframework.context.ApplicationEvent;

@Getter
public class ServiceRequestCreatedEvent extends ApplicationEvent {
    private final ServiceRequest request;

    public ServiceRequestCreatedEvent(Object source, ServiceRequest request) {
        super(source);
        this.request = request;
    }
}

