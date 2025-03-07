import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CandidatService } from '../services/candidat.service';

@Component({
  selector: 'app-candidat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './candidat.component.html',
  styleUrls: ['./candidat.component.css'],
})
export class CandidatComponent {
  carteElecteur = '';
  messageErreur = '';
  formCandidat = false;

  // Informations du candidat
  nom = '';
  prenom = '';
  dateNaissance = '';
  email = '';
  telephone = '';
  partiPolitique = '';
  slogan = '';
  couleur1 = '';
  couleur2 = '';
  couleur3 = '';
  urlInfo = '';
  photo: File | null = null;

  constructor(private candidatService: CandidatService) {}

  /**
   * Vérifie si un candidat existe déjà.
   */
  verifierCandidat() {
    if (!this.carteElecteur) {
      this.messageErreur = 'Veuillez entrer un numéro de carte d\'électeur.';
      return;
    }

    this.candidatService.verifierCandidat(this.carteElecteur).subscribe({
      next: (response) => {
        this.formCandidat = true;
        this.nom = response.nom;
        this.prenom = response.prenom;
        this.dateNaissance = response.dateNaissance;
        this.messageErreur = '';
      },
      error: (error) => {
        this.messageErreur = 'Aucun candidat trouvé avec ce numéro.';
        this.formCandidat = false;
      },
    });
  }

  /**
   * Enregistre un nouveau candidat.
   */
  enregistrerCandidat() {
    const candidat = {
      numElecteur: this.carteElecteur,
      nom: this.nom,
      prenom: this.prenom,
      dateNaissance: this.dateNaissance,
      email: this.email,
      telephone: this.telephone,
      partiPolitique: this.partiPolitique,
      slogan: this.slogan,
      couleurs: [this.couleur1, this.couleur2, this.couleur3],
      urlInfo: this.urlInfo,
      photo: this.photo,
    };

    this.candidatService.enregistrerCandidat(candidat).subscribe({
      next: (response) => {
        alert('Candidat enregistré avec succès !');
        this.resetForm();
      },
      error: (error) => {
        this.messageErreur = 'Erreur lors de l\'enregistrement du candidat.';
      },
    });
  }

  /**
   * Réinitialise le formulaire.
   */
  resetForm() {
    this.carteElecteur = '';
    this.nom = '';
    this.prenom = '';
    this.dateNaissance = '';
    this.email = '';
    this.telephone = '';
    this.partiPolitique = '';
    this.slogan = '';
    this.couleur1 = '';
    this.couleur2 = '';
    this.couleur3 = '';
    this.urlInfo = '';
    this.photo = null;
    this.formCandidat = false;
  }

  /**
   * Gère l'upload de la photo.
   */
  onFileChange(event: any) {
    if (event.target.files.length > 0) {
      this.photo = event.target.files[0];
    }
  }
}