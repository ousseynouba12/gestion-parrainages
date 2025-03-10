import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1/auth/login';
  
  constructor(private http: HttpClient) {}
  
  login(email: string, password: string): Observable<any> {
    // Créer des paramètres de formulaire (form data)
    const params = new HttpParams()
      .set('username', email)  // Utiliser 'username' au lieu de 'email'
      .set('password', password);
      
    // Définir les en-têtes pour form-urlencoded
    const headers = new HttpHeaders().set(
      'Content-Type', 
      'application/x-www-form-urlencoded'
    );
    
    // Envoyer sous forme de form-urlencoded
    return this.http.post<any>(this.apiUrl, params.toString(), { headers });
  }
}