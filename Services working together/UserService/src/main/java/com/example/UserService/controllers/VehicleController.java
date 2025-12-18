package com.example.UserService.controllers;

import com.example.UserService.dto.CreateVehicleDTO;
import com.example.UserService.dto.VehicleDTO;
import com.example.UserService.services.VehicleService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/vehicles")
@RequiredArgsConstructor
public class VehicleController {

    private final VehicleService vehicleService;

    @PostMapping
    public VehicleDTO createVehicle(@RequestBody CreateVehicleDTO dto) {
        return vehicleService.createVehicle(dto);
    }

    @GetMapping("/{id}")
    public VehicleDTO getVehicleById(@PathVariable Long id) {
        return vehicleService.getVehicleById(id);
    }
}
