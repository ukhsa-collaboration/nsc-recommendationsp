import { initAll } from 'govuk-frontend';

export { default as cookies } from './utils/cookies.js';
import { formsets } from './utils/formset.js';
import { opendate } from './reviews/opendate';
import { filterExportButton } from './stakeholders';
import { initCookieBanner } from './components/cookie-banner';
import { initAutocomplete } from './autocomplete';

const initApp = () => {
  if (document.readyState === "complete") {
    initAll();
    formsets();
    opendate();
    filterExportButton();
    initCookieBanner();
    initAutocomplete(document);
  }
}

export {
  initApp
}
