# CarTechnical – Vehicle Maintenance & Scheduling System

## Team Members
- Pica Eduard-Ionut  
- Pasaroiu Mihai-Octavian  

---

## Problem Statement  
The goal of this project is to develop a comprehensive **Vehicle Maintenance and Scheduling Management System** that integrates various components of the automotive service ecosystem to streamline maintenance processes, enhance customer experience, and ensure efficient data management. 

The project aims to compare three architectural approaches — **monolithic**, **containerized**, and **microservices architectures** — evaluating them based on scalability, maintainability, and deployment flexibility. 

The system will connect **vehicle owners**, **mechanics**, and **garage administrators**, enabling seamless interaction and automation of key operations such as **vehicle registration**, **maintenance scheduling**, **service tracking**, **billing**, and **notifications**.  

The application will emphasize **data consistency**, **asynchronous communication**, and **role-based access control** to ensure security and efficient collaboration among all system users.

---

## System Overview  
- Create a distributed vehicle management platform integrating functionalities for owners, garages, and mechanics.  
- Vehicle and service data will be securely stored, continuously updated, and shared across authorized users.  
- Enable interoperability between subsystems (vehicle records, service requests, notifications).  
- Demonstrate good software design principles through the integration of multiple design patterns and microservice-based modularization.

---

## Functionalities

### 1. Vehicle & Owner Records
- Create, update, and retrieve vehicle records (make, model, VIN, mileage, last service date).  
- Link multiple vehicles to a single owner profile.  
- Implement authentication and authorization mechanisms to control access by role (Owner, Mechanic, Admin).  
- Ensure secure and centralized management of all vehicle data.

---

### 2. Appointment Scheduling
- Develop a user-friendly interface for booking, rescheduling, or canceling service appointments.  
- Enable real-time availability checking and conflict prevention for scheduled services.  
- Provide automated notifications for booking confirmations, changes, and reminders.  
- Support different types of maintenance services (inspection, repair, oil change, etc.).

---

### 3. Service Reporting & Maintenance History
- Allow mechanics to generate detailed service reports, including performed tasks, used parts, and total cost.  
- Maintain a comprehensive history of all completed services per vehicle.  
- Enable filtering and searching by vehicle, date range, and mechanic.  
- Ensure data accuracy and traceability for all maintenance activities.

---

### 4. Billing
- Implement transparent billing functionalities, including invoice generation and payment tracking.  
- Provide financial reporting capabilities for both car owners and garage owners.
- Support future integration with external payment systems.

---

## Design Patterns Used

### 1. Factory Method
- **Purpose:** Used for creating different types of `ServiceRequest` objects (e.g., maintenance, repair, inspection) depending on user input.  
- **Problem Solved:** Without the factory, multiple conditional statements would be needed to handle request creation logic.  
- **Advantages:** Enhances extensibility — new request types can be added easily without modifying existing code, ensuring adherence to the **Open-Closed Principle** and improving code maintainability.

---

### 2. Observer
- **Purpose:** Implements a decoupled notification mechanism between system components, allowing the `NotificationService` to react to service or appointment updates.  
- **Problem Solved:** Prevents tight coupling between core logic (appointments) and notification handling.  
- **Advantages:** Promotes scalability by allowing multiple observers (email sender, dashboard notifier) to subscribe independently to system events.

---

### 3. Strategy
- **Purpose:** Used for implementing flexible scheduling algorithms such as - **priority-based**, **earliest-available**, or **mechanic-specific** scheduling.  
- **Problem Solved:** Hardcoding a single scheduling approach reduces flexibility and complicates future changes.  
- **Advantages:** Allows dynamic selection of scheduling strategies at runtime, improving configurability and making the system adaptable to different garage policies or user preferences.

---

### 4. Singleton
- **Purpose:** Ensures a single shared instance of key system components such as `DatabaseConnectionManager` or `NotificationDispatcher`.  
- **Problem Solved:** Prevents creation of multiple conflicting instances that could cause inconsistent state or duplicate notifications.  
- **Advantages:** Centralizes access to shared resources, improves performance, and maintains consistent configuration across the application.

---
