package com.example.UserService.services;

import com.example.UserService.dto.CreateVehicleDTO;
import com.example.UserService.dto.VehicleDTO;
import com.example.UserService.models.User;
import com.example.UserService.models.Vehicle;
import com.example.UserService.repositories.UserRepository;
import com.example.UserService.repositories.VehicleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class VehicleServiceImpl implements VehicleService {

    private final VehicleRepository vehicleRepo;
    private final UserRepository userRepo;

    @Override
    public VehicleDTO createVehicle(CreateVehicleDTO dto) {
        // Find the user who will own the vehicle
        User owner = userRepo.findById(dto.ownerId())
                .orElseThrow(() -> new IllegalArgumentException("Owner not found"));

        // Create the vehicle object and link it to the user
        Vehicle vehicle = Vehicle.builder()
                .make(dto.make())
                .model(dto.model())
                .year(dto.year())
                .vin(dto.vin())
                .mileage(dto.mileage())
                .owner(owner)  // Set the owner of the vehicle
                .build();

        // Save the vehicle to the database
        vehicleRepo.save(vehicle);

        // Return the vehicle's details in the DTO
        return new VehicleDTO(
                vehicle.getId(),
                vehicle.getMake(),
                vehicle.getModel(),
                vehicle.getYear(),
                vehicle.getVin(),
                vehicle.getMileage(),
                owner.getId()  // Return the owner's ID
        );
    }

    @Override
    public VehicleDTO getVehicleById(Long id) {
        Vehicle vehicle = vehicleRepo.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Vehicle not found"));

        return new VehicleDTO(
                vehicle.getId(),
                vehicle.getMake(),
                vehicle.getModel(),
                vehicle.getYear(),
                vehicle.getVin(),
                vehicle.getMileage(),
                vehicle.getOwner().getId()
        );
    }
}
