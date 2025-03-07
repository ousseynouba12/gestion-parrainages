import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { UploadService } from '../../services/upload.service'; 

@Component({
  selector: 'upload-root',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css'],
  imports : [CommonModule, FormsModule]  
})
export class UploadComponent {
  checksum: string = '';  
  file: File | null = null; 
  message: string = ''; 

  constructor(private uploadService: UploadService) {}  


  onFileChange(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.file = file;
    }
  }


  upload(): void {
    if (!this.file || !this.checksum) {
      this.message = 'Veuillez sélectionner un fichier et entrer une empreinte SHA256';
      return;
    }
    this.uploadFile(this.file, this.checksum);
  }


  uploadFile(file: File, checksum: string): void {
    this.uploadService.uploadFile(file, checksum).subscribe(
      (response) => {
        this.message = 'Importation réussie!';
      },
      (error) => {
        this.message = 'Erreur lors de l\'importation';
      }
    );
  }
}
