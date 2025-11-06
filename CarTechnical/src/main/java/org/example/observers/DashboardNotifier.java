package org.example.observers;

import org.example.models.ServiceRequest;
import org.example.singletons.NotificationDispatcher;

public class DashboardNotifier implements Observer {

    @Override
    public void update(ServiceRequest request) {
        String msg = "[Dashboard] Service Request " + request.getId() + " updated to " + request.getStatus();
        System.out.println(msg);
        // dispatch via singleton
        NotificationDispatcher.getInstance().dispatch("DashboardNotifier", msg);
    }
}
