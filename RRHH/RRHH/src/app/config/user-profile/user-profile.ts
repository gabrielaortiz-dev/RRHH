import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { AvatarModule } from 'primeng/avatar';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CardModule, InputTextModule, ButtonModule, AvatarModule, ToastModule],
  providers: [MessageService],
  templateUrl: './user-profile.html',
  styleUrl: './user-profile.css'
})
export class UserProfile {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private messageService = inject(MessageService);

  currentUser = this.authService.getCurrentUser();
  profileForm: FormGroup;
  passwordForm: FormGroup;

  constructor() {
    const user = this.currentUser();
    this.profileForm = this.fb.group({
      name: [user?.name || '', Validators.required],
      email: [user?.email || '', [Validators.required, Validators.email]],
      role: [{value: user?.role || '', disabled: true}]
    });

    this.passwordForm = this.fb.group({
      currentPassword: ['', Validators.required],
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    });
  }

  updateProfile() {
    if (this.profileForm.valid) {
      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Perfil actualizado correctamente'
      });
    }
  }

  changePassword() {
    if (this.passwordForm.valid) {
      const { newPassword, confirmPassword } = this.passwordForm.value;
      if (newPassword === confirmPassword) {
        this.messageService.add({
          severity: 'success',
          summary: 'Éxito',
          detail: 'Contraseña actualizada correctamente'
        });
        this.passwordForm.reset();
      } else {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Las contraseñas no coinciden'
        });
      }
    }
  }
}

