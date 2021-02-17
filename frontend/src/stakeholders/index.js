
export const filterExportButton  = () => {
   const form = document.getElementById("stakeholder-filter");
   const button = document.getElementById("export-button");

   form.addEventListener("input", function () {
       button.innerHTML = "Export current search results";
   });
}