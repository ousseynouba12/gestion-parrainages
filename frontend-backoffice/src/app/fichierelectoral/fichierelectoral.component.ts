import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { FileUploadService } from '../services/file-upload.service';

@Component({
  selector: 'app-fichierelectoral',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './fichierelectoral.component.html',
  styleUrls: ['./fichierelectoral.component.css'],
})
export class FichierelectoralComponent {
  uploadForm: FormGroup;
  message: string = '';
  messageClass: string = '';

  constructor(private fb: FormBuilder, private fileUploadService: FileUploadService) {
    this.uploadForm = this.fb.group({
      checksum: ['', [Validators.required, Validators.minLength(64), Validators.maxLength(64)]],
      file: [null, Validators.required],
    });
  }

  onFileChange(event: any) {
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      this.uploadForm.patchValue({ file: file });
    }
  }

  submitForm() {
    if (this.uploadForm.invalid) {
      this.message = 'Veuillez remplir tous les champs correctement.';
      this.messageClass = 'error';
      return;
    }

    const checksum = this.uploadForm.get('checksum')?.value;
    const file = this.uploadForm.get('file')?.value;

    this.message = 'Fichier en cours de vérification...';
    this.messageClass = 'info';

    // Vérifier si l'upload est autorisé avant de procéder
    this.fileUploadService.checkUploadStatus().subscribe({
      next: (statusResponse) => {
        if (statusResponse.upload_autorise) {
          // Upload du fichier électoral
          this.fileUploadService.uploadElectoralFile(file, checksum).subscribe({
            next: (uploadResponse) => {
              this.message = 'Fichier téléchargé et validé avec succès.';
              this.messageClass = 'success';
              console.log('Réponse de l\'upload:', uploadResponse);
            },
            error: (uploadError) => {
              this.message = 'Erreur lors de l\'upload du fichier.';
              this.messageClass = 'error';
              console.error('Erreur d\'upload:', uploadError);
            },
          });
        } else {
          this.message = 'L\'upload n\'est pas autorisé pour le moment.';
          this.messageClass = 'error';
        }
      },
      error: (statusError) => {
        this.message = 'Erreur lors de la vérification du statut d\'upload.';
        this.messageClass = 'error';
        console.error('Erreur de statut:', statusError);
      },
    });
  }
}