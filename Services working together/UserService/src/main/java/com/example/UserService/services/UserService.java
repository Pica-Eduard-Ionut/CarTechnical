package com.example.UserService.services;

import com.example.UserService.dto.CreateUserDTO;
import com.example.UserService.dto.UserDTO;
import com.example.UserService.models.User;

public interface UserService {
    UserDTO createUser(CreateUserDTO dto);
    User getById(Long id);
}