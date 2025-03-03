import { Component, OnInit } from '@angular/core';
import { PeriodeService } from '../../services/periode.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-periode',
  templateUrl: './periode.component.html',
  styleUrls: ['./periode.component.css'],
  standalone: true,
  imports: [FormsModule]
})
export class PeriodeComponent implements OnInit {
  dateDebut: string = '';
  dateFin: string = '';

  constructor(private periodeService: PeriodeService) {}

  ngOnInit(): void {
    this.getPeriode();
  }

  getPeriode(): void {
    this.periodeService.getPeriode().subscribe(data => {
      this.dateDebut = data.dateDebut;
      this.dateFin = data.dateFin;
    });
  }

  setPeriode(): void {
    this.periodeService.setPeriode({ dateDebut: this.dateDebut, dateFin: this.dateFin }).subscribe(response => {
      alert('Période mise à jour avec succès !');
    });
  }

  fermerPeriode(): void {
    this.periodeService.fermerPeriode().subscribe(response => {
      alert('Période de parrainage fermée.');
    });
  }
}
