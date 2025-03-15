import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1';
  private tokenKey = 'auth_token';
  private isBrowser: boolean;
  private isAuthenticatedSubject: BehaviorSubject<boolean>;
  
  constructor(
    private http: HttpClient, 
    private router: Router,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
    this.isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  }
  
  login(email: string, password: string): Observable<any> {
    const formData = new URLSearchParams();
    formData.set('username', email);
    formData.set('password', password);
    
    return this.http.post<any>(`${this.apiUrl}/auth/token`, formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).pipe(
      tap(response => {
        if (this.isBrowser) {
          localStorage.setItem(this.tokenKey, response.access_token);
        }
        this.isAuthenticatedSubject.next(true);
      })
    );
  }
  
  logout(): void {
    if (this.isBrowser) {
      localStorage.removeItem(this.tokenKey);
    }
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/login']);
  }
  
  getToken(): string | null {
    if (this.isBrowser) {
      return localStorage.getItem(this.tokenKey);
    }
    return null;
  }
  
  isAuthenticated(): Observable<boolean> {
    return this.isAuthenticatedSubject.asObservable();
  }
  
  hasToken(): boolean {
    return !!this.getToken();
  }
  
  refreshToken(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/token/refresh`, {});
  }
}