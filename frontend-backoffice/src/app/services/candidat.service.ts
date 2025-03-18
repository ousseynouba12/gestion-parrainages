import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError, retry, tap } from 'rxjs/operators';
import {switchMap} from 'rxjs/operators';

export interface Candidat {
  numElecteur: string;
  nom?: string;
  prenom?: string;
  dateNaissance?: string;
  email: string;
  telephone: string;
  partiPolitique?: string;
  slogan?: string;
  couleur1?: string;
  couleur2?: string;
  couleur3?: string;
  urlInfo?: string;
  photo?: string;
} 
export interface Electeur {
numElecteur : string;
nom : string;
prenom : string;
dateNaissance :string;

}

export interface CandidatResponse {
  id: number;
  numElecteur: string;
  email: string;
  telephone: string;
  partiPolitique: string;
  slogan?: string;
  couleur1?: string;
  couleur2?: string;
  couleur3?: string;
  urlInfo?: string;
  photo?: string;
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
   * Gestion des erreurs HTTP
   */
  private handleError(error: HttpErrorResponse) {  
    let errorMessage = '';
    
    if (error.status === 0) {
      // Erreur côté client ou problème réseau
      errorMessage = `Erreur de connexion: ${error.message}`;
      console.error('Problème de connexion au serveur:', error);
    } else if (error.status === 500) {
      errorMessage = `Erreur serveur interne (500): Le serveur ne répond pas correctement`;
      console.error('Erreur 500 du serveur:', error);
    } else {
      // Le backend a retourné un code d'erreur
      errorMessage = `Le serveur a retourné: ${error.status}, message: ${error.message}`;
      console.error(`API a retourné le code ${error.status}:`, error);
    }
    
    // Retourne un observable avec un message d'erreur pour informer l'utilisateur
    return throwError(() => new Error(errorMessage));
  }

  /**
   * Vérifie si un électeur existe et peut devenir candidat
   */
  verifierCandidat(numElecteur: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/electeurs/${numElecteur}`)
      .pipe(
        retry(1), // Réessayer une fois en cas d'échec
        catchError(this.handleError)
      );
  }

  /**
   * Crée un nouveau candidat et génère un code de sécurité
   */
  /**
 * Crée un nouveau candidat après vérification de l'électeur
 */
  enregistrerCandidat(candidat: Candidat, numElecteur: string): Observable<CandidatResponse> {
    const candidatData = {
      numElecteur: numElecteur,
      email: candidat.email,
      telephone: candidat.telephone,
      partiPolitique: candidat.partiPolitique,
      slogan: candidat.slogan,
      couleur1: candidat.couleur1,
      couleur2: candidat.couleur2,
      couleur3: candidat.couleur3,
      urlInfo: candidat.urlInfo,
      photo: candidat.photo
    };
  
    return this.http.post<CandidatResponse>(`${this.apiUrl}/candidats`, candidatData);
  
}
  

  /**
   * Mettre à jour les informations additionnelles du candidat
   */
  updateCandidat(numElecteur: string, candidatData: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/candidats/${numElecteur}`, candidatData)
      .pipe(
        tap(response => console.log('Candidat mis à jour avec succès:', response)),
        catchError(this.handleError)
      );
  }

  /**
   * Upload de la photo du candidat
   */
  uploadPhoto(numElecteur: string, photo: File): Observable<any> {
    const formData = new FormData();
    formData.append('photo', photo);
    
    return this.http.post<any>(`${this.apiUrl}/candidats/${numElecteur}/photo`, formData)
      .pipe(
        tap(response => console.log('Photo uploadée avec succès:', response)),
        catchError(this.handleError)
      );
  }

  /**
   * Génère un nouveau code de sécurité pour un candidat
   */
  genererCodeSecurite(numElecteur: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/candidats/${numElecteur}/generer_mdp`, {})
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Récupère la liste de tous les candidats
   */
  getAllCandidats(): Observable<CandidatResponse[]> {
    return this.http.get<CandidatResponse[]>(`${this.apiUrl}/candidats`)
      .pipe(
        retry(2), // Réessayer 2 fois avant d'abandonner
        catchError((error) => {
          console.error('Erreur lors du chargement des candidats:', error);
          // Retourner un tableau vide en cas d'erreur
          return of([]);
        })
      );
  }

  /**
   * Récupère les détails d'un candidat
   */
  getCandidat(numElecteur: string): Observable<CandidatResponse> {
    return this.http.get<CandidatResponse>(`${this.apiUrl}/candidats/${numElecteur}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Supprime un candidat
   */
  deleteCandidat(numElecteur: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/candidats/${numElecteur}`)
      .pipe(
        tap(response => console.log('Candidat supprimé avec succès:', response)),
        catchError(this.handleError)
      );
  }
}