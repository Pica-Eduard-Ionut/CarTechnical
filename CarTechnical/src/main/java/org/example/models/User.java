package org.example.models;

import java.util.ArrayList;
import java.util.List;

public class User {
    private Long id;
    private String name;
    private String email;
    private String passwordHash;
    private Role role;
    private List<Vehicle> vehicles = new ArrayList<>();
    private List<ServiceRequest> requests = new ArrayList<>();
    private List<NotificationEvent> notifications = new ArrayList<>();

    public User addVehicle(Vehicle vehicle) {
        vehicles.add(vehicle);
        vehicle.setOwner(this);
        return this;
    }

    public User addRequest(ServiceRequest request) {
        requests.add(request);
        request.setOwner(this);
        return this;
    }

    public User addNotification(NotificationEvent notification) {
        notifications.add(notification);
        notification.setUser(this);
        return this;
    }

    // Simple Builder
    public static class Builder {
        private Long id;
        private String name;
        private String email;
        private String password;
        private Role role;

        public Builder id(Long id) { this.id = id; return this; }
        public Builder name(String name) { this.name = name; return this; }
        public Builder email(String email) { this.email = email; return this; }
        public Builder password(String password) { this.password = password; return this; }
        public Builder role(Role role) { this.role = role; return this; }

        public User build() {
            User user = new User();
            user.id = this.id;
            user.name = this.name;
            user.email = this.email;
            user.passwordHash = this.password; // no encryption locally
            user.role = this.role;
            return user;
        }
    }

    public static Builder builder() { return new Builder(); }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }

    public Role getRole() {
        return role;
    }

    public void setRole(Role role) {
        this.role = role;
    }

    public List<Vehicle> getVehicles() {
        return vehicles;
    }

    public void setVehicles(List<Vehicle> vehicles) {
        this.vehicles = vehicles;
    }

    public List<ServiceRequest> getRequests() {
        return requests;
    }

    public void setRequests(List<ServiceRequest> requests) {
        this.requests = requests;
    }

    public List<NotificationEvent> getNotifications() {
        return notifications;
    }

    public void setNotifications(List<NotificationEvent> notifications) {
        this.notifications = notifications;
    }
}
