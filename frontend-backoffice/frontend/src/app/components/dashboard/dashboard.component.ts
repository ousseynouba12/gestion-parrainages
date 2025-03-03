import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../../services/dashboard.service';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule,MatTableModule,MatCardModule, MatIconModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  candidats: any[] = [];
  totalParrainages: number = 0;
  periode: any = { dateDebut: '', dateFin: '' };
  totalElecteurs: number = 0;

  private dashboardService = inject(DashboardService);

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData() {
    this.dashboardService.getCandidats().subscribe({
      next: (data) => this.candidats = data,
      error: (err) => console.error('Erreur chargement candidats', err)
    });

    this.dashboardService.getStatistiques().subscribe({
      next: (stats) => this.totalParrainages = stats.totalParrainages,
      error: (err) => console.error('Erreur chargement nb parrainages', err)
    });

    this.dashboardService.getStatistiques().subscribe({
      next: (stats) => this.totalElecteurs = stats.totalElecteurs,
      error: (err) => console.error('Erreur chargement nb electeurs', err)
    });

    this.dashboardService.getPeriode().subscribe({
      next: (periode) => this.periode = periode,
      error: (err) => console.error('Erreur chargement période', err)
    });

    // this.dashboardService.getElecteurs().subscribe({
    //   next: (etat) => this.Electeur = etat,
    //   error: (err) => console.error('Erreur chargement état upload', err)
    // });
  }
}
