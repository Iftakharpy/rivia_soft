
// ================================================================================================
// Handle export for pages which has tax year input beside search bar
/**
 * Gets a list of the 'value' (field names) for all checked export columns.
 * @returns {string[]} An array of selected field names.
 */
function getSelectedFieldNames() {
	let form = document.querySelector("form[data-export-form]");
	if (!form) {
		console.error("Export form not found.");
		return [];
	}
	let checkedInputs = form.querySelectorAll("input[data-field]:checked");
	let selectedFieldNames = Array.from(checkedInputs).map(
		(input) => input.value
	);
	return selectedFieldNames;
}


const exportActionBtn = document.querySelector(".action-export");
if (exportActionBtn==undefined) {
		console.error("Export action button undefined. Column name selection during data export won't work.")
	};
const exportActionAnchor = exportActionBtn.querySelector("a");
const exportColumnsContainer = document.querySelector(
	"[data-export-columns-container]"
);
const exportColumnsClose = document.querySelector(
	"[data-export-columns-close]"
);
const exportColumnsSubmit = document.querySelector(
	"[data-export-columns-submit]"
);

const els = [exportActionAnchor, exportColumnsClose, exportColumnsSubmit]
els.forEach(
	(element) => {
		// preventing default handler to avoid reload and immediate download
		element.addEventListener("click", (ev) => ev.preventDefault());
	}
);

// Handle select/deselect all field
const fieldGroupToggles = document.querySelectorAll(
	"[data-field-group-toggle]"
);
fieldGroupToggles?.forEach((checkbox) => {
	checkbox.addEventListener("click", (e) => {
		let isSelectAll = checkbox.checked;
		let group = checkbox.closest("[data-field-group]");
		let field_checkboxes = group.querySelectorAll(
			"ul input[data-field]"
		);
		if (isSelectAll)
			field_checkboxes.forEach((field) => (field.checked = true));
		else field_checkboxes.forEach((field) => (field.checked = false));
	});
});

document.addEventListener("keydown", (e) => {
	if (e.key == "Escape") {
		exportColumnsContainer?.classList.add(
			exportColumnsContainer?.getAttribute("data-hide-class")
		);
	}
});
exportColumnsClose?.addEventListener("click", (ev) => {
	exportColumnsContainer?.classList.add(
		exportColumnsContainer?.getAttribute("data-hide-class")
	);
});
exportActionBtn?.addEventListener("click", (ev) => {
	exportColumnsContainer?.classList.remove(
		exportColumnsContainer?.getAttribute("data-hide-class")
	);
});


// Handle export fields
exportColumnsSubmit?.addEventListener("click", (ev) => {
	let url = new URL(exportActionAnchor.href);
	
	// add "tax_year" query param
	const tax_year_select_input = document.querySelector('select#tax_years')
	if (tax_year_select_input != null) {
		let tax_year = tax_year_select_input.value;
		url.searchParams.set("tax_year", tax_year);
	}
	
	// add "data_filter_query" text to filter rows
	const data_filter_query_text = document.querySelector('[name="data_filter_query"]')
	url.searchParams.set("data_filter_query", data_filter_query_text.value)
	
	// add "export_fields" to export only selected columns
	const selectedFieldNames = getSelectedFieldNames();
	url.searchParams.set("export_fields", selectedFieldNames.join(","));
	
	// opening a new tab will download the csv file
	window.open(url.href);
});

