package com.example.UserService.models;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "vehicles")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor @Builder
public class Vehicle {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column
    private String make;

    @Column
    private String model;

    @Column
    private Integer year;

    @Column(unique = true, nullable = false)
    private String vin;

    @Column
    private Long mileage;

    @ManyToOne(fetch = FetchType.LAZY)  // Link to User
    @JoinColumn(name = "owner_id", nullable = false)
    private User owner;  // This is the relationship to User

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

    public User getOwner() {
        return owner;
    }

    public void setOwner(User owner) {
        this.owner = owner;
    }
}
