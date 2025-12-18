package com.example.RequestService.events;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import com.example.RequestService.models.ServiceRequest;

@Getter
@RequiredArgsConstructor
public class RequestStatusChangedEvent {
    private final ServiceRequest serviceRequest;
    private final String newStatus;
}
