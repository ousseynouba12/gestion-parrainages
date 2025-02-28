import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListecandidatComponent } from './listecandidat.component';

describe('ListecandidatComponent', () => {
  let component: ListecandidatComponent;
  let fixture: ComponentFixture<ListecandidatComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListecandidatComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListecandidatComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
