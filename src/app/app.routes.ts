import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { PeriodeparrainageComponent } from './periodeparrainage/periodeparrainage.component';
import { CandidatComponent } from './candidat/candidat.component';
import { FichierelectoralComponent} from './fichierelectoral/fichierelectoral.component';
import { SuiviparrainageComponent } from './suiviparrainage/suiviparrainage.component';
import { ListecandidatComponent} from './listecandidat/listecandidat.component';

export const routes: Routes = [ 
    { path: '', redirectTo: '/login', pathMatch: 'full' },
    { path: 'login', component: LoginComponent },
    { path: 'dashboard', component: DashboardComponent },
    { path: 'periodeparrainage', component: PeriodeparrainageComponent },
    { path: 'candidat', component: CandidatComponent },
    { path: 'fichierelectoral', component: FichierelectoralComponent },
    { path: 'suiviparrainage', component: SuiviparrainageComponent },
    { path: 'listecandidat', component: ListecandidatComponent },

];

