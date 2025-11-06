package org.example.models;

import java.time.LocalDateTime;
import org.example.observers.*;

public class NotificationEvent {
    private Long id;
    private User user;
    private NotificationType type;
    private String payload;
    private LocalDateTime sentAt;
    private NotificationStatus status;

    public NotificationEvent() {}

    public NotificationEvent(Long id, User user, NotificationType type,
                             String payload, LocalDateTime sentAt, NotificationStatus status) {
        this.id = id;
        this.user = user;
        this.type = type;
        this.payload = payload;
        this.sentAt = sentAt;
        this.status = status;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }

    public NotificationType getType() { return type; }
    public void setType(NotificationType type) { this.type = type; }

    public String getPayload() { return payload; }
    public void setPayload(String payload) { this.payload = payload; }

    public LocalDateTime getSentAt() { return sentAt; }
    public void setSentAt(LocalDateTime sentAt) { this.sentAt = sentAt; }

    public NotificationStatus getStatus() { return status; }
    public void setStatus(NotificationStatus status) { this.status = status; }
}
