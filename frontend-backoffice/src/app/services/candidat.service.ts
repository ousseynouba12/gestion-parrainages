import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Candidat {
  numElecteur: string;
  nom?: string;
  prenom?: string;
  dateNaissance?: string;
  email: string;
  telephone: string;
  partiPolitique?: string;     // Renommé pour correspondre à l'API
   // Ajouté pour correspondre à l'API
  slogan?: string;
  couleur1?: string;
  couleur2?: string;
  couleur3?: string;
  urlInfo?: string;
  photo?: string;
}

export interface CandidatResponse {
  id: number;
  numElecteur: string;
  email: string;
  telephone: string;
  partiPolitique: string;
  codeSecurite: string;
  dateCreation: string;
}

@Injectable({
  providedIn: 'root'
})
export class CandidatService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1';

  constructor(private http: HttpClient) { }

  /**
   * Vérifie si un électeur existe et peut devenir candidat
   */
  verifierCandidat(numElecteur: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/electeurs/${numElecteur}`);
  }

  /**
   * Crée un nouveau candidat et génère un code de sécurité
   * Selon la documentation API, les paramètres attendus sont :
   * numElecteur, email, telephone, parti, profession
   */
  enregistrerCandidat(candidat: Candidat): Observable<CandidatResponse> {
    const candidatData = {
      numElecteur: candidat.numElecteur,
      email: candidat.email,
      telephone: candidat.telephone,
      parti: candidat.partiPolitique || '',
       
    };

    // Endpoint correct selon la documentation: /candidats
    return this.http.post<CandidatResponse>(`${this.apiUrl}/candidats`, candidatData);
  }

  /**
   * Mettre à jour les informations additionnelles du candidat
   */
  updateCandidat(numElecteur: string, candidatData: any): Observable<any> {
    // Endpoint correct selon la documentation: /candidats/{numElecteur}
    return this.http.put<any>(`${this.apiUrl}/candidats/${numElecteur}`, candidatData);
  }

  /**
   * Upload de la photo du candidat
   */
  uploadPhoto(numElecteur: string, photo: File): Observable<any> {
    const formData = new FormData();
    formData.append('photo', photo);
    
    return this.http.post<any>(`${this.apiUrl}/candidats/${numElecteur}/photo`, formData);
  }

  /**
   * Génère un nouveau code de sécurité pour un candidat
   */
  genererCodeSecurite(numElecteur: string): Observable<any> {
    // Endpoint correct selon la documentation: /candidats/{numElecteur}/generer_mdp
    return this.http.post<any>(`${this.apiUrl}/candidats/${numElecteur}/generer_mdp`, {});
  }

  /**
   * Récupère la liste de tous les candidats
   */
  getAllCandidats(): Observable<CandidatResponse[]> {
    return this.http.get<CandidatResponse[]>(`${this.apiUrl}/candidats`);
  }

  /**
   * Récupère les détails d'un candidat
   */
  getCandidat(numElecteur: string): Observable<CandidatResponse> {
    return this.http.get<CandidatResponse>(`${this.apiUrl}/candidats/${numElecteur}`);
  }

  /**
   * Supprime un candidat
   */
  deleteCandidat(numElecteur: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/candidats/${numElecteur}`);
  }
}