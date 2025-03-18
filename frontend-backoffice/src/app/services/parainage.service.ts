import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

export interface Parrainage {
  id: number;
  numElecteur: string;
  numCandidat: string;
  candidat: string;
  dateParrainage: string;
}

export interface Candidat {
  numElecteur: string;
  nom: string;
  prenom: string;
  parti: string;
  email: string;
  telephone: string;
}

export interface ParrainageStat {
  candidat: string;
  count: number;
  percentage: number;
  progress: number;
}

@Injectable({
  providedIn: 'root'
})
export class ParrainagesService {
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1';

  constructor(private http: HttpClient) {}

  // Récupération de tous les parrainages
  getParrainages(): Observable<Parrainage[]> {
    return this.http.get<Parrainage[]>(`${this.apiUrl}/parrain/`).pipe(
      tap(_ => console.log('Parrainages récupérés')),
      catchError(this.handleError<Parrainage[]>('getParrainages', []))
    );
  }

  // Récupération de tous les candidats
  getCandidats(): Observable<Candidat[]> {
    return this.http.get<Candidat[]>(`${this.apiUrl}/candidats/`).pipe(
      tap(_ => console.log('Candidats récupérés')),
      catchError(this.handleError<Candidat[]>('getCandidats', []))
    );
  }

  // Récupération des parrainages d'un candidat spécifique
  getParrainagesByCandidat(numCandidat: string): Observable<Parrainage[]> {
    return this.getParrainages().pipe(
      map(parrainages => parrainages.filter(p => 
        p.numCandidat === numCandidat || p.candidat === numCandidat
      ))
    );
  }

  // Récupération du nombre de parrainages pour un candidat
  getNombreParrainagesCandidat(numCandidat: string): Observable<number> {
    return this.http.get<{numCandidat: string, nbrParrainages: number}>(
      `${this.apiUrl}/parrainages/candidat/${numCandidat}`
    ).pipe(
      map(response => response.nbrParrainages),
      catchError(error => {
        console.error(`Erreur lors de la récupération des parrainages du candidat ${numCandidat}:`, error);
        // Fallback: compter manuellement si l'API échoue
        return this.getParrainagesByCandidat(numCandidat).pipe(
          map(parrainages => parrainages.length)
        );
      })
    );
  }

  // Calcul des statistiques pour tous les candidats
  calculateParrainageStats(objectif: number = 500): Observable<ParrainageStat[]> {
    return this.getParrainages().pipe(
      map(parrainages => {
        // Calculer le nombre total de parrainages
        const totalParrainages = parrainages.length;
        
        // Compter les parrainages par candidat
        const countByCandidats: {[key: string]: number} = {};
        parrainages.forEach(p => {
          const candidatKey = p.candidat || p.numCandidat;
          countByCandidats[candidatKey] = (countByCandidats[candidatKey] || 0) + 1;
        });
        
        // Transformer en tableau de statistiques
        const stats: ParrainageStat[] = Object.keys(countByCandidats).map(candidat => ({
          candidat,
          count: countByCandidats[candidat],
          percentage: Math.round((countByCandidats[candidat] / totalParrainages) * 100),
          progress: (countByCandidats[candidat] / objectif) * 100
        }));
        
        // Trier par nombre de parrainages décroissant
        return stats.sort((a, b) => b.count - a.count);
      })
    );
  }

  // Gestion des erreurs
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} a échoué: ${error.message}`);
      return of(result as T);
    };
  }
}