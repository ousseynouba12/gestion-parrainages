import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { OnInit } from '@angular/core';
import {NgxChartsModule } from '@swimlane/ngx-charts';




@Component({
  selector: 'app-suiviparrainage',
  imports: [NgxChartsModule],
  templateUrl: './suiviparrainage.component.html',
  styleUrl: './suiviparrainage.component.css'
})
export class SuiviparrainageComponent implements OnInit {
// Installation des dépendances nécessaires
// npm install @angular/material @angular/flex-layout ngx-charts

  
  parrainages: any[] = [];
  stats: any = {};
  chartData: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.getParrainages();
  }

  getParrainages() {
    this.http.get<any>('https://gestion-parrainages.onrender.com/parrainages') // Remplacer par l'URL de l'API
      .subscribe(data => {
        this.parrainages = data;
        this.calculateStats();
      });
  }

  calculateStats() {
    const statsMap = this.parrainages.reduce((acc, p) => {
      acc[p.candidat] = (acc[p.candidat] || 0) + 1;
      return acc;
    }, {});

    this.stats = statsMap;
    this.chartData = Object.keys(statsMap).map(candidat => ({
      name: candidat,
      value: statsMap[candidat]
    }));
  }
}


