import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ControlResponse {
  success: boolean;
  message?: string;
  statistiques: {
    nbElecteursTotal: number;
    nbElecteursValides: number;
    nbElecteursInvalides: number;
    typesErreurs: { [key: string]: number };
  };
  peut_valider: boolean;
}

export interface ElecteurProblematique {
  numElecteur: string;
  nom: string;
  prenom: string;
  erreurs: string[];
}

@Injectable({
  providedIn: 'root'
})
export class FileUploadService {
  private apiUrl = 'https://gestion-parrainages.onrender.com';

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  checkUploadStatus(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/statut-upload`, { headers: this.getHeaders() });
  }

  uploadElectoralFile(file: File, checksum: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('checksum', checksum);

    return this.http.post<any>(`${this.apiUrl}/upload-fichier-electoral`, formData, { headers: this.getHeaders() });
  }

  controlerElecteurs(tentativeId: number): Observable<ControlResponse> {
    return this.http.post<ControlResponse>(`${this.apiUrl}/controler-electeurs/${tentativeId}`, {}, { headers: this.getHeaders() });
  }

  getElecteursProblematiques(tentativeId: number, typeErreur: string = ''): Observable<any> {
    let url = `${this.apiUrl}/electeurs-problematiques/${tentativeId}`;
    if (typeErreur) {
      url += `?type_erreur=${typeErreur}`;
    }
    return this.http.get<any>(url, { headers: this.getHeaders() });
  }

  validerImportation(tentativeId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/valider-importation/${tentativeId}`, {}, { headers: this.getHeaders() });
  }

  reinitialiserEtatUpload(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/reinitialiser-etat-upload`, {}, { headers: this.getHeaders() });
  }
}