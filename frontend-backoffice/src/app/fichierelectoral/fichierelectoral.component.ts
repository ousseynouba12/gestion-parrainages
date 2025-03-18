import { Component } from '@angular/core';
import { ElectoralFileService } from '../services/file-upload.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-upload-electoral-file',
  imports :[CommonModule,FormsModule],
  templateUrl: './fichierelectoral.component.html',
  styleUrls: ['./fichierelectoral.component.css']
})
export class FichierelectoralComponent {
  file: File | null = null;
  checksum: string = '';
  uploadStatus: any = null;
  tentativeId: number | null = null;
  controlResult: any = null;
  importStatistics: any = null;
  problematicElectors: any = null;

  constructor(private electoralFileService: ElectoralFileService) {}

  onFileChange(event: any): void {
    this.file = event.target.files[0];
  }

  onChecksumChange(event: any): void {
    this.checksum = event.target.value;
  }

  checkUploadStatus(): void {
    this.electoralFileService.checkUploadStatus().subscribe(
      (response) => {
        this.uploadStatus = response;
      },
      (error) => {
        console.error('Error checking upload status:', error);
      }
    );
  }

  uploadFile(): void {
    if (this.file && this.checksum) {
      this.electoralFileService.uploadElectoralFile(this.file, this.checksum).subscribe(
        (response) => {
          this.tentativeId = response.tentative_id;
          console.log('File uploaded successfully:', response);
        },
        (error) => {
          console.error('Error uploading file:', error);
        }
      );
    } else {
      console.error('File and checksum are required.');
    }
  }

  controlElectors(): void {
    if (this.tentativeId) {
      this.electoralFileService.controlElectors(this.tentativeId).subscribe(
        (response) => {
          this.controlResult = response;
          console.log('Electors controlled successfully:', response);
        },
        (error) => {
          console.error('Error controlling electors:', error);
        }
      );
    } else {
      console.error('Tentative ID is required.');
    }
  }

  validateImport(): void {
    if (this.tentativeId) {
      this.electoralFileService.validateImport(this.tentativeId).subscribe(
        (response) => {
          console.log('Import validated successfully:', response);
        },
        (error) => {
          console.error('Error validating import:', error);
        }
      );
    } else {
      console.error('Tentative ID is required.');
    }
  }

  getImportStatistics(): void {
    if (this.tentativeId) {
      this.electoralFileService.getImportStatistics(this.tentativeId).subscribe(
        (response) => {
          this.importStatistics = response;
          console.log('Import statistics:', response);
        },
        (error) => {
          console.error('Error getting import statistics:', error);
        }
      );
    } else {
      console.error('Tentative ID is required.');
    }
  }

  getProblematicElectors(errorType?: string): void {
    if (this.tentativeId) {
      this.electoralFileService.getProblematicElectors(this.tentativeId, errorType).subscribe(
        (response) => {
          this.problematicElectors = response;
          console.log('Problematic electors:', response);
        },
        (error) => {
          console.error('Error getting problematic electors:', error);
        }
      );
    } else {
      console.error('Tentative ID is required.');
    }
  }

  resetUploadState(): void {
    this.electoralFileService.resetUploadState().subscribe(
      (response) => {
        console.log('Upload state reset successfully:', response);
      },
      (error) => {
        console.error('Error resetting upload state:', error);
      }
    );
  }
}