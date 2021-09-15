import accessibleAutocomplete from 'accessible-autocomplete';

export const initAutocomplete = (document) => {
    const containers = document.getElementsByClassName("autocomplete-container");

    for(const element of containers) {
        accessibleAutocomplete({
            element,
            id: element.attributes["data-field-id"].value,
            name: element.attributes["data-field-name"].value,
            defaultValue: element.attributes["data-default-value"].value,
            source: JSON.parse(
                document.getElementById(element.attributes["data-source-id"].value).text
            ),
        })
    }
}
