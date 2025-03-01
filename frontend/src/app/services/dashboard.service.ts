import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class DashboardService {

  constructor(private http: HttpClient) {}

  getCandidats(): Observable<any[]> {
    return this.http.get<any[]>('/api/candidats');
  }

  getStatistiques(): Observable<any> {
    return this.http.get<any>('/api/stat');
  }

  getPeriode(): Observable<any> {
    return this.http.get<any>('/api/periode');
  }

  getEtatUpload(): Observable<string> {
    return this.http.get<string>('/api/upload/etat');
  }
}
