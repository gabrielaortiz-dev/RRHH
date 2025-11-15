import { Injectable, signal } from '@angular/core';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
  read: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notifications = signal<Notification[]>([]);
  
  allNotifications = this.notifications.asReadonly();
  unreadCount = signal(0);
  
  constructor() {
    this.loadNotifications();
  }

  private loadNotifications() {
    if (typeof window === 'undefined') return;
    
    const stored = localStorage.getItem('notifications');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        this.notifications.set(parsed.map((n: any) => ({
          ...n,
          timestamp: new Date(n.timestamp)
        })));
        this.updateUnreadCount();
      } catch (e) {
        console.error('Error loading notifications:', e);
      }
    }
  }

  private saveNotifications() {
    if (typeof window === 'undefined') return;
    localStorage.setItem('notifications', JSON.stringify(this.notifications()));
  }

  private updateUnreadCount() {
    const count = this.notifications().filter(n => !n.read).length;
    this.unreadCount.set(count);
  }

  addNotification(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) {
    const newNotification: Notification = {
      ...notification,
      id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      read: false
    };
    
    const current = this.notifications();
    this.notifications.set([newNotification, ...current]);
    this.updateUnreadCount();
    this.saveNotifications();
    
    return newNotification.id;
  }

  success(title: string, message: string) {
    return this.addNotification({ title, message, type: 'success' });
  }

  error(title: string, message: string) {
    return this.addNotification({ title, message, type: 'error' });
  }

  info(title: string, message: string) {
    return this.addNotification({ title, message, type: 'info' });
  }

  warning(title: string, message: string) {
    return this.addNotification({ title, message, type: 'warning' });
  }
}
