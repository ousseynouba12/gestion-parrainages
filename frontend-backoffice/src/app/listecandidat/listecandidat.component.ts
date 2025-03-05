import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-listecandidat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './listecandidat.component.html',
  styleUrl: './listecandidat.component.css'
})

export class ListecandidatComponent {
 
    candidats = [
      {
        id: 1,
        nom: 'Dupont',
        prenom: 'Jean',
        naissance: '01/01/1990',
        email: 'jean.dupont@email.com',
        telephone: '0123456789',
        parti: 'Parti A',
        slogan: 'Un avenir meilleur',
        photo: 'photo_jean.jpg',
        couleurs: ['Rouge', 'Blanc', 'Bleu'],
        url: 'https://jeandupont.fr'
      },
      {
        id: 2,
        nom: 'Martin',
        prenom: 'Claire',
        naissance: '05/02/1985',
        email: 'claire.martin@email.com',
        telephone: '0987654321',
        parti: 'Parti B',
        slogan: 'Ensemble pour demain',
        photo: 'photo_claire.jpg',
        couleurs: ['Vert', 'Jaune', 'Noir'],
        url: 'https://clairemartin.fr'
      }
    ];
  
    selectedCandidat: any = null;
  
    showDetails(candidat: any) {
      console.log("Candidat sélectionné :", candidat);
      this.selectedCandidat = candidat;
    }
    
  
    closeDetails() {
      this.selectedCandidat = null;
    }
  }
