import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { FileUploadService, ControlResponse, ElecteurProblematique } from '../services/file-upload.service';

@Component({
  selector: 'app-fichierelectoral',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './fichierelectoral.component.html',
  styleUrls: ['./fichierelectoral.component.css'],
})
export class FichierelectoralComponent implements OnInit {
  uploadForm: FormGroup;
  message: string = '';
  messageClass: string = '';
  
  // États du processus d'importation
  isUploading: boolean = false;
  isUploadComplete: boolean = false;
  isProcessing: boolean = false;
  isValidating: boolean = false;
  
  // Données de la tentative d'importation
  tentativeId: number | null = null;
  statistiques: ControlResponse | null = null;
  peutValider: boolean = false;
  
  // Liste des électeurs problématiques
  electeursProblematiques: ElecteurProblematique[] = [];
  
  // Options de filtrage
  typesErreurs: string[] = [];
  filtreTypeErreur: string = '';

  constructor(
    private fb: FormBuilder, 
    private fileUploadService: FileUploadService
  ) {
    this.uploadForm = this.fb.group({
      checksum: ['', [Validators.required, Validators.minLength(64), Validators.maxLength(64)]],
      file: [null, Validators.required],
    });
  }

  ngOnInit(): void {
    this.checkUploadStatus();
  }

  /**
   * Vérifie si un upload est autorisé
   */
  checkUploadStatus(): void {
    this.fileUploadService.checkUploadStatus().subscribe({
      next: (response) => {
        if (!response.upload_autorise) {
          this.message = 'Un fichier électoral est déjà en cours de traitement. Contactez un administrateur si nécessaire.';
          this.messageClass = 'warning';
          this.uploadForm.disable();
        }
      },
      error: (error) => {
        this.message = 'Erreur lors de la vérification du statut d\'upload.';
        this.messageClass = 'error';
        console.error('Erreur:', error);
      }
    });
  }

  /**
   * Gère le changement de fichier
   */
  onFileChange(event: any): void {
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      this.uploadForm.patchValue({ file: file });
    }
  }

  /**
   * Soumet le formulaire d'upload
   */
  submitForm(): void {
    if (this.uploadForm.invalid) {
      this.message = 'Veuillez remplir tous les champs correctement.';
      this.messageClass = 'error';
      return;
    }

    const checksum = this.uploadForm.get('checksum')?.value;
    const file = this.uploadForm.get('file')?.value;

    this.message = 'Fichier en cours de vérification...';
    this.messageClass = 'info';
    this.isUploading = true;

    // Vérifier si l'upload est autorisé avant de procéder
    this.fileUploadService.checkUploadStatus().subscribe({
      next: (statusResponse) => {
        if (statusResponse.upload_autorise) {
          // Upload du fichier électoral
          this.fileUploadService.uploadElectoralFile(file, checksum).subscribe({
            next: (uploadResponse) => {
              this.message = 'Fichier téléchargé avec succès. Analyse en cours...';
              this.messageClass = 'success';
              this.isUploading = false;
              this.isUploadComplete = true;
              this.tentativeId = uploadResponse.tentative_id;
              
              // Lancer automatiquement le contrôle des électeurs
              this.controlerElecteurs();
            },
            error: (uploadError) => {
              this.isUploading = false;
              this.handleApiError(uploadError, 'Erreur lors de l\'upload du fichier');
            },
          });
        } else {
          this.isUploading = false;
          this.message = 'L\'upload n\'est pas autorisé pour le moment.';
          this.messageClass = 'error';
        }
      },
      error: (statusError) => {
        this.isUploading = false;
        this.handleApiError(statusError, 'Erreur lors de la vérification du statut d\'upload');
      },
    });
  }

  /**
   * Lance le contrôle des électeurs
   */
  controlerElecteurs(): void {
    if (!this.tentativeId) {
      this.message = 'Identifiant de tentative manquant.';
      this.messageClass = 'error';
      return;
    }

    this.isProcessing = true;
    this.message = 'Contrôle des électeurs en cours...';
    this.messageClass = 'info';

    this.fileUploadService.controlerElecteurs(this.tentativeId).subscribe({
      next: (response) => {
        this.isProcessing = false;
        this.statistiques = response;
        this.peutValider = response.peut_valider;
        
        if (response.success) {
          this.message = `Contrôle terminé : ${response.statistiques.nbElecteursValides} électeurs valides sur ${response.statistiques.nbElecteursTotal}.`;
          this.messageClass = response.peut_valider ? 'success' : 'warning';
          
          // Extraire les types d'erreurs pour le filtrage
          this.typesErreurs = Object.keys(response.statistiques.typesErreurs);
          
          // Si des erreurs existent, charger les électeurs problématiques
          if (response.statistiques.nbElecteursInvalides > 0) {
            this.chargerElecteursProblematiques();
          }
        } else {
          this.message = response.message || 'Erreur lors du contrôle des électeurs.';
          this.messageClass = 'error';
        }
      },
      error: (error) => {
        this.isProcessing = false;
        this.handleApiError(error, 'Erreur lors du contrôle des électeurs');
      }
    });
  }

  /**
   * Charge la liste des électeurs problématiques
   */
  chargerElecteursProblematiques(): void {
    if (!this.tentativeId) return;

    this.fileUploadService.getElecteursProblematiques(this.tentativeId, this.filtreTypeErreur).subscribe({
      next: (response) => {
        this.electeursProblematiques = response.electeurs;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des électeurs problématiques:', error);
      }
    });
  }

  /**
   * Filtre les électeurs problématiques par type d'erreur
   */
  filtrerParTypeErreur(typeErreur: string): void {
    this.filtreTypeErreur = typeErreur;
    this.chargerElecteursProblematiques();
  }

  /**
   * Valide l'importation finale
   */
  validerImportation(): void {
    if (!this.tentativeId || !this.peutValider) {
      this.message = 'Validation impossible. Veuillez corriger les erreurs.';
      this.messageClass = 'error';
      return;
    }

    this.isValidating = true;
    this.message = 'Validation de l\'importation en cours...';
    this.messageClass = 'info';

    this.fileUploadService.validerImportation(this.tentativeId).subscribe({
      next: (response) => {
        this.isValidating = false;
        if (response.success) {
          this.message = `Importation validée avec succès. ${response.nb_electeurs_importes} électeurs importés.`;
          this.messageClass = 'success';
          
          // Réinitialiser le formulaire
          this.resetForm();
        } else {
          this.message = response.message || 'Erreur lors de la validation.';
          this.messageClass = 'error';
        }
      },
      error: (error) => {
        this.isValidating = false;
        this.handleApiError(error, 'Erreur lors de la validation de l\'importation');
      }
    });
  }

  /**
   * Réinitialise l'état d'upload (admin uniquement)
   */
  reinitialiserEtatUpload(): void {
    this.fileUploadService.reinitialiserEtatUpload().subscribe({
      next: (response) => {
        if (response.success) {
          this.message = response.message;
          this.messageClass = 'success';
          this.resetForm();
          this.uploadForm.enable();
        } else {
          this.message = response.message || 'Erreur lors de la réinitialisation.';
          this.messageClass = 'error';
        }
      },
      error: (error) => {
        this.handleApiError(error, 'Erreur lors de la réinitialisation');
      }
    });
  }

  /**
   * Réinitialise le formulaire et les états
   */
  resetForm(): void {
    this.uploadForm.reset();
    this.isUploadComplete = false;
    this.tentativeId = null;
    this.statistiques = null;
    this.peutValider = false;
    this.electeursProblematiques = [];
    this.typesErreurs = [];
    this.filtreTypeErreur = '';
  }

  /**
   * Gère les erreurs API de manière uniforme
   */
  private handleApiError(error: any, defaultMessage: string): void {
    console.error('Erreur API:', error);
    
    if (error.status === 403) {
      this.message = 'Vous n\'êtes pas autorisé à effectuer cette action.';
    } else if (error.status === 401) {
      this.message = 'Votre session a expiré. Veuillez vous reconnecter.';
    } else if (error.error && error.error.message) {
      this.message = error.error.message;
    } else {
      this.message = `${defaultMessage}. Erreur: ${error.status || 'inconnue'}`;
    }
    
    this.messageClass = 'error';
  }
}