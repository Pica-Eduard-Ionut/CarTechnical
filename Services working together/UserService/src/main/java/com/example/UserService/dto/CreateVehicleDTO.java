package com.example.UserService.dto;

public record CreateVehicleDTO(String make, String model, Integer year, String vin, Long mileage, Long ownerId) {}
