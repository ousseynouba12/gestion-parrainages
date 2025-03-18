import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ElectoralFileService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1/electoral';

  constructor(private http: HttpClient) {}

  // Vérifier si un upload est autorisé
  checkUploadStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/statut-upload`);
  }

  // Upload du fichier électoral
  uploadElectoralFile(file: File, checksum: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('checksum', checksum);

    return this.http.post(`${this.apiUrl}/upload-fichier-electoral`, formData);
  }

  // Contrôler les électeurs
  controlElectors(tentativeId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/controler-electeurs/${tentativeId}`, {});
  }

  // Valider l'importation
  validateImport(tentativeId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/valider-importation/${tentativeId}`, {});
  }

  // Obtenir les statistiques d'importation
  getImportStatistics(tentativeId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/statistiques-importation/${tentativeId}`);
  }

  // Obtenir les électeurs problématiques
  getProblematicElectors(tentativeId: number, errorType?: string): Observable<any> {
    const url = errorType 
      ? `${this.apiUrl}/electeurs-problematiques/${tentativeId}?type_erreur=${errorType}`
      : `${this.apiUrl}/electeurs-problematiques/${tentativeId}`;
    return this.http.get(url);
  }

  // Réinitialiser l'état d'upload (admin uniquement)
  resetUploadState(): Observable<any> {
    return this.http.post(`${this.apiUrl}/reinitialiser-etat-upload`, {});
  }
}