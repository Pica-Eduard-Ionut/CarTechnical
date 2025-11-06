package org.example.observers;

import org.example.models.ServiceRequest;
import org.example.singletons.NotificationDispatcher;

public class EmailNotifier implements Observer {

    @Override
    public void update(ServiceRequest request) {
        String msg = "[Email] Sending update email for request " + request.getId();
        System.out.println(msg);
        // dispatch via singleton
        NotificationDispatcher.getInstance().dispatch("EmailNotifier", msg);
    }
}
