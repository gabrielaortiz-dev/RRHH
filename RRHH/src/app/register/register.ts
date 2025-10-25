import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Navigation } from '../navigation';

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
      
      // Simular registro de usuario (aquí conectarías con tu servicio de registro)
      setTimeout(() => {
        const formData = this.registerForm.value;
        console.log('Datos de registro:', formData);
        
        // Simular éxito en el registro
        this.successMessage = 'Usuario registrado exitosamente. Ya puedes iniciar sesión.';
        this.isLoading = false;
        
        // Limpiar formulario después del éxito
        setTimeout(() => {
          this.registerForm.reset();
          this.successMessage = '';
        }, 3000);
        
      }, 2000);
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
