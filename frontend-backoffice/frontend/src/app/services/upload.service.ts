import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private apiUrl = 'http://localhost:5000/api/upload';  // L'URL de votre API

  constructor(private http: HttpClient) {}

  uploadFile(file: File, checksum: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('checksum', checksum);

    return this.http.post(this.apiUrl, formData);
  }
}
