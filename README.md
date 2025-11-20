# CarTechnical – Vehicle Maintenance & Scheduling System

## Team Members
- Pica Eduard-Ionut  
- Pasaroiu Mihai-Octavian  

---

# 1) Monolithic Architecture

## System Structure in a Monolithic Architecture

In a monolithic architecture, the user interface, business logic, and data access logic—operates as one unified and tightly coupled codebase. For this project, the web application used by Owners, Mechanics, and Admins interacts with a single backend service that contains all modules within the same deployable unit.

## Client Layer: Web App

- Users (Owner, Mechanic, Admin) access the system through a Web App.
- The web client communicates with the server using HTTP/HTTPS requests.

## Server Layer: Monolithic Backend Application

All backend functionality is packaged inside one executable or deployment artifact.  

The following modules exist inside the monolith:

### **User & Vehicle Module**
Manages user profiles, authentication, authorization, and vehicle data.

### **Scheduling & Service Requests Module**
Handles maintenance bookings, service updates, job assignments, and service status workflows.

### **Billing Module**
Processes service fees, payment tracking, and invoice generation.

### **Notification Module**
Sends alerts and updates related to appointments, service completions, or administrative messages.

These modules communicate internally through function calls, not APIs, since everything resides in the same runtime.

## Data Layer: Application Database

- A single relational database stores all application data.
- All modules read from and write to this same database through a shared data access layer.
- No data boundaries exist between modules.

## Data Flow Summary

1. User interacts with the Web App.
2. Request travels over the Internet to the Monolithic Web Server.
3. The backend routes the request to the appropriate internal module.
4. The module retrieves/stores information from/to the Application Database.
5. Response is returned to the user through the web interface.

## Component
![](./component%20monolithic.jpg)

## Deployment
![](./deployment%20monolithic.jpg)

## Pros:
- **Simpler initial development**: all functionality resides in a single unified codebase, making early development straightforward.
- **Easy deployment**: only one deployment artifact to build and release; no coordination across multiple services.
- **Fast internal communication**: modules interact via in-process function calls instead of network APIs, reducing latency and complexity.
- **Centralized data management**: a single relational database ensures strong ACID transactions and simplifies consistency.
- **Lower infrastructure requirements**: no need for service discovery, API gateways, or distributed tracing tools.
- **Cost-effective for early stages**: one server or container can run the entire system.

## Cons:
- **Scalability limitations**: the entire application must scale as a unit, even if only one module experiences heavy load.
- **Deployment coupling**: any update, no matter how small, requires redeploying the entire application.
- **Maintainability issues as system grows**: codebase becomes large and tightly coupled, making changes riskier over time.
- **Limited fault isolation**: a failure in one module (e.g., billing or notifications) can bring down the entire system.
- **Increased downtime during updates**: full redeployment leads to system-wide downtime unless complex deployment strategies are used.
---
# 2) Microservices Architecture (synchronous & bounded contexts)
## Microservices Architecture — Structure & Components

The system is organized as a set of independent, domain-based microservices behind a central **API Gateway**.  
Users (Owner, Mechanic, Admin) interact through the **Web Client**, which communicates exclusively with the API Gateway.  
Each microservice owns its **own database**, ensuring loose coupling and service autonomy.


## **Core Microservices**

### **1. User & Vehicle Management Service**
- Handles user accounts, roles, authentication data, and all vehicle-related information.  
- Owns the **User & Vehicle DB**.  
- Serves client requests routed through the **API Gateway**.

### **2. Appointment & Scheduling Service**
- Handles service requests, appointment creation, scheduling, and lifecycle management.  
- Uses the **Appointment DB**.  
- Interacts with:
  - **User & Vehicle Service** (validate owner/mechanic)
  - **Notification Service** (send reminders/updates)
  - **Billing Service** (finalize service cost after completion)

### **3. Notification Service**
- Receives event triggers from other services (e.g., appointment confirmed, upcoming deadlines).  
- Sends notifications through various channels (email, dashboard alerts, SMS later).  
- Stores notification records in the **Notification DB**.  
- Fully decoupled and event-driven.

### **4. Billing Service**
- Manages service cost calculation, invoicing, and payment statuses.  
- Uses the **Billing DB**.  
- Communicates with the Appointment Service and the Notification Service.


## **Data Flow**

1. The **User** interacts with the system via the **Web Client**.  
2. The Web Client sends requests to the **API Gateway**.  
3. The API Gateway forwards each request to the correct microservice.  
4. Each microservice:
   - Accesses **its own database** only.
   - Sends commands or events to other services when necessary  
     (e.g., *appointment created → send notification*).
5. The **Notification Service** delivers alerts, reminders, and updates to users.


## Component
![](./component%20microservices.jpg)

## Deployment
![](./deployment%20diagram%20microservices.jpg)

## Pros
- Clear separation of domains (User/Vehicle, Appointments, Notifications, Billing).
- Independent scaling: Appointment service can scale separately from Billing or Notifications.
- Strong fault isolation: A failure in Billing or Notifications does not affect scheduling or vehicle operations.
- Independent databases ensure loose coupling and domain-specific data models.
- API Gateway acts as a unified entry point, simplifying authentication and routing.
- Easy to extend: New services (e.g., Parts Inventory, SMS Service) can be added without modifying existing services.

## Cons
- Requires more DevOps setup (API Gateway, service discovery, monitoring, logging, tracing).
- Debugging becomes harder since logic is distributed across many services.
- Increased network communication introduces latency and possible communication failures.
- Data consistency must rely on events or eventual consistency rather than a single transaction.
---
# 3) Event-Driven Distributed Architecture (EDA) — Message-centric (Event Sourcing / CQRS optional)

## Overview — structure & components

- Domain services (similar bounded services as in microservices): auth, vehicle, request, scheduling, mechanic, report, notification — each publishes and consumes domain events.
- Event Bus / Message Broker: central backbone (Kafka/RabbitMQ). Topics: RequestCreated, AppointmentScheduled, RequestStatusChanged, ServiceCompleted, NotificationRequested, etc.
- Event store (optional): for event sourcing, keeps immutable log of domain events.
- Read-model / Query-materializer: services (or a dedicated "read-store" service) build denormalized read models (CQRS) for dashboards / queries.
- Command API: services expose lightweight command endpoints (REST/gRPC). Commands result in domain events written to bus.
- Consumers: notification-service subscribes to AppointmentScheduled and ServiceCompleted events and sends emails; analytics service consumes events to build reports.

## Data flow (create request):
1. Client -> request-service (command).
2. request-service validates, persists minimal state (or emits RequestCreated event if using event store).
3. RequestCreated on bus -> scheduling-service consumes and tries to schedule; on success scheduling-service emits AppointmentScheduled.
4. AppointmentScheduled consumed by request-service to update state (or read-model), and byThe system follows an event-driven style where services communicate indirectly through a **Message Broker** instead of calling each other directly.  
The **Web Browser → API Gateway** path is still used for client-initiated operations, but all cross-service workflows (notifications, billing triggers, status updates) happen asynchronously.

---

## Core Components

### **1. User & Vehicle Service**
- Handles user accounts, roles, and vehicle information.  
- Owns the **User & Vehicle DB**.  
- Communicates *only* with the API Gateway (no direct service-to-service calls).

### **2. Appointment & Scheduling Service**
- Creates and updates service appointments.  
- Stores data in the **Appointment DB**.  
- Publishes events to the **Message Broker**, such as:
  - `appointment.created`
  - `appointment.scheduled`
  - `appointment.completed`
  - `billing.required`
  - `notification.required`

This service is the main event producer.

### **3. Message Broker**
- Central asynchronous hub (Kafka/RabbitMQ).  
- Delivers events to subscribers (Billing and Notification services).  
- Ensures loose coupling and reliable event propagation.

### **4. Billing Service**
- Subscribes to events like `billing.required` or `appointment.completed`.  
- Generates invoices, calculates costs, and updates the **Billing DB**.  
- No direct communication with other services—everything is event-driven.

### **5. Notification Service**
- Subscribes to events such as `notification.required`.  
- Sends reminders, confirmations, and updates via email/dashboard channels.  
- Stores outgoing messages in the **Notification DB**.

---

## Event-Driven Data Flow

1. **User interacts through the Web Browser** → API Gateway → target microservice.
2. When an appointment is created or its status changes, the **Appointment & Scheduling Service**:
   - writes to its **Appointment DB**  
   - **publishes events** to the Message Broker.
3. The **Billing Service** listens to billing-related events and updates its Billing DB.
4. The **Notification Service** listens to notification events and sends messages.
5. No service calls another directly — all cross-context communication flows **through the Message Broker**.



## Component
![](./component%20event%20driven.jpg)

## Deployment
![](./deployment%20event%20driven.jpg)

### Pros
- **Loose coupling**: Services communicate through events, not direct calls, reducing dependencies.
- **High scalability**: Each service (Billing, Notifications, Appointments) scales independently based on event load.
- **Asynchronous performance**: User-facing actions remain fast because long tasks run in the background.
- **Resilience to failure**: If Billing or Notifications go down, events pile up in the broker without blocking the system.
- **Natural fit for workflows**: Appointment creation automatically triggers notifications/billing without service-to-service calls.
- **Easier to extend**: New services can subscribe to existing events without modifying current services.
- **Improved observability option**: Event logs act as a natural audit trail of system activity.

### Cons
- **More complex debugging**: Failures are harder to trace because logic is distributed across events.
- **Eventual consistency**: Data across services may not be updated at the same time; no single ACID transaction.
- **Infrastructure overhead**: Requires managing a message broker (Kafka/RabbitMQ) and monitoring event flow.
- **Harder error handling**: Retry logic, dead-letter queues, and idempotency must be carefully implemented.
- **Higher cognitive load**: Developers must understand event schemas, topics, and asynchronous patterns.
- **Risk of event explosion**: Too many events make the system noisy and hard to maintain.
---
# Architecture Style Comparison

## 1. Monolithic Architecture

The monolithic architecture offers a straightforward approach where all system functionality resides within a single, unified codebase. This simplicity makes it highly suitable during early development, as the system is easier to implement, test, and deploy. However, as the application evolves, its tightly coupled structure becomes a significant limitation. Scaling the system requires scaling the entire application, even if only one module—such as notifications or scheduling—experiences heavy workload. Additionally, any update requires a full-system redeployment, causing downtime and hindering development velocity. Over time, these characteristics reduce maintainability and increase technical debt.

**Pros:** Simple design, easy deployment, minimal infrastructure requirements, ideal for small teams and early prototypes.

**Cons:** Poor scalability, tightly coupled components, full redeployment needed for any change, increasingly difficult to maintain as the codebase grows.

---

## 2. Event-Driven Architecture

The event-driven architecture provides a highly decoupled and reactive system design. Services communicate by publishing and subscribing to events, enabling asynchronous workflows that are particularly effective for tasks such as notification delivery, appointment updates, and background processing. This results in improved system responsiveness and the ability to scale individual event consumers independently.  
However, adopting an event-driven style introduces significant complexity. Debugging becomes harder due to the indirect flow of execution across event streams, and the system must manage eventual consistency across services. The reliance on message brokers also increases operational overhead and requires careful design to prevent issues such as event duplication, ordering problems, and dead-letter queues.

**Pros:** High decoupling, excellent for asynchronous tasks, scalable event consumption, natural fit for notifications and analytics.

**Cons:** Increased debugging difficulty, reliance on complex messaging infrastructure, eventual consistency challenges, higher system complexity.

---

## 3. Microservices Architecture

Microservices architecture divides the system into multiple independently deployable services, each responsible for a specific domain such as authentication, vehicles, scheduling, billing, or notifications. This separation aligns closely with the natural boundaries of the project, allowing each service to evolve, scale, and be deployed without affecting the others. It supports parallel development across team members and provides a strong foundation for long-term maintainability.  
The trade-off is an increased need for DevOps capabilities, including containerization, service discovery, centralized logging, distributed monitoring, and an API gateway. While more complex to operate, microservices offer the greatest flexibility and scalability among the three architectural styles.

**Pros:** Independent scaling and deployment, strong domain isolation, enhanced maintainability, supports parallel development, future-proof.

**Cons:** Higher operational complexity, requires advanced DevOps infrastructure and monitoring.

---

# Final Comparison and Selection

When comparing the three architectures, each presents strengths suited to different project stages and priorities:
- The **monolithic architecture** excels in simplicity and ease of deployment but becomes increasingly restrictive as the system expands. Its tight coupling and limited scalability make it unsuitable for long-term growth.
- The **event-driven architecture** is highly effective for asynchronous workflows and system responsiveness. However, its complexity, eventual consistency, and debugging difficulty make it better suited as a complementary style rather than the primary architectural backbone.
- The **microservices architecture** offers the best balance for this project. It maps naturally to the system’s domain boundaries (Users/Vehicles, Scheduling, Billing, Notifications), allows independent scaling of high-load components, and supports incremental development and deployment. Although it requires more sophisticated infrastructure, the long-term gains in flexibility and maintainability outweigh the initial costs.

---

# Conclusion: Microservices as the Most Suitable Choice

Microservices provide the strongest alignment with the project’s functional domains, performance requirements, and expected evolution. They enable scalable, modular, and maintainable development while avoiding the rigidity of a monolith and the operational complexity of a fully event-driven ecosystem. For these reasons, **microservices are the most suitable architecture for the system** and offer the most robust long-term solution.
