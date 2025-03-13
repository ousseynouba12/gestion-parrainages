import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CandidatService, Candidat, CandidatResponse } from '../services/candidat.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-listecandidat',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './listecandidat.component.html',
  styleUrl: './listecandidat.component.css'
})

export class ListecandidatComponent implements OnInit {
  candidats: CandidatResponse[] = [];
  selectedCandidat: CandidatResponse | null = null;
  isEditing: boolean = false;
  editForm: FormGroup;
  loading: boolean = false;
  error: string = '';
  success: string = '';

  constructor(
    private candidatService: CandidatService,
    private fb: FormBuilder
  ) {
    this.editForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      telephone: ['', Validators.required],
      parti: [''],
      profession: ['']
    });
  }

  ngOnInit(): void {
    this.loadCandidats();
  }

  loadCandidats(): void {
    this.loading = true;
    this.candidatService.getAllCandidats().subscribe({
      next: (data) => {
        this.candidats = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des candidats:', err);
        this.error = 'Erreur lors du chargement des candidats';
        this.loading = false;
      }
    });
  }

  showDetails(numElecteur: string): void {
    this.loading = true;
    this.candidatService.getCandidat(numElecteur).subscribe({
      next: (candidat) => {
        this.selectedCandidat = candidat;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des détails du candidat:', err);
        this.error = 'Erreur lors du chargement des détails du candidat';
        this.loading = false;
      }
    });
  }

  closeDetails(): void {
    this.selectedCandidat = null;
    this.isEditing = false;
    this.error = '';
    this.success = '';
  }

  startEditing(): void {
    if (this.selectedCandidat) {
      this.editForm.patchValue({
        email: this.selectedCandidat.email,
        telephone: this.selectedCandidat.telephone,
        parti: this.selectedCandidat.partiPolitique,
       
      });
      this.isEditing = true;
    }
  }

  cancelEditing(): void {
    this.isEditing = false;
    this.error = '';
  } 

  saveCandidat(): void {
    if (this.editForm.valid && this.selectedCandidat) {
      this.loading = true;
      const updatedData = this.editForm.value;
      
      this.candidatService.updateCandidat(this.selectedCandidat.numElecteur, updatedData).subscribe({
        next: (response) => {
          this.selectedCandidat = {
            ...this.selectedCandidat!,
            ...updatedData
          };
          this.isEditing = false;
          this.success = 'Candidat mis à jour avec succès';
          this.loading = false;
          this.loadCandidats(); // Rafraîchir la liste
        },
        error: (err) => {
          console.error('Erreur lors de la mise à jour du candidat:', err);
          this.error = 'Erreur lors de la mise à jour du candidat';
          this.loading = false;
        }
      });
    }
  }

  deleteCandidat(numElecteur: string): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce candidat ?')) {
      this.loading = true;
      this.candidatService.deleteCandidat(numElecteur).subscribe({
        next: () => {
          this.success = 'Candidat supprimé avec succès';
          this.loadCandidats(); // Rafraîchir la liste
          this.closeDetails(); // Fermer les détails
          this.loading = false;
        },
        error: (err) => {
          console.error('Erreur lors de la suppression du candidat:', err);
          this.error = 'Erreur lors de la suppression du candidat';
          this.loading = false;
        }
      });
    }
  }

  genererNouveauCode(numElecteur: string): void {
    this.loading = true;
    this.candidatService.genererCodeSecurite(numElecteur).subscribe({
      next: (response) => {
        // Mettre à jour le candidat sélectionné avec le nouveau code
        if (this.selectedCandidat) {
          this.selectedCandidat.codeSecurite = response.codeSecurite;
        }
        this.success = 'Nouveau code de sécurité généré avec succès';
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors de la génération du nouveau code:', err);
        this.error = 'Erreur lors de la génération du nouveau code';
        this.loading = false;
      }
    });
  }
}