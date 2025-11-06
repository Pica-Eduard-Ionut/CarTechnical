package org.example.models;

import java.time.LocalDateTime;

public class ServiceRequest {
    private Long id;
    private Vehicle vehicle;
    private User owner;
    private User assignedMechanic;
    private LocalDateTime requestedFrom;
    private LocalDateTime requestedTo;
    private ServiceType serviceType;
    private Priority priority;
    private ServiceStatus status;
    private LocalDateTime createdAt;
    private ServiceReport report;

    public ServiceRequest attachReport(ServiceReport report) {
        this.report = report;
        report.setServiceRequest(this);
        return this;
    }

    public static class Builder {
        private Vehicle vehicle;
        private User owner;
        private User mechanic;
        private LocalDateTime from;
        private LocalDateTime to;
        private ServiceType serviceType;
        private Priority priority;
        private ServiceStatus status;
        private LocalDateTime createdAt;

        public Builder vehicle(Vehicle vehicle) { this.vehicle = vehicle; return this; }
        public Builder owner(User owner) { this.owner = owner; return this; }
        public Builder mechanic(User mechanic) { this.mechanic = mechanic; return this; }
        public Builder requestedFrom(LocalDateTime from) { this.from = from; return this; }
        public Builder requestedTo(LocalDateTime to) { this.to = to; return this; }
        public Builder serviceType(ServiceType type) { this.serviceType = type; return this; }
        public Builder priority(Priority priority) { this.priority = priority; return this; }
        public Builder status(ServiceStatus status) { this.status = status; return this; }
        public Builder createdAt(LocalDateTime createdAt) { this.createdAt = createdAt; return this; }

        public ServiceRequest build() {
            ServiceRequest sr = new ServiceRequest();
            sr.vehicle = this.vehicle;
            sr.owner = this.owner;
            sr.assignedMechanic = this.mechanic;
            sr.requestedFrom = this.from;
            sr.requestedTo = this.to;
            sr.serviceType = this.serviceType;
            sr.priority = this.priority;
            sr.status = this.status;
            sr.createdAt = this.createdAt;
            return sr;
        }
    }

    public static Builder builder() { return new Builder(); }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Vehicle getVehicle() {
        return vehicle;
    }

    public void setVehicle(Vehicle vehicle) {
        this.vehicle = vehicle;
    }

    public User getOwner() {
        return owner;
    }

    public void setOwner(User owner) {
        this.owner = owner;
    }

    public User getAssignedMechanic() {
        return assignedMechanic;
    }

    public void setAssignedMechanic(User assignedMechanic) {
        this.assignedMechanic = assignedMechanic;
    }

    public LocalDateTime getRequestedFrom() {
        return requestedFrom;
    }

    public void setRequestedFrom(LocalDateTime requestedFrom) {
        this.requestedFrom = requestedFrom;
    }

    public LocalDateTime getRequestedTo() {
        return requestedTo;
    }

    public void setRequestedTo(LocalDateTime requestedTo) {
        this.requestedTo = requestedTo;
    }

    public ServiceType getServiceType() {
        return serviceType;
    }

    public void setServiceType(ServiceType serviceType) {
        this.serviceType = serviceType;
    }

    public Priority getPriority() {
        return priority;
    }

    public void setPriority(Priority priority) {
        this.priority = priority;
    }

    public ServiceStatus getStatus() {
        return status;
    }

    public void setStatus(ServiceStatus status) {
        this.status = status;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public ServiceReport getReport() {
        return report;
    }

    public void setReport(ServiceReport report) {
        this.report = report;
    }

    @Override
    public String toString() {
        return "ServiceRequest{" +
                "id=" + id +
                ", vehicle=" + vehicle +
                ", owner=" + owner +
                ", assignedMechanic=" + assignedMechanic +
                ", requestedFrom=" + requestedFrom +
                ", requestedTo=" + requestedTo +
                ", serviceType=" + serviceType +
                ", priority=" + priority +
                ", status=" + status +
                ", createdAt=" + createdAt +
                ", report=" + report +
                '}';
    }
}
