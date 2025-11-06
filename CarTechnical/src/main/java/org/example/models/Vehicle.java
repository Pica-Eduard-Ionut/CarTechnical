package org.example.models;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

public class Vehicle {
    private Long id;
    private String make;
    private String model;
    private Integer year;
    private String vin;
    private Long mileage;
    private LocalDate lastServiceDate;
    private User owner;
    private List<ServiceRequest> serviceRequests = new ArrayList<>();

    public Vehicle addServiceRequest(ServiceRequest request) {
        serviceRequests.add(request);
        request.setVehicle(this);
        return this;
    }

    public static class Builder {
        private String make, model, vin;
        private Integer year;
        private Long mileage;
        private LocalDate lastServiceDate;
        private User owner;

        public Builder make(String make) { this.make = make; return this; }
        public Builder model(String model) { this.model = model; return this; }
        public Builder year(Integer year) { this.year = year; return this; }
        public Builder vin(String vin) { this.vin = vin; return this; }
        public Builder mileage(Long mileage) { this.mileage = mileage; return this; }
        public Builder lastServiceDate(LocalDate date) { this.lastServiceDate = date; return this; }
        public Builder owner(User owner) { this.owner = owner; return this; }

        public Vehicle build() {
            Vehicle v = new Vehicle();
            v.make = this.make;
            v.model = this.model;
            v.year = this.year;
            v.vin = this.vin;
            v.mileage = this.mileage;
            v.lastServiceDate = this.lastServiceDate;
            v.owner = this.owner;
            return v;
        }
    }

    public static Builder builder() { return new Builder(); }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getMake() {
        return make;
    }

    public void setMake(String make) {
        this.make = make;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public Integer getYear() {
        return year;
    }

    public void setYear(Integer year) {
        this.year = year;
    }

    public String getVin() {
        return vin;
    }

    public void setVin(String vin) {
        this.vin = vin;
    }

    public Long getMileage() {
        return mileage;
    }

    public void setMileage(Long mileage) {
        this.mileage = mileage;
    }

    public LocalDate getLastServiceDate() {
        return lastServiceDate;
    }

    public void setLastServiceDate(LocalDate lastServiceDate) {
        this.lastServiceDate = lastServiceDate;
    }

    public User getOwner() {
        return owner;
    }

    public void setOwner(User owner) {
        this.owner = owner;
    }

    public List<ServiceRequest> getServiceRequests() {
        return serviceRequests;
    }

    public void setServiceRequests(List<ServiceRequest> serviceRequests) {
        this.serviceRequests = serviceRequests;
    }

}
