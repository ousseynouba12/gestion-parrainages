import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { PeriodeparrainageComponent } from './periodeparrainage/periodeparrainage.component';
import { CandidatComponent } from './candidat/candidat.component';
import { FichierelectoralComponent} from './fichierelectoral/fichierelectoral.component';
import { SuiviparrainageComponent } from './suiviparrainage/suiviparrainage.component';
import { ListecandidatComponent} from './listecandidat/listecandidat.component';
import { authGuard } from './services/auth.guard';

export const routes: Routes = [ 
    { path: 'login', component: LoginComponent },
    { 
        path: '', 
        canActivate: [authGuard],
        children: [
          { path: 'candidat', component: CandidatComponent },
          { path: 'listecandidat', component: ListecandidatComponent },
          { path: 'periodeparrainage', component: PeriodeparrainageComponent },
          { path: 'fichierelectoral', component: FichierelectoralComponent },
          { path: 'suiviparrainage', component: SuiviparrainageComponent },
          { path: '', redirectTo: 'suiviparrainage', pathMatch: 'full' }
        ]
      },
      
      // Redirection vers la page de connexion pour les routes non trouvées
      { path: '**', redirectTo: '/login' },  

    // Redirection vers la page de connexion par défaut
    { path: '', redirectTo: '/login', pathMatch: 'full' },
   
    { path: 'fichierelectoral', component: FichierelectoralComponent },
];

