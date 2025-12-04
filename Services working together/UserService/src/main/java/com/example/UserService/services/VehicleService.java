package com.example.UserService.services;


import com.example.UserService.dto.CreateVehicleDTO;
import com.example.UserService.dto.VehicleDTO;

public interface VehicleService {
    VehicleDTO createVehicle(CreateVehicleDTO dto);

    VehicleDTO getVehicleById(Long id);
}
