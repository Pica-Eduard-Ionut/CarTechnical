package com.example.RequestService.services;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

@Service
public class RequestProducer {
    private final RabbitTemplate rabbitTemplate;

    public RequestProducer(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void sendRequestNotification(String message) {
        rabbitTemplate.convertAndSend("request-exchange", "request.created", message);
    }
}
