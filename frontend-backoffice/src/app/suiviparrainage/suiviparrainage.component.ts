import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { map, catchError } from 'rxjs/operators';
import { of, interval, Subscription } from 'rxjs';
import {  Color, ScaleType  } from '@swimlane/ngx-charts';

interface Parrainage {
  id: number;
  numElecteur: string;
  numCandidat: string;
  candidat: string;
  dateParrainage: string;
}

interface CandidatStats {
  candidat: string;
  count: number;
  percentage: number;
}

@Component({
  selector: 'app-suivi-parrainages',
  standalone: true,
  imports: [
    CommonModule, 
    NgxChartsModule,
    MatTableModule,
    MatCardModule,
    MatDividerModule,
    MatProgressBarModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './suiviparrainage.component.html',
  styleUrls: ['./suiviparrainage.component.css']
})
export class SuiviparrainageComponent implements OnInit {
  // API URL
  private apiUrl = 'https://gestion-parrainages.onrender.com/api/v1';
  
  // Données
  parrainages: Parrainage[] = [];
  candidats: any[] = [];
  stats: { [key: string]: number } = {};
  chartData: any[] = [];
  
  // Statistiques globales
  totalParrainages = 0;
  objectifParrainages = 500; // Objectif fictif, à ajuster selon vos besoins
  
  // Pour le tableau
  displayedColumns: string[] = ['candidat', 'count', 'percentage', 'progress'];
  dataSource: CandidatStats[] = [];
  
  // Pour le rafraîchissement automatique
  refreshInterval: Subscription | null = null;
  autoRefresh = false;
  
  // Pour la vue détaillée
  selectedCandidat: string | null = null;
  parrainagesParCandidat: Parrainage[] = [];
  
  // Pour les couleurs du graphique
  colorScheme: Color = {
    domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA', '#5AABFF', '#FFA75A', '#FF5A5A', '#5AFF5A'],
    name: 'Custom Color Scheme',
    selectable: true,
    group: ScaleType.Ordinal
  };

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadCandidats();
    this.loadParrainages();
  }

  loadCandidats(): void {
    this.http.get<any[]>(`${this.apiUrl}/candidats`)
      .pipe(
        catchError(error => {
          console.error('Erreur lors du chargement des candidats:', error);
          return of([]);
        })
      )
      .subscribe(data => {
        this.candidats = data;
      });
  }

  loadParrainages(): void {
    this.http.get<Parrainage[]>(`${this.apiUrl}/parrainages`)
      .pipe(
        catchError(error => {
          console.error('Erreur lors du chargement des parrainages:', error);
          return of([]);
        })
      )
      .subscribe(data => {
        this.parrainages = data;
        this.calculateStats();
      });
  }

  calculateStats(): void {
    // Réinitialiser les statistiques
    this.stats = {};
    this.totalParrainages = 0;
    
    // Calculer le nombre de parrainages par candidat
    this.parrainages.forEach(p => {
      // Si le candidat n'est pas défini, utiliser le numCandidat
      const candidatKey = p.candidat || p.numCandidat;
      this.stats[candidatKey] = (this.stats[candidatKey] || 0) + 1;
      this.totalParrainages++;
    });
    
    // Préparer les données pour le graphique
    this.chartData = Object.keys(this.stats).map(candidat => ({
      name: candidat,
      value: this.stats[candidat]
    }));
    
    // Préparer les données pour le tableau avec pourcentages
    this.dataSource = Object.keys(this.stats).map(candidat => ({
      candidat: candidat,
      count: this.stats[candidat],
      percentage: Math.round((this.stats[candidat] / this.totalParrainages) * 100),
      progress: (this.stats[candidat] / this.objectifParrainages) * 100
    }));
    
    // Trier par nombre de parrainages décroissant
    this.dataSource.sort((a, b) => b.count - a.count);
  }

  toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;
    
    if (this.autoRefresh) {
      this.refreshInterval = interval(30000).subscribe(() => {
        this.loadParrainages();
      });
    } else if (this.refreshInterval) {
      this.refreshInterval.unsubscribe();
      this.refreshInterval = null;
    }
  }

  refreshData(): void {
    this.loadParrainages();
  }

  viewCandidatDetails(candidat: string): void {
    this.selectedCandidat = candidat;
    this.parrainagesParCandidat = this.parrainages.filter(p => 
      (p.candidat === candidat) || (p.numCandidat === candidat)
    );
  }

  closeDetails(): void {
    this.selectedCandidat = null;
  }

  ngOnDestroy(): void {
    if (this.refreshInterval) {
      this.refreshInterval.unsubscribe();
    }
  }
}