import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NotificationService } from '../services/notification.service';
import { AuthService } from '../services/auth.service';
import { Notification, NotificationType } from '../models/notification.model';

@Component({
  selector: 'app-notification-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notification-panel.html',
  styleUrl: './notification-panel.css'
})
export class NotificationPanel implements OnInit {
  private notificationService = inject(NotificationService);
  private authService = inject(AuthService);
  private router = inject(Router);

  currentUser = this.authService.getCurrentUser();
  notifications = signal<Notification[]>([]);
  unreadCount = signal<number>(0);
  panelVisible = signal<boolean>(false);
  showOnlyUnread = signal<boolean>(false);

  displayedNotifications = computed(() => {
    const all = this.notifications();
    return this.showOnlyUnread() ? all.filter(n => !n.isRead) : all;
  });

  ngOnInit(): void {
    this.loadNotifications();
    
    const user = this.currentUser();
    if (user?.email && this.notifications().length === 0) {
      this.notificationService.createSampleNotifications(user.email);
      this.loadNotifications();
    }
  }

  loadNotifications(): void {
    const user = this.currentUser();
    if (user?.email) {
      const userNotifications = this.notificationService.getUserNotifications(user.email);
      this.notifications.set(userNotifications);
      this.unreadCount.set(this.notificationService.getUserUnreadCount(user.email));
    }
  }

  togglePanel() {
    this.panelVisible.update(val => !val);
    if (this.panelVisible()) {
      this.loadNotifications();
    }
  }

  closePanel() {
    this.panelVisible.set(false);
  }

  getNotificationIcon(type: NotificationType): string {
    const icons = {
      'info': 'pi-info-circle',
      'success': 'pi-check-circle',
      'warning': 'pi-exclamation-triangle',
      'error': 'pi-times-circle',
      'approval': 'pi-thumbs-up',
      'request': 'pi-inbox',
      'reminder': 'pi-clock',
      'expiration': 'pi-calendar-times'
    };
    return `pi ${icons[type] || 'pi-bell'}`;
  }

  onNotificationClick(notification: Notification, event: Event): void {
    event.stopPropagation();
    
    if (!notification.isRead) {
      this.notificationService.markAsRead(notification.id);
      this.loadNotifications();
    }

    if (notification.redirectUrl) {
      this.closePanel();
      this.router.navigate([notification.redirectUrl]);
    }
  }

  markAllAsRead(): void {
    const user = this.currentUser();
    if (user?.email) {
      this.notificationService.markAllAsRead(user.email);
      this.loadNotifications();
    }
  }

  deleteNotification(notificationId: string, event: Event): void {
    event.stopPropagation();
    this.notificationService.deleteNotification(notificationId);
    this.loadNotifications();
  }

  deleteAllRead(): void {
    const user = this.currentUser();
    if (user?.email) {
      this.notificationService.deleteAllRead(user.email);
      this.loadNotifications();
    }
  }

  formatDate(date: Date): string {
    const now = new Date();
    const notifDate = new Date(date);
    const diffMs = now.getTime() - notifDate.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Ahora';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours} h`;
    if (diffDays < 7) return `Hace ${diffDays} días`;
    
    return notifDate.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }
}
