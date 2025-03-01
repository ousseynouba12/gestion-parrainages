import { RouterModule, Routes } from '@angular/router';
import { UploadComponent } from './components/upload/upload.component';
import { PeriodeComponent } from './components/periode/periode.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { NavComponent } from './nav/nav.component';
import { CandidatComponent } from './components/candidat/candidat.component';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'importe', component: UploadComponent },
  { path: 'periode' , component: PeriodeComponent},
  { path: 'candidat' , component: CandidatComponent}
];
