package org.example;

import org.example.models.*;
import org.example.strategies.*;
import org.example.observers.*;
import org.example.singletons.*;

import java.time.LocalDateTime;
import java.util.List;

public class Main {
    public static void main(String[] args) {

        // users
        User owner = User.builder().name("John").email("john@test.com").role(Role.OWNER).build();
        User mechanic = User.builder().name("Mike").email("mike@test.com").role(Role.MECHANIC).build();

        // vehicle
        Vehicle car = Vehicle.builder().make("Toyota").model("Corolla").year(2018).owner(owner).build();
        owner.addVehicle(car);

        // service requests (factory)
        ServiceRequest req1 = ServiceRequest.builder()
                .vehicle(car).owner(owner).mechanic(mechanic)
                .priority(Priority.HIGH).status(ServiceStatus.PENDING)
                .requestedFrom(LocalDateTime.now().minusDays(2)).build();
        req1.setId(1L);

        ServiceRequest req2 = ServiceRequest.builder()
                .vehicle(car).owner(owner).mechanic(mechanic)
                .priority(Priority.LOW).status(ServiceStatus.PENDING)
                .requestedFrom(LocalDateTime.now().minusDays(1)).build();
        req2.setId(2L);

        ServiceRequest req3 = ServiceRequest.builder()
                .vehicle(car).owner(owner).mechanic(mechanic)
                .priority(Priority.NORMAL).status(ServiceStatus.PENDING)
                .requestedFrom(LocalDateTime.now().minusDays(1)).build();
        req3.setId(3L);

        car.addServiceRequest(req1);
        car.addServiceRequest(req2);
        car.addServiceRequest(req3);
        owner.addRequest(req1);
        owner.addRequest(req2);
        owner.addRequest(req3);

        List<ServiceRequest> pendingRequests = List.of(req3, req1, req2);

        System.out.println("===== CREATED OBJECTS =====");
        System.out.println("Owner: " + owner.getName() + " | " + owner.getEmail() + " | " + owner.getRole());
        System.out.println("Mechanic: " + mechanic.getName() + " | " + mechanic.getEmail() + " | " + mechanic.getRole());
        System.out.println("Vehicle: " + car.getMake() + " | " + car.getModel() + " | " + car.getOwner().getName());
        System.out.println("Service Requests:");
        pendingRequests.forEach(req ->
                System.out.println("  ID: " + req.getId() + " | Vehicle: " + req.getVehicle().getModel() +
                        " | Priority: " + req.getPriority() + " | Requested From: " + req.getRequestedFrom())
        );

        // scheduling strategy (strategy)
        SchedulingStrategy strategy = new PriorityBasedStrategy();
        ServiceRequest nextRequest = strategy.schedule(pendingRequests);

        System.out.println("\n===== NEXT SERVICE REQUEST BASED ON STRATEGY =====");
        if (nextRequest != null) {
            System.out.println("ID: " + nextRequest.getId() + " | Vehicle: " + nextRequest.getVehicle().getModel() +
                    " | Priority: " + nextRequest.getPriority());
        } else {
            System.out.println("No pending requests found.");
        }

        // observer (observer)
        NotificationSubject subject = NotificationSubject.getInstance();
        subject.attach(new EmailNotifier());
        subject.attach(new DashboardNotifier());

        // singleton (singleton)
        System.out.println("\n===== NOTIFICATIONS VIA SINGLETON DISPATCHER =====");
        subject.notifyObservers(nextRequest);
    }
}
