package com.example.UserService.repositories;

import com.example.UserService.models.User;
import com.example.UserService.models.Vehicle;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface VehicleRepository extends JpaRepository<Vehicle, Long> {
    // Find all vehicles belonging to a specific owner
    List<Vehicle> findByOwner(User owner);

    // Optional: find a vehicle by VIN (unique identifier)
    Vehicle findByVin(String vin);
}