import { Component, signal, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Login } from './login/login';
import { Register } from './register/register';
import { Navigation } from './navigation';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Login, Register],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('RRHH');
  private navigation = inject(Navigation);
  
  get currentView() {
    return this.navigation.getCurrentView();
  }
}
