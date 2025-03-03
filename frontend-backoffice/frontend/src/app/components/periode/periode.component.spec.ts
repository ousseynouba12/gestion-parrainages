import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PeriodeComponent } from './periode.component';

describe('PeriodeComponent', () => {
  let component: PeriodeComponent;
  let fixture: ComponentFixture<PeriodeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PeriodeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PeriodeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
