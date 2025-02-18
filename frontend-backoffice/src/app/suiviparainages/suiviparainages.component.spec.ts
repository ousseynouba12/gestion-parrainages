import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SuiviparainagesComponent } from './suiviparainages.component';

describe('SuiviparainagesComponent', () => {
  let component: SuiviparainagesComponent;
  let fixture: ComponentFixture<SuiviparainagesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SuiviparainagesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SuiviparainagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
