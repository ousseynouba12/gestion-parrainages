import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-periodeparrainage',
  imports: [FormsModule, CommonModule],
  templateUrl: './periodeparrainage.component.html',
  styleUrls: ['./periodeparrainage.component.css'],
  standalone: true
})
export class PeriodeparrainageComponent implements OnInit {
  startDate: string = '';
  endDate: string = '';
  startError: string = '';
  endError: string = '';
  isValid: boolean = false;
  successMessage: string = '';
  errorMessage: string = '';
  periodes: any[] = [];
  loading: boolean = false;
  deleting: boolean = false;
  apiUrl: string = 'https://gestion-parrainages.onrender.com/api/v1/periodes/periodes-parrainage/';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.getPeriodes();
  }

  getPeriodes() {
    this.loading = true;
    this.http.get<any[]>(this.apiUrl)
      .subscribe({
        next: (data) => {
          this.periodes = data;
          this.loading = false;
          console.log('Périodes récupérées :', data);
        },
        error: (error) => {
          console.error('Erreur lors de la récupération des périodes', error);
          
          
            
            // Données simulées pour le développement
            this.periodes = [
              {periodes_id: 1, date_debut: '2025-10-01', date_fin: '2025-12-31' },
              { periodes_id: 2, date_debut: '2026-01-01', date_fin: '2026-03-31' }
            ];
            console.log('Utilisation de données simulées pour le développement');
      }})
  }

  validateDates() {
    const today = new Date();
    const minStartDate = new Date();
    minStartDate.setMonth(today.getMonth() + 6);

    const start = new Date(this.startDate);
    const end = new Date(this.endDate);

    this.startError = '';
    this.endError = '';
    this.isValid = false;

    if (!this.startDate) {
      this.startError = "Veuillez entrer une date de début.";
    } else if (start < minStartDate) {
      this.startError = "La date de début doit être au moins 6 mois après aujourd'hui.";
    }

    if (!this.endDate) {
      this.endError = "Veuillez entrer une date de fin.";
    } else if (start >= end) {
      this.endError = "La date de fin doit être postérieure à la date de début.";
    }

    // Vérifier si la période chevauche des périodes existantes
    for (const periode of this.periodes) {
      const periodeStart = new Date(periode.date_debut);
      const periodeEnd = new Date(periode.date_fin);
      
      if ((start <= periodeEnd && end >= periodeStart)) {
        this.startError = "Cette période chevauche une période existante.";
        break;
      }
    }

    if (!this.startError && !this.endError) {
      this.isValid = true;
    }
  }

  saveDates() {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';
    
    const payload = {
      date_debut: this.startDate,
      date_fin: this.endDate
    };

    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    this.http.post(this.apiUrl, payload, { headers })
      .subscribe({
        next: (response) => {
          console.log('Période enregistrée:', response);
          this.successMessage = "Période de parrainage enregistrée avec succès.";
          this.startDate = '';
          this.endDate = '';
          this.isValid = false;
          this.getPeriodes();
          this.loading = false;
        },
        error: (error) => {
          console.error('Erreur lors de l\'enregistrement:', error);
          this.errorMessage = `Erreur lors de l'enregistrement: ${error.status} ${error.statusText}. Vérifiez la documentation de l'API.`;
          this.loading = false;
        }
      });
  }

  deletePeriode(periodes_id: number) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette période ?')) {
      this.deleting = true;
      this.http.delete(`${this.apiUrl}/${periodes_id}`)
        .subscribe({
          next: () => {
            console.log('Période supprimée avec succès');
            this.successMessage = "Période supprimée avec succès.";
            this.getPeriodes();
            this.deleting = false;
          },
          error: (error) => {
            console.error('Erreur lors de la suppression:', error);
            this.errorMessage = `Erreur lors de la suppression: ${error.status} ${error.statusText}. Vérifiez la documentation de l'API.`;
            this.deleting = false;
          }
        });
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
  }
}