import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Navigation } from '../navigation';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  registerForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  private navigation = inject(Navigation);
  private authService = inject(AuthService);

  constructor(private fb: FormBuilder) {
    this.registerForm = this.fb.group({
      firstName: ['', [Validators.required, Validators.minLength(2)]],
      lastName: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],
      phone: ['', [Validators.required, Validators.pattern(/^[0-9+\-\s()]+$/)]],
      department: ['', [Validators.required]],
      position: ['', [Validators.required]],
      acceptTerms: [false, [Validators.requiredTrue]]
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(control: AbstractControl): {[key: string]: any} | null {
    const password = control.get('password');
    const confirmPassword = control.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { 'passwordMismatch': true };
    }
    return null;
  }

  onSubmit() {
    if (this.registerForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      const formData = this.registerForm.value;
      
      const registerData = {
        username: formData.email.split('@')[0],
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
        phone: formData.phone
      };
      
      this.authService.register(registerData).subscribe({
        next: (result) => {
          if (result.success) {
            this.successMessage = result.message || 'Usuario registrado exitosamente. Ya puedes iniciar sesión.';
            
            // Limpiar formulario después del éxito
            setTimeout(() => {
              this.registerForm.reset();
              this.successMessage = '';
              this.navigation.showLogin();
            }, 3000);
          } else {
            this.errorMessage = result.message || 'Error al registrar usuario';
          }
          this.isLoading = false;
        },
        error: (error) => {
          this.errorMessage = error.message || 'Error al conectar con el servidor';
          console.error('Error en registro:', error);
          this.isLoading = false;
        }
      });
    } else {
      this.markFormGroupTouched();
    }
  }

  markFormGroupTouched() {
    Object.keys(this.registerForm.controls).forEach(key => {
      const control = this.registerForm.get(key);
      control?.markAsTouched();
    });
  }

  getErrorMessage(fieldName: string): string {
    const control = this.registerForm.get(fieldName);
    
    if (control?.hasError('required')) {
      return `${this.getFieldDisplayName(fieldName)} es requerido`;
    }
    if (control?.hasError('email')) {
      return 'Email inválido';
    }
    if (control?.hasError('minlength')) {
      const requiredLength = control.errors?.['minlength']?.requiredLength;
      return `${this.getFieldDisplayName(fieldName)} debe tener al menos ${requiredLength} caracteres`;
    }
    if (control?.hasError('pattern')) {
      return 'Formato inválido';
    }
    if (control?.hasError('requiredTrue')) {
      return 'Debes aceptar los términos y condiciones';
    }
    return '';
  }

  getFieldDisplayName(fieldName: string): string {
    const fieldNames: {[key: string]: string} = {
      'firstName': 'Nombre',
      'lastName': 'Apellido',
      'email': 'Email',
      'password': 'Contraseña',
      'confirmPassword': 'Confirmar contraseña',
      'phone': 'Teléfono',
      'department': 'Departamento',
      'position': 'Cargo'
    };
    return fieldNames[fieldName] || fieldName;
  }

  isFieldInvalid(fieldName: string): boolean {
    const control = this.registerForm.get(fieldName);
    return !!(control && control.invalid && control.touched);
  }

  hasPasswordMismatch(): boolean {
    return this.registerForm.hasError('passwordMismatch') && 
           (this.registerForm.get('confirmPassword')?.touched ?? false);
  }

  goToLogin() {
    this.navigation.showLogin();
  }
}
