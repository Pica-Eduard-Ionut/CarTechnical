package com.example.UserService.repositories;

import com.example.UserService.models.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;


public interface UserRepository extends JpaRepository<User, Long> {
    // Find a user by email (useful if you need it in future)
    Optional<User> findByEmail(String email);

    // Find all users by role (optional, can be used to list mechanics or owners)
    List<User> findByRole(com.example.UserService.models.Role role);
}
