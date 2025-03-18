import { TestBed } from '@angular/core/testing';

import { ParainageService } from './parainage.service';

describe('ParainageService', () => {
  let service: ParainageService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ParainageService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
