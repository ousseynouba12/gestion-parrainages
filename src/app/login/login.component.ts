import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true, // ✅ Composant standalone
  imports: [FormsModule, CommonModule], // Import des modules nécessaires
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private router: Router, private authService: AuthService) {}

  // Méthode appelée lors de la soumission du formulaire
  onLogin() {
    if (this.email && this.password) {
      this.authService.login(this.email, this.password).subscribe({
        next: (response) => {
          // Redirection vers le tableau de bord après une connexion réussie
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          this.errorMessage = 'Email ou mot de passe incorrect';
        },
      });
    } else {
      this.errorMessage = 'Veuillez remplir tous les champs';
    }
  }
}