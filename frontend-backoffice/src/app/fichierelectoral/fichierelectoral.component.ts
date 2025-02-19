import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';




@Component({
  selector: 'app-fichierelectoral',
  imports: [ReactiveFormsModule,CommonModule],
  templateUrl: './fichierelectoral.component.html',
  styleUrl: './fichierelectoral.component.css'
})
export class FichierelectoralComponent {
  uploadForm: FormGroup;
  message: string = '';
  messageClass: string = '';

  constructor(private fb: FormBuilder) {
    this.uploadForm = this.fb.group({
      checksum: ['', [Validators.required, Validators.minLength(64), Validators.maxLength(64)]],
      file: [null, Validators.required]
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

    // Simulation d'envoi (remplacer par un service HTTP)
    this.message = 'Fichier en cours de vérification...';
    this.messageClass = 'info';

    setTimeout(() => {
      this.message = 'Fichier importé avec succès !';
      this.messageClass = 'success';
    }, 2000);
  }
}
