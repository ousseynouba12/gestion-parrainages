import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-candidat',
  imports: [CommonModule,FormsModule],
  templateUrl: './candidat.component.html',
  styleUrl: './candidat.component.css'
})
export class CandidatComponent {
  carteElecteur = '';
  messageErreur = '';
  formCandidat = false;
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

  verifierCandidat() {
    if (this.carteElecteur === '123456') {
      this.messageErreur = '';
      this.formCandidat = true;
      this.nom = 'Doe';
      this.prenom = 'John';
      this.dateNaissance = '1985-06-15';
    } else if (this.carteElecteur === '654321') {
      this.messageErreur = 'Candidat déjà enregistré !';
      this.formCandidat = false;
    } else {
      this.messageErreur = 'Le candidat considéré n’est pas présent dans le fichier électoral.';
      this.formCandidat = false;
    }
  }

  onFileSelected(event: any) {
    this.photo = event.target.files[0];
  }

  enregistrerCandidat() {
    alert('Candidature enregistrée avec succès ! Un code de sécurité a été envoyé.');
  }
}
