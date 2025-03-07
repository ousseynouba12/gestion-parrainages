import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SuiviparrainageComponent } from './suiviparrainage.component';

describe('SuiviparrainageComponent', () => {
  let component: SuiviparrainageComponent;
  let fixture: ComponentFixture<SuiviparrainageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SuiviparrainageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SuiviparrainageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
