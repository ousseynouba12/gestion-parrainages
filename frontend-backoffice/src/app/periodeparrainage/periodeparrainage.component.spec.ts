import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PeriodeparrainageComponent } from './periodeparrainage.component';

describe('PeriodeparrainageComponent', () => {
  let component: PeriodeparrainageComponent;
  let fixture: ComponentFixture<PeriodeparrainageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PeriodeparrainageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PeriodeparrainageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
