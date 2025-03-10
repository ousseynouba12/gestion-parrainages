import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class CandidatService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1'; // Remplacez par l'URL de votre API

  constructor(private http: HttpClient) {}

  /**
   * Vérifie si un candidat existe déjà.
   * @param numElecteur Le numéro de carte d'électeur.
   * @returns Observable avec les informations du candidat.
   */
  verifierCandidat(numElecteur: string): Observable<any> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    });

    return this.http.get(`${this.apiUrl}/electeurs/${numElecteur}`, { headers });
  }

  /**
   * Enregistre un nouveau candidat.
   * @param candidat Les informations du candidat.
   * @returns Observable avec la réponse de l'API.
   */
  enregistrerCandidat(candidat: any): Observable<any> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    });

    return this.http.post(`${this.apiUrl}/candidats`, candidat, { headers });
  }

  /**
   * Récupère la liste de tous les candidats.
   * @returns Observable avec la liste des candidats.
   */
  getCandidats(): Observable<any> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    });

    return this.http.get(`${this.apiUrl}/candidats`, { headers });
  }
}