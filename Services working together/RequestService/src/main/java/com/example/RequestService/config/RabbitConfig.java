package com.example.RequestService.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

    @Bean
    public Queue requestQueue() {
        return new Queue("request-queue", true);
    }

    @Bean
    public TopicExchange requestExchange() {
        return new TopicExchange("request-exchange");
    }

    @Bean
    public Binding binding(Queue requestQueue, TopicExchange requestExchange) {
        return BindingBuilder.bind(requestQueue).to(requestExchange).with("request.*");
    }
}
