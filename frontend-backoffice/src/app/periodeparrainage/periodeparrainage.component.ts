import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-periodeparrainage',
  imports: [CommonModule,FormsModule],
  templateUrl: './periodeparrainage.component.html',
  styleUrl: './periodeparrainage.component.css'
})
export class PeriodeparrainageComponent {
  startDate: string = '';
  endDate: string = '';
  startError: string = '';
  endError: string = '';
  isValid: boolean = false;
  successMessage: string = '';

  validateDates() {
    const today = new Date();
    const minStartDate = new Date();
    minStartDate.setMonth(today.getMonth() + 6); // 6 mois après aujourd'hui

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
