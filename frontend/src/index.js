import { initAll } from 'govuk-frontend';

export { default as cookies } from './utils/cookies.js';
import { formsets } from './utils/formset.js';
import { opendate } from './reviews/opendate';
import { filterExportButton } from './stakeholders';

document.addEventListener('DOMContentLoaded', (event) => {
  initAll();
  formsets();
  opendate();
  filterExportButton();
})
