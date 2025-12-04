package com.example.RequestService.services;

import com.example.RequestService.dto.CreateServiceReportDTO;
import com.example.RequestService.models.ServiceReport;

public interface ServiceReportService {

    ServiceReport createServiceReport(CreateServiceReportDTO dto);
}
