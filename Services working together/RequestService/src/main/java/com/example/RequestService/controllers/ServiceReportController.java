package com.example.RequestService.controllers;

import com.example.RequestService.dto.CreateServiceReportDTO;
import com.example.RequestService.models.ServiceReport;
import com.example.RequestService.services.ServiceReportService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/service-reports")
public class ServiceReportController {

    private final ServiceReportService serviceReportService;

    public ServiceReportController(ServiceReportService serviceReportService) {
        this.serviceReportService = serviceReportService;
    }

    @PostMapping
    public ServiceReport createReport(@RequestBody CreateServiceReportDTO reportDTO) {
        return serviceReportService.createServiceReport(reportDTO);
    }
}
