package org.example.singletons;

public class NotificationDispatcher {
    private static final NotificationDispatcher INSTANCE = new NotificationDispatcher();

    private NotificationDispatcher() {}

    public static NotificationDispatcher getInstance() {
        return INSTANCE;
    }

    public void dispatch(String channel, String message) {
        System.out.println("[NotificationDispatcher][" + channel + "] " + message);
    }
}
