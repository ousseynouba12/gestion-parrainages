import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PeriodeService {
  private apiUrl = 'http://localhost:5000/api/periode'; // Remplace par l'URL de ton API

  constructor(private http: HttpClient) {}


  getPeriode(): Observable<any> {
    return this.http.get(`${this.apiUrl}`);
  }


  setPeriode(data: { dateDebut: string; dateFin: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}`, data);
  }


  fermerPeriode(): Observable<any> {
    return this.http.put(`${this.apiUrl}/fermer`, {});
  }
}
