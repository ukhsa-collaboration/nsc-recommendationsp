import { initAll } from 'govuk-frontend';

import { formsets } from './utils/formset.js';

initAll();

document.addEventListener('DOMContentLoaded', (event) => {
  formsets();
})

