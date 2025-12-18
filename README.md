
## Project Overview
This project implements a **microservices-based system** for managing vehicle service requests and user notifications.  
The system demonstrates **asynchronous communication using RabbitMQ**, **service decoupling**, and a **fully automated CI/CD pipeline** using GitHub Actions.

The architecture follows modern microservices best practices:
- Independent services
- Database per service
- Event-driven communication
- Containerized deployment

---

## Architecture Overview

### Microservices
| Service | Technology | Description |
|------|-----------|-------------|
| **User Service** | Java | Manages user data |
| **Request Service** | Java | Handles vehicle service requests and publishes events |
| **Notification Service** | Python | Consumes events and sends notifications |
| **RabbitMQ** | Message Broker | Asynchronous event delivery |
| **MariaDB** | Database | Separate database per service |

Each service is **independently deployable** and communicates either via HTTP or events.

---

## Message Queue Integration (RabbitMQ)

### Why RabbitMQ?
RabbitMQ is used to enable **asynchronous, event-driven communication** between the Request Service and the Notification Service.

This avoids tight coupling and allows services to scale and fail independently.

---

## Event Flow

### 1. Event Producer – Request Service (Java)

The `ServiceRequestServiceImpl` publishes events to RabbitMQ when:
- A **service request is created**
- A **service request is updated** (e.g. mechanic assigned)

#### Example: Event Published on Request Creation
```java
requestProducer.sendRequestNotification(message);
{
  "requestId": 12,
  "ownerId": 5,
  "ownerEmail": "user@example.com",
  "ownerName": "John Doe",
  "status": "PENDING",
  "serviceType": "REPAIR",
  "priority": "HIGH"
}
```
### 2. Event Consumer – Notification Service (Python)

The `Notification Service`:

- Subscribes to the RabbitMQ queue
- Consumes messages asynchronously
- Sends email or system notifications based on the event
  
If the Notification Service is unavailable:
- Messages remain safely in RabbitMQ
- Processing resumes once the service is back online
  
| Benefit| Explanation|
| --------------------------- | ------------------------- |
| **Decoupling**              | Request Service never directly calls Notification Service |
| **Scalability**             | Multiple consumers can be added                           |
| **Fault Tolerance**         | Messages are not lost if a service crashes                |
| **Asynchronous Processing** | User requests are processed faster                        |


# Docker & Containerization

Each service runs in its own container:
- Independent Dockerfiles
- Shared Docker Compose network
- Separate volumes for databases
  
| Service              | URL                                              |
| -------------------- | ------------------------------------------------ |
| User Service         | [http://localhost:8081](http://localhost:8081)   |
| Request Service      | [http://localhost:8082](http://localhost:8082)   |
| Notification Service | [http://localhost:8083](http://localhost:8083)   |
| RabbitMQ UI          | [http://localhost:15672](http://localhost:15672) |


### RabbitMQ Credentials:
```bash
username: guest
password: guest
```

# CI/CD Pipeline (GitHub Actions)
### Overview

The project uses GitHub Actions to automatically:
- Build
- Test
- Package
- Deploy the microservices

The pipeline runs on:
- Push to `main` or `develop`
- Pull requests

# CI Pipeline Stages

### Unit Testing
- Java services tested using JUnit
- Python service tested using Pytest
- MariaDB containers spun up for isolated testing
  

### Docker Image Build

- Builds Docker images for:
  - User Service
  - Request Service
  - Notification Service
- Images are pushed to Docker Hub

### Integration Testing (Docker Compose)

- Entire system is started using Docker Compose
- Includes:
  - All services
  - RabbitMQ
  - Databases
- Health checks ensure services are running correctly

### Deployment
- Latest images are pulled
- Containers are restarted
- Old containers and unused images are removed
  
This results in automatic deployment on every push to `main`.
