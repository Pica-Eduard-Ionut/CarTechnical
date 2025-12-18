## Project Overview

This repository implements a **microservices-based car service management system** for a university project.  
The system is split into **three independent services**:

- **UserService (Java / Spring Boot, port 8081)** – manages users and vehicles.
- **RequestService (Java / Spring Boot, port 8082)** – manages service requests, scheduling, and service reports.
- **NotificationService (Python / Flask, port 8083)** – sends email notifications and reminders and stores notification history.

Each service has its **own database** (MariaDB) and communicates with the others via **HTTP REST**. A `docker-compose.yml` file in `Services working together/` runs the whole system.

---

## Architecture & Microservices

### Services & Responsibilities

- **UserService**
  - **Responsibility**: Manage **users** (owners, mechanics, admins) and their **vehicles**.
  - **Database**: `userservice` (via `user-db` container).
  - **Main endpoints**:
    - **POST `/users`** – create user.
    - **GET `/users/{id}`** – get user by ID.
    - **POST `/vehicles`** – create vehicle for an owner.
    - **GET `/vehicles/{id}`** – get vehicle by ID.

- **RequestService**
  - **Responsibility**: Manage **service requests**, **mechanic assignment**, **scheduling**, and **service reports**.
  - **Database**: `requestservice` (via `request-db` container).
  - **Main endpoints**:
    - **POST `/service-requests`** – create service request (validates owner & vehicle with UserService, then notifies NotificationService).
    - **GET `/service-requests/{id}`** – get request by ID.
    - **GET `/service-requests/vehicle/{vehicleId}`** – requests for a vehicle.
    - **GET `/service-requests/status/{status}`** – requests by status (PENDING, CONFIRMED, SCHEDULED, etc.).
    - **PUT `/service-requests/{id}/assign-mechanic`** – assign mechanic to a request and notify NotificationService.
    - **POST `/service-requests/schedule/earliest`** – schedule next request by earliest date.
    - **POST `/service-requests/schedule/priority`** – schedule next request by priority.
    - **POST `/service-reports`** – create service report and mark request as COMPLETED, then notify NotificationService.

- **NotificationService**
  - **Responsibility**: Send **email notifications** and **reminder emails**, track notification history and reminder stats.
  - **Database**: `notificationservice` (via `notification-db` container).
  - **Main endpoints**:
    - **GET `/health`** – health check.
    - **GET `/config/check`** – show SMTP configuration status (no secrets).
    - **POST `/notifications/request-created`** – email when a service request is created. Can fetch extra data from:
      - UserService: `GET /users/{ownerId}`
      - RequestService: `GET /service-requests/{requestId}`
    - **POST `/notifications/request-updated`** – email with details when a request is completed/updated.
    - **POST `/notifications/status-changed`** – email when request status changes.
    - **POST `/reminders/process`** – manually trigger reminder processing (24h before appointment).
    - **GET `/reminders/stats`** – reminder statistics.
    - **GET `/notifications/history`** – list notification history with optional filters (`limit`, `type`, `request_id`, `user_id`).

### Inter-service Communication

- **RequestService → UserService**
  - Validates owners and vehicles before creating service requests:
    - `GET /vehicles/{vehicleId}`
    - `GET /users/{ownerId}`

- **RequestService → NotificationService**
  - After creating a request: `POST /notifications/request-created`.
  - After assigning a mechanic: `POST /notifications/status-changed`.
  - After creating a report (COMPLETED): `POST /notifications/request-updated`.

- **NotificationService → UserService / RequestService**
  - For notifications and reminders:
    - `GET /users/{ownerId}`
    - `GET /service-requests/{requestId}`
    - `GET /service-requests/status/{status}` (to find upcoming appointments).

All communication is **HTTP REST**, using Spring WebFlux `WebClient` in Java services and the `requests` library in Python.

---

## Technologies Used

- **UserService & RequestService**
  - Java 17, Spring Boot 3.5.6
  - Spring Web, Spring Data JPA, Spring WebFlux (`WebClient`)
  - MariaDB driver, Thymeleaf (for UI pages)

- **NotificationService**
  - Python, Flask, Flask-CORS
  - APScheduler (background reminders), `requests`, `pymysql`, `python-dotenv`

- **Databases**
  - MariaDB instances:
    - `user-db` → `userservice`
    - `request-db` → `requestservice`
    - `notification-db` → `notificationservice`

- **Docker**
  - One `Dockerfile` per service.
  - `docker-compose.yml` in `Services working together/` orchestrates all services and databases.

---

## Running the System with Docker

### Prerequisites

- **Docker** and **Docker Compose** installed.
- Internet access to pull base images.

> You do **not** need local Java or Python when using Docker.

### 1. Navigate to the compose folder

From the project root:

```bash
cd "Services working together"
```

### 2. Configure NotificationService SMTP

Create `NotificationService/.env` (if it does not exist) with at least:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
FROM_EMAIL=your_email@gmail.com
```

You can also override DB and service URLs if needed, but Docker provides defaults via environment variables.

### 3. Build and run all services

From `Services working together/`:

```bash
docker compose up --build
```

Or in detached mode:

```bash
docker compose up --build -d
```

After startup:

- UserService: `http://localhost:8081`
- RequestService: `http://localhost:8082`
- NotificationService: `http://localhost:8083`

To stop everything:

```bash
docker compose down
```


---

## CI/CD

GitHub Actions workflows live in [.github/workflows](.github/workflows):

- CI: builds and tests all services, then builds/pushes Docker images on `main` ([ci-cd.yml](.github/workflows/ci-cd.yml)).
- Integration: spins up the full stack with Docker Compose and runs basic health checks ([integration-test.yml](.github/workflows/integration-test.yml)).

### Required Secrets

Set these repository secrets for full CI/CD:

- DOCKER_USERNAME: Docker Hub username
- DOCKER_PASSWORD: Docker Hub access token/password
- SMTP_USERNAME: SMTP user for NotificationService integration tests (e.g., Gmail address)
- SMTP_PASSWORD: SMTP app password
- DEPLOY_HOST: SSH host for deployment (optional)
- DEPLOY_USER: SSH user for deployment (optional)
- DEPLOY_SSH_KEY: Private key for SSH (optional)

Without Docker/Deploy secrets, CI (build + tests) still runs. Docker image push and deploy steps will be skipped.

### Status Badges

You can add badges like:

```
![CI/CD](https://github.com/<OWNER>/<REPO>/actions/workflows/ci-cd.yml/badge.svg)
![Integration](https://github.com/<OWNER>/<REPO>/actions/workflows/integration-test.yml/badge.svg)
```

Replace `<OWNER>` and `<REPO>` with your GitHub org/user and repository name.



