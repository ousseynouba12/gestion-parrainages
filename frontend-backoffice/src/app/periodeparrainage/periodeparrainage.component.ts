import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-periodeparrainage',
  imports : [FormsModule,CommonModule],
  templateUrl: './periodeparrainage.component.html',
  styleUrls: ['./periodeparrainage.component.css']
})
export class PeriodeparrainageComponent implements OnInit {
  startDate: string = '';
  endDate: string = '';
  startError: string = '';
  endError: string = '';
  isValid: boolean = false;
  successMessage: string = '';
  periodes: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.getPeriodes();
  }

  getPeriodes() {
    this.http.get<any[]>('https://gestion-parrainages.onrender.com/api/v1/periodes/')
      .subscribe(
        (data) => {
          this.periodes = data;
          console.log('Périodes récupérées :', data);
        },
        (error) => {
          console.error('Erreur lors de la récupération des périodes', error);
        }
      );
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

    if (!this.startError && !this.endError) {
      this.isValid = true;
    }
  }

  saveDates() {
    this.successMessage = "Dates enregistrées avec succès.";
  }
}
