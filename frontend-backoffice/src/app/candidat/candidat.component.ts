import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CandidatService, Candidat } from '../services/candidat.service';

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
  messageSucces = '';
  formCandidat = false;
  etapeCreation = 'verification'; // 'verification', 'creation', 'confirmation'
  codeSecurite = '';

  // Informations du candidat
  nom = '';
  prenom = '';
  dateNaissance = '';
  email = '';
  telephone = '';
  partiPolitique = '';          // Renommé pour correspondre à l'API
  profession = '';
  slogan = '';
  couleur1 = '#ffffff';
  couleur2 = '#ffffff';
  couleur3 = '#ffffff';
  urlInfo = '';
  photo = '';

  constructor(private candidatService: CandidatService) {}

  /**
   * Vérifie si un électeur existe.
   */
  verifierCandidat() {
    this.messageErreur = '';
    this.messageSucces = '';
    
    if (!this.carteElecteur) {
      this.messageErreur = 'Veuillez entrer un numéro de carte d\'électeur.';
      return;
    }

    this.candidatService.verifierCandidat(this.carteElecteur).subscribe({
      next: (response) => {
        this.formCandidat = true;
        this.etapeCreation = 'creation';
        this.nom = response.nom || '';
        this.prenom = response.prenom || '';
        this.dateNaissance = response.dateNaissance || '';
      },
      error: (error) => {
        console.error('Erreur lors de la vérification:', error);
        if (error.status === 404) {
          this.messageErreur = 'Aucun électeur trouvé avec ce numéro.';
        } else if (error.status === 409) {
          this.messageErreur = 'Un candidat existe déjà avec ce numéro d\'électeur.';
        } else {
          this.messageErreur = 'Une erreur est survenue. Veuillez réessayer.';
        }
        this.formCandidat = false;
      },
    });
  }

  /**
   * Enregistre un nouveau candidat.
   */
  enregistrerCandidat() {
    this.messageErreur = '';
    
    // Validation basique
    if (!this.email || !this.telephone) {
      this.messageErreur = 'Veuillez remplir tous les champs obligatoires.';
      return;
    }

    const candidat: Candidat = {
      numElecteur: this.carteElecteur,
      email: this.email,
      telephone: this.telephone,
      partiPolitique: this.partiPolitique,
      
    };

    this.candidatService.enregistrerCandidat(candidat).subscribe({
      next: (response) => {
        console.log('Candidat enregistré:', response);
        this.codeSecurite = response.codeSecurite;
        this.etapeCreation = 'confirmation';
        this.messageSucces = 'Candidat enregistré avec succès !';
        
        // Mise à jour des informations additionnelles si nécessaire
        if (this.slogan || this.couleur1 !== '#ffffff' || this.urlInfo) {
          const updateData = {
            email: this.email,
            telephone: this.telephone,
            parti: this.partiPolitique,
            profession: this.profession,
            // Données additionnelles non mentionnées dans l'API mais possiblement supportées
            slogan: this.slogan,
            couleur1: this.couleur1,
            couleur2: this.couleur2,
            couleur3: this.couleur3,
            urlInfo: this.urlInfo
          };
          
          this.candidatService.updateCandidat(this.carteElecteur, updateData).subscribe({
            next: (updateResponse) => {
              console.log('Candidat mis à jour:', updateResponse);
            },
            error: (updateError) => {
              console.error('Erreur lors de la mise à jour:', updateError);
              // On ne bloque pas le processus si cette mise à jour échoue
            }
          });
        }
        
        // Upload de la photo si présente
        
      },
      error: (error) => {
        console.error('Erreur lors de l\'enregistrement:', error);
        if (error.status === 400) {
          this.messageErreur = 'Données invalides. Veuillez vérifier les informations saisies.';
        } else if (error.status === 409) {
          this.messageErreur = 'Un candidat existe déjà avec ce numéro d\'électeur.';
        } else {
          this.messageErreur = 'Erreur lors de l\'enregistrement du candidat.';
        }
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
    this.profession = '';
    this.slogan = '';
    this.couleur1 = '#ffffff';
    this.couleur2 = '#ffffff';
    this.couleur3 = '#ffffff';
    this.urlInfo = '';
    this.photo = '';
    this.formCandidat = false;
    this.etapeCreation = 'verification';
    this.messageErreur = '';
    this.messageSucces = '';
  }

}