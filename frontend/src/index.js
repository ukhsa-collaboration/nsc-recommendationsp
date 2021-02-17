import { initAll } from 'govuk-frontend';

import { formsets } from './utils/formset.js';
import { opendate } from './reviews/opendate';
import { filterExportButton } from './stakeholders';

initAll();

document.addEventListener('DOMContentLoaded', (event) => {
  formsets();
})

document.addEventListener('DOMContentLoaded', (event) => {
  opendate();
})

document.addEventListener('DOMContentLoaded', (event) => {
    filterExportButton();
})
