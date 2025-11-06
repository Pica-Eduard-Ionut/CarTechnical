# CarTechnical – Vehicle Maintenance & Scheduling System

## Team Members
- Pica Eduard-Ionut  
- Pasaroiu Mihai-Octavian  

---
## Overview
**CarTechnical** is a proof-of-concept Java application that models a simplified **vehicle service management system**.  
It demonstrates the integration and interaction of four core design patterns within an extensible architecture.

The project focuses on design clarity and code maintainability, rather than full functionality. It includes:
- A comprehensive UML class diagram covering the entire system  
- Two detailed UML sequence diagrams illustrating key use cases  
- Implementation of four design patterns in Java  

## Implemented Design Patterns

| Pattern | Purpose | Key Classes |
|----------|----------|-------------|
| **Builder** | Simplifies complex object creation for `User`, `Vehicle`, and `ServiceRequest` | `User`, `Vehicle`, `ServiceRequest` |
| **Strategy** | Enables flexible scheduling strategies for selecting service requests | `SchedulingStrategy`, `PriorityBasedStrategy` |
| **Observer** | Enables notification dispatch when a service request is updated or processed | `NotificationSubject`, `EmailNotifier`, `DashboardNotifier` |
| **Singleton** | Ensures a single shared notification center instance | `NotificationSubject` |


## System Design Summary

### **Core Concept**
Car owners submit service requests for their vehicles, which mechanics then schedule and process.  
The system prioritizes these requests using the **Strategy pattern**, while updates trigger notifications via the **Observer** and **Singleton** patterns. Object creation uses the **Builder** pattern to enhance readability and flexibility.


## UML Class Diagram

![](/class%20uml.png)

### Diagram Highlights:
- All classes are interconnected to show relationships among **models**, **strategies**, **observers**, and **singleton components**.  
- Each design pattern is clearly annotated with UML **notes**, pointing to the relevant classes.  
- The diagram emphasizes **pattern integration** rather than isolated subsystems.

**Classes included:**
- `User`, `Vehicle`, `ServiceRequest`, `Role`, `Priority`, `ServiceStatus`
- `SchedulingStrategy`, `PriorityBasedStrategy`
- `NotificationSubject`, `EmailNotifier`, `DashboardNotifier`

## UML Sequence Diagrams

### **Sequence 1 – ServiceRequest**
![](/Sequence1%20-%20ServiceRequest.jpeg)

**Scenario:**  
An owner submits a new service request for their vehicle.  
- The system builds the request using the **Builder pattern**.  
- The owner associates the request with their vehicle.  
- The service request is recorded and marked as pending for further scheduling.

### **Sequence 2 – ServiceReport**
![](/Sequence2%20-%20ServiceReport.jpeg)

**Scenario:**  
A mechanic reviews pending service requests and completes a service report.  
- The **Strategy pattern** determines which request to process next based on priority.  
- Once completed, the **Observer pattern** notifies all registered observers (email and dashboard).  
- The notification flow is managed through the **Singleton** notification dispatcher.


## Implementation Details

### **1. Builder Pattern**
Simplifies object construction for `User`, `Vehicle`, and `ServiceRequest`.

```java
User owner = User.builder().name("John").email("john@test.com").role(Role.OWNER).build();
Vehicle car = Vehicle.builder().make("Toyota").model("Corolla").year(2018).owner(owner).build();
ServiceRequest req = ServiceRequest.builder()
    .vehicle(car).owner(owner).priority(Priority.HIGH).status(ServiceStatus.PENDING).build();
```


### **2. Strategy Pattern**

Defines interchangeable scheduling strategies for selecting the next service request.

```java
SchedulingStrategy strategy = new PriorityBasedStrategy();
ServiceRequest nextRequest = strategy.schedule(pendingRequests);
```
Different strategies can be implemented (e.g., time-based, load-based) by extending SchedulingStrategy.

### **3. Observer Pattern**

Used for real-time notifications when a service request changes state.
```java
NotificationSubject subject = NotificationSubject.getInstance();
subject.attach(new EmailNotifier());
subject.attach(new DashboardNotifier());
subject.notifyObservers(nextRequest);
```

Each observer reacts differently, e.g., sending an email or updating a dashboard.

### **4. Singleton Pattern**

Ensures a single instance of the notification dispatcher throughout the application.
```java
public class NotificationSubject {
    private static NotificationSubject instance;
    private List<Notifier> observers = new ArrayList<>();

    private NotificationSubject() {}

    public static synchronized NotificationSubject getInstance() {
        if (instance == null) instance = new NotificationSubject();
        return instance;
    }
}
```

## How the Patterns Work Together

Builder creates rich domain objects (User, Vehicle, ServiceRequest).

Strategy determines the optimal request to process next.

Observer + Singleton manage centralized notifications for updates.

Together, they form a modular and extensible system.

## Proof of Concept (Main.java)

The Main class demonstrates the integrated design patterns:

Create User, Vehicle, and ServiceRequest objects via Builder

Determine next request using Strategy

Register and notify observers through a Singleton Observer system

Example Output
```
===== CREATED OBJECTS =====
Owner: John | john@test.com | OWNER
Mechanic: Mike | mike@test.com | MECHANIC
Vehicle: Toyota | Corolla | John
Service Requests:
  ID: 3 | Vehicle: Corolla | Priority: NORMAL | Requested From: 2025-11-04
  ID: 1 | Vehicle: Corolla | Priority: HIGH | Requested From: 2025-11-03
  ID: 2 | Vehicle: Corolla | Priority: LOW | Requested From: 2025-11-05

===== NEXT SERVICE REQUEST BASED ON STRATEGY =====
ID: 1 | Vehicle: Corolla | Priority: HIGH

===== NOTIFICATIONS VIA SINGLETON DISPATCHER =====
[EmailNotifier] Notification sent to mechanic: Mike
[DashboardNotifier] Dashboard updated for request ID 1
```

## Conclusion

This project demonstrates:

  - Integration of four design patterns in a cohesive, real-world context
  UML documentation showing pattern relationships
  - Sequence diagrams depicting main use cases
  - A proof-of-concept Java implementation showcasing the interaction of all patterns
  - This fulfills the design and implementation requirements for a design-pattern-driven project in Java.