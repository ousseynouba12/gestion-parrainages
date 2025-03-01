import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';


@Component({
  selector: 'app-candidat',
  templateUrl: './candidat.component.html',
  styleUrls: ['./candidat.component.css'],
  imports : [ReactiveFormsModule,MatIcon,MatTableModule,CommonModule,MatFormFieldModule,MatInputModule,MatSelectModule,MatButtonModule],
})
export class CandidatComponent {

  showForm = false;
  candidatForm: FormGroup;

  candidats = [
    { numElecteur: '123', nom: 'Diop', prenom: 'Awa', partiPolitique: 'Parti A', email: 'awa@example.com', telephone: '778888888', slogan: 'Pour un avenir meilleur' },
    { numElecteur: '456', nom: 'Sow', prenom: 'Moussa', partiPolitique: 'Parti B', email: 'moussa@example.com', telephone: '779999999', slogan: 'Ensemble pour demain' },
  ];

  constructor(private fb: FormBuilder) {
    this.candidatForm = this.fb.group({
      numElecteur: [''],
      nom: ['', Validators.required],
      prenom: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      telephone: ['', Validators.required],
      partiPolitique: ['', Validators.required],
      slogan: ['']
    });
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.candidatForm.reset();
    }
  }

  enregistrer() {
    if (this.candidatForm.valid) {
      const candidat = this.candidatForm.value;
      if (candidat.numElecteur) {
        // Modification
        const index = this.candidats.findIndex(c => c.numElecteur === candidat.numElecteur);
        if (index !== -1) {
          this.candidats[index] = candidat;
        }
      } else {
        // Ajout (générer un numElecteur fictif pour l’exemple)
        candidat.numElecteur = Date.now().toString();
        this.candidats.push(candidat);
      }
      this.toggleForm();
    }
  }

  modifierCandidat(candidat: any) {
    this.candidatForm.patchValue(candidat);
    this.showForm = true;
  }

  supprimerCandidat(numElecteur: string) {
    this.candidats = this.candidats.filter(c => c.numElecteur !== numElecteur);
  }
}