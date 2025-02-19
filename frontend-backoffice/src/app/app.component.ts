import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from "./layout/sidebar/sidebar.component";
import { NavbarComponent } from "./layout/navbar/navbar.component";

import { ReactiveFormsModule } from '@angular/forms';


@Component({
  selector: 'app-root',
  imports: [CommonModule,SidebarComponent,NavbarComponent,RouterOutlet,ReactiveFormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'plateformeDGE';
}
