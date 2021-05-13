import { initAll } from 'govuk-frontend';

export { default as cookies } from './utils/cookies.js';
import { formsets } from './utils/formset.js';
import { opendate } from './reviews/opendate';
import { filterExportButton } from './stakeholders';
import { initCookieBanner } from './components/cookie-banner';

const initApp = () => {
  initAll();
  formsets();
  opendate();
  filterExportButton();
  initCookieBanner();
}

export {
  initApp
}
