import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root', // Le service est disponible dans toute l'application
})
export class FileUploadService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1'; // Remplacez par l'URL de votre API

  constructor(private http: HttpClient) {}

  /**
   * Vérifie si l'upload est autorisé.
   * @returns Observable avec la réponse de l'API (true/false).
   */
  checkUploadStatus(): Observable<any> {
    // Ajoutez le token JWT dans les en-têtes de la requête
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    });

    return this.http.get(`${this.apiUrl}/electoral/statut-upload`, { headers });
  }

  /**
   * Upload un fichier électoral avec son empreinte SHA256.
   * @param file Le fichier CSV à uploader.
   * @param checksum L'empreinte SHA256 du fichier.
   * @returns Observable avec la réponse de l'API.
   */
  uploadElectoralFile(file: File, checksum: string): Observable<any> {
    // Créez un objet FormData pour envoyer le fichier et le checksum
    const formData = new FormData();
    formData.append('file', file); // Ajoutez le fichier
    formData.append('checksum', checksum); // Ajoutez le checksum

    // Ajoutez le token JWT dans les en-têtes de la requête
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    });

    // Envoyez la requête POST à l'API
    return this.http.post(`${this.apiUrl}/electoral/upload-fichier-electoral`, formData, { headers });
  }
}