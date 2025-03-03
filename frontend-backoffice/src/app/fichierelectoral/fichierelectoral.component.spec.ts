import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FichierelectoralComponent } from './fichierelectoral.component';

describe('FichierelectoralComponent', () => {
  let component: FichierelectoralComponent;
  let fixture: ComponentFixture<FichierelectoralComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FichierelectoralComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FichierelectoralComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
