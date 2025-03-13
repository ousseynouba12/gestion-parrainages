import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';


export interface UploadStatus {
  upload_autorise: boolean;
}

export interface UploadResponse {
  message: string;
  tentative_id: number;
  success: boolean;
}

export interface ControlResponse {
  success: boolean;
  message: string;
  statistiques: {
    nbElecteursTotal: number;
    nbElecteursValides: number;
    nbElecteursInvalides: number;
    typesErreurs: {
      [key: string]: number;
    };
  };
  peut_valider: boolean;
}

export interface ValidationResponse {
  success: boolean;
  message: string;
  nb_electeurs_importes: number;
}

export interface ElecteurProblematique {
  numElecteur: string;
  nom: string;
  prenom: string;
  erreurs: string[];
}

export interface ElecteursProblematiquesResponse {
  electeurs: ElecteurProblematique[];
  count: number;
}

@Injectable({
  providedIn: 'root'
})
export class FileUploadService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1/electoral'; // À ajuster selon votre configuration

  constructor(private http: HttpClient, private authService: AuthService) {}

  /**
   * Vérifie si un upload de fichier électoral est autorisé
   */
  checkUploadStatus(): Observable<UploadStatus> {
    return this.http.get<UploadStatus>(`${this.apiUrl}/statut-upload`, {
      headers: this.getAuthHeaders()
    });
  }

  /**
   * Upload du fichier électoral
   * @param file Fichier à uploader
   * @param checksum Empreinte SHA256 du fichier
   */
  uploadElectoralFile(file: File, checksum: string): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('checksum', checksum);

    return this.http.post<UploadResponse>(`${this.apiUrl}/upload-fichier-electoral`, formData, {
      headers: this.getAuthHeaders(false) // Sans Content-Type pour FormData
    });
  }

  /**
   * Contrôle des électeurs après upload
   * @param tentativeId ID de la tentative d'importation
   */
  controlerElecteurs(tentativeId: number): Observable<ControlResponse> {
    return this.http.post<ControlResponse>(`${this.apiUrl}/controler-electeurs/${tentativeId}`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  /**
   * Validation finale de l'importation
   * @param tentativeId ID de la tentative d'importation
   */
  validerImportation(tentativeId: number): Observable<ValidationResponse> {
    return this.http.post<ValidationResponse>(`${this.apiUrl}/valider-importation/${tentativeId}`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  /**
   * Récupère les statistiques d'une tentative d'importation
   * @param tentativeId ID de la tentative d'importation
   */
  getStatistiquesImportation(tentativeId: number): Observable<ControlResponse> {
    return this.http.get<ControlResponse>(`${this.apiUrl}/statistiques-importation/${tentativeId}`, {
      headers: this.getAuthHeaders()
    });
  }

  /**
   * Récupère la liste des électeurs problématiques
   * @param tentativeId ID de la tentative d'importation
   * @param typeErreur Filtre optionnel par type d'erreur
   */
  getElecteursProblematiques(tentativeId: number, typeErreur?: string): Observable<ElecteursProblematiquesResponse> {
    let url = `${this.apiUrl}/electeurs-problematiques/${tentativeId}`;
    if (typeErreur) {
      url += `?type_erreur=${typeErreur}`;
    }

    return this.http.get<ElecteursProblematiquesResponse>(url, {
      headers: this.getAuthHeaders()
    });
  }

  /**
   * Réinitialise l'état d'upload (admin uniquement)
   */
  reinitialiserEtatUpload(): Observable<{ success: boolean; message: string }> {
    return this.http.post<{ success: boolean; message: string }>(`${this.apiUrl}/reinitialiser-etat-upload`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  /**
   * Récupère les en-têtes d'authentification avec le token JWT
   * @param includeContentType Indique si l'en-tête Content-Type doit être inclus
   */
  private getAuthHeaders(includeContentType: boolean = true): HttpHeaders {
    let headers = new HttpHeaders();
    const token = this.authService.login;
    
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    
    if (includeContentType) {
      headers = headers.set('Content-Type', 'application/json');
    }
    
    return headers;
  }
 
}