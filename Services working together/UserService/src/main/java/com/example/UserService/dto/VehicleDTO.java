package com.example.UserService.dto;


public record VehicleDTO(Long id, String make, String model, Integer year, String vin, Long mileage, Long ownerId) {}
