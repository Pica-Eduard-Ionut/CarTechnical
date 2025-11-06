package org.example.observers;

import org.example.models.ServiceRequest;

import java.util.ArrayList;
import java.util.List;

public class NotificationSubject {
    private static final NotificationSubject INSTANCE = new NotificationSubject();
    private final List<Observer> observers = new ArrayList<>();

    private NotificationSubject() {}

    public static NotificationSubject getInstance() {
        return INSTANCE;
    }

    public void attach(Observer observer) {
        observers.add(observer);
    }

    public void detach(Observer observer) {
        observers.remove(observer);
    }

    public void notifyObservers(ServiceRequest request) {
        for (Observer observer : observers) {
            observer.update(request);
        }
    }
}
