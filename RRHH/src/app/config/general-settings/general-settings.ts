import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { SelectModule } from 'primeng/select';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-general-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, CardModule, InputTextModule, CheckboxModule, SelectModule, ButtonModule, ToastModule],
  providers: [MessageService],
  templateUrl: './general-settings.html',
  styleUrl: './general-settings.css'
})
export class GeneralSettings {
  settingsForm: FormGroup;
  
  darkMode = signal(false);
  notifications = signal(true);
  emailNotifications = signal(true);

  languages = [
    { label: 'Español', value: 'es' },
    { label: 'English', value: 'en' }
  ];

  themes = [
    { label: 'Claro', value: 'light' },
    { label: 'Oscuro', value: 'dark' }
  ];

  constructor(private fb: FormBuilder, private messageService: MessageService) {
    this.settingsForm = this.fb.group({
      companyName: ['RRHH System', Validators.required],
      language: ['es', Validators.required],
      theme: ['light', Validators.required]
    });
  }

  saveSettings() {
    if (this.settingsForm.valid) {
      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Configuración guardada correctamente'
      });
    }
  }

  resetSettings() {
    this.settingsForm.reset({
      companyName: 'RRHH System',
      language: 'es',
      theme: 'light'
    });
    this.darkMode.set(false);
    this.notifications.set(true);
    this.emailNotifications.set(true);
    
    this.messageService.add({
      severity: 'info',
      summary: 'Reiniciado',
      detail: 'Configuración restaurada a valores por defecto'
    });
  }
}

