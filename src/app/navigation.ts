import { Injectable, signal } from '@angular/core';

export type ViewType = 'login' | 'register';

@Injectable({
  providedIn: 'root'
})
export class Navigation {
  private currentView = signal<ViewType>('login');

  getCurrentView() {
    return this.currentView.asReadonly();
  }

  showLogin() {
    this.currentView.set('login');
  }

  showRegister() {
    this.currentView.set('register');
  }
}
