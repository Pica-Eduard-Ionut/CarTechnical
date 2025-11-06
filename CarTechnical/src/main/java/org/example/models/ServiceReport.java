package org.example.models;

import java.time.LocalDateTime;

public class ServiceReport {
    private Long id;
    private ServiceRequest serviceRequest;
    private User mechanic;
    private LocalDateTime performedAt;
    private String summary;
    private String partsUsed;
    private Double totalCost;

    public ServiceReport() {}

    public static class Builder {
        private ServiceRequest request;
        private User mechanic;
        private LocalDateTime performedAt;
        private String summary;
        private String partsUsed;
        private Double totalCost;

        public Builder serviceRequest(ServiceRequest req) { this.request = req; return this; }
        public Builder mechanic(User mechanic) { this.mechanic = mechanic; return this; }
        public Builder performedAt(LocalDateTime performedAt) { this.performedAt = performedAt; return this; }
        public Builder summary(String summary) { this.summary = summary; return this; }
        public Builder partsUsed(String partsUsed) { this.partsUsed = partsUsed; return this; }
        public Builder totalCost(Double totalCost) { this.totalCost = totalCost; return this; }

        public ServiceReport build() {
            ServiceReport sr = new ServiceReport();
            sr.serviceRequest = this.request;
            sr.mechanic = this.mechanic;
            sr.performedAt = this.performedAt;
            sr.summary = this.summary;
            sr.partsUsed = this.partsUsed;
            sr.totalCost = this.totalCost;
            return sr;
        }
    }

    public static Builder builder() { return new Builder(); }

    // Getters & setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public ServiceRequest getServiceRequest() { return serviceRequest; }
    public void setServiceRequest(ServiceRequest serviceRequest) { this.serviceRequest = serviceRequest; }

    public User getMechanic() { return mechanic; }
    public void setMechanic(User mechanic) { this.mechanic = mechanic; }

    public LocalDateTime getPerformedAt() { return performedAt; }
    public void setPerformedAt(LocalDateTime performedAt) { this.performedAt = performedAt; }

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }

    public String getPartsUsed() { return partsUsed; }
    public void setPartsUsed(String partsUsed) { this.partsUsed = partsUsed; }

    public Double getTotalCost() { return totalCost; }
    public void setTotalCost(Double totalCost) { this.totalCost = totalCost; }

    @Override
    public String toString() {
        return "ServiceReport{" +
                "id=" + id +
                ", serviceRequest=" + serviceRequest +
                ", mechanic=" + mechanic +
                ", performedAt=" + performedAt +
                ", summary='" + summary + '\'' +
                ", partsUsed='" + partsUsed + '\'' +
                ", totalCost=" + totalCost +
                '}';
    }
}
