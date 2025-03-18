import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CandidatService, Candidat ,Electeur } from '../services/candidat.service';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-candidat',
  standalone: true,
  imports: [CommonModule, FormsModule,ReactiveFormsModule],
  templateUrl: './candidat.component.html',
  styleUrls: ['./candidat.component.css'],
})
export class CandidatComponent {
  numElecteur = '';
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
  photo: string | null = null;

  constructor(private candidatService: CandidatService) {}

  /**
   * Vérifie si un électeur existe.
   */
  verifierCandidat() {
    this.messageErreur = '';
    this.messageSucces = '';
    
    if (!this.numElecteur) {
      this.messageErreur = 'Veuillez entrer un numéro de carte d\'électeur.';
      return;
    }

    this.candidatService.verifierCandidat(this.numElecteur).subscribe({
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
  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.readAsDataURL(file); // Convertit le fichier en base64
      reader.onload = () => {
        this.photo = reader.result as string; // Stocke le résultat en base64
      };
      reader.onerror = (error) => {
        console.error('Erreur lors de la lecture du fichier:', error);
        this.messageErreur = 'Erreur lors de la lecture du fichier.';
      };
    }
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
      numElecteur: this.numElecteur,
      email: this.email,
      telephone: this.telephone,
      partiPolitique: this.partiPolitique,
      slogan: this.slogan,
      couleur1: this.couleur1,
      couleur2: this.couleur2,
      couleur3: this.couleur3,
      urlInfo: this.urlInfo,
      photo: this.photo || '' // Ajoutez la photo en base64 ici
    }; 
    

    this.candidatService.enregistrerCandidat(candidat, this.numElecteur).subscribe({
      next: (response) => {
        console.log('Candidat enregistré:', response);
        this.codeSecurite = response.codeSecurite;
        this.etapeCreation = 'confirmation';
        this.messageSucces = 'Candidat enregistré avec succès !';
      },
      error: (error) => {
        console.error('Erreur lors de l\'enregistrement du candidat:', error);
        this.messageErreur = 'Une erreur est survenue. Veuillez réessayer.';
      }
    });
  
        
        // Mise à jour des informations additionnelles si nécessaire
        if (this.slogan || this.couleur1 !== '#ffffff' || this.urlInfo) {
          const updateData = {
            email: this.email,
            telephone: this.telephone,
            parti: this.partiPolitique,
            // Données additionnelles non mentionnées dans l'API mais possiblement supportées
            slogan: this.slogan,
            couleur1: this.couleur1,
            couleur2: this.couleur2,
            couleur3: this.couleur3,
            urlInfo: this.urlInfo,
            
    };
          
          this.candidatService.updateCandidat(this.numElecteur, updateData).subscribe({
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
        
      }
    
  

  /**
   * Réinitialise le formulaire.
   */
  resetForm() {
    this.numElecteur = '';
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

  /**
   * Gère l'upload de la photo.
   */
  }