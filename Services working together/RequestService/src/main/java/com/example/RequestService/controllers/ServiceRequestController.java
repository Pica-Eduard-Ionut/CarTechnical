package com.example.RequestService.controllers;

import com.example.RequestService.dto.CreateServiceRequestDTO;
import com.example.RequestService.models.ServiceRequest;
import com.example.RequestService.services.ServiceRequestService;
import com.example.RequestService.services.SchedulingService;  // Import the SchedulingService
import com.example.RequestService.strategies.EarliestAvailableStrategy;
import com.example.RequestService.strategies.PriorityBasedStrategy;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/service-requests")
public class ServiceRequestController {

    private final ServiceRequestService serviceRequestService;
    private final SchedulingService schedulingService;  // Declare SchedulingService

    @Autowired
    public ServiceRequestController(ServiceRequestService serviceRequestService, SchedulingService schedulingService) {
        this.serviceRequestService = serviceRequestService;
        this.schedulingService = schedulingService;  // Inject SchedulingService
    }

    @PostMapping
    public ServiceRequest createServiceRequest(@RequestBody CreateServiceRequestDTO dto) {
        return serviceRequestService.createServiceRequest(dto);
    }

    @GetMapping("/vehicle/{vehicleId}")
    public List<ServiceRequest> getServiceRequestsByVehicleId(@PathVariable Long vehicleId) {
        return serviceRequestService.getServiceRequestsByVehicleId(vehicleId);
    }

    @GetMapping("/{id}")
    public ServiceRequest getServiceRequestById(@PathVariable Long id) {
        return serviceRequestService.getServiceRequestById(id)
                .orElseThrow(() -> new RuntimeException("Service request not found"));
    }

    @GetMapping("/status/{status}")
    public List<ServiceRequest> getServiceRequestsByStatus(@PathVariable String status) {
        return serviceRequestService.getServiceRequestsByStatus(status);
    }

    @PutMapping("/{id}/assign-mechanic")
    public ServiceRequest assignMechanicToRequest(@PathVariable Long id, @RequestBody Long mechanicId) {
        return serviceRequestService.assignMechanicToRequest(id, mechanicId);
    }

    @PostMapping("/schedule/earliest")
    public ServiceRequest scheduleEarliestRequest() {
        return schedulingService.scheduleNextServiceRequest(new EarliestAvailableStrategy());
    }

    @PostMapping("/schedule/priority")
    public ServiceRequest schedulePriorityRequest() {
        return schedulingService.scheduleNextServiceRequest(new PriorityBasedStrategy());
    }
}
