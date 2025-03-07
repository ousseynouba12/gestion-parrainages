import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root', // Le service est disponible dans toute l'application
})
export class AuthService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1';

  constructor(private http: HttpClient) {}

  // Méthode pour se connecter
  login(email: string, password: string): Observable<any> {
    const body = { username: email, password: password };
    return this.http.post(`${this.apiUrl}/auth/login`, body).pipe(
      tap((response: any) => {
        // Stocker le token dans le localStorage
        //localStorage.setItem('token', response.access_token);
      })
    );
  }

  // Méthode pour se déconnecter
  logout() {
    localStorage.removeItem('token');
  }

  // Méthode pour récupérer le token
  getToken(): string | null {
    return localStorage.getItem('token');
  }
}