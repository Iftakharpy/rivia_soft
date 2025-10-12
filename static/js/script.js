import { populate_with_data } from "./table.js";
import {
	db_all_records,
	db_search_records,
	db_search_records_client_id,
} from "./fetch_data.js";
import DATA from "./parse_data.js";
//table cell compare attribute name = "data-cmp"

// clear message after 10 seconds
let delete_message_after = 10000; //millisecond
setTimeout(function () {
	let messages = document.querySelectorAll(".message");
	if (messages) {
		for (let element of messages) {
			element.remove();
		}
	}
}, delete_message_after);

// ================================================================================================
// Handle reload
if (!["/companies/MTrc/home/", "/"].includes(location.pathname)) {
	// don't add reload handler for view tracker, merged tracker will handle that
	document
		.querySelector(".action-reload")
		?.addEventListener("click", async (event) => {
			loadAllRecords();
		});
}

// Search functionality
//setup before functions
let typingTimer; //timer identifier
//                milliseconds * seconds
let doneTypingInterval = 1000; //time in ms (4/5 seconds)
//on keyup, start the countdown
// document.getElementById('element-id').addEventListener('keyup', () => {
//     clearTimeout(typingTimer);
//     if (myInput.value) {
//         typingTimer = setTimeout(search_function, doneTypingInterval);
//     }
// });
const tax_year_select_input = document.querySelector("select#tax_years");
const search_bar = document.querySelector('input[name="search"]');
function searchHandler(event) {
	let search_url = DATA.search_url;
	let search_text = search_bar.value.trim();

	// reset timer to prevent extra search
	clearTimeout(typingTimer);
	// set the timer again to call api after doneTypingInterval
	if (search_text === "" || search_url === undefined) {
		// typingTimer = setTimeout( async () => {
		//   loadAllRecords()
		// }, doneTypingInterval); // Get all the records
	} else {
		typingTimer = setTimeout(
			async (search_text, search_url) => {
				let search_records = await db_search_records(
					search_text,
					search_url
				);
				populate_with_data(search_records);
			},
			doneTypingInterval,
			search_text,
			search_url
		); // search with text
	}
}
if (search_bar) {
	search_bar.addEventListener("input", searchHandler);
}
if (tax_year_select_input) {
	tax_year_select_input.addEventListener("change", searchHandler);
}

export function loadAllRecords() {
	setTimeout(async () => {
		let all_records = await db_all_records();
		populate_with_data(all_records);
	}, 10); // search with text
}
// loadAllRecords()

// OpenSearch
let current_url = window.location.href;
let url = new URL(current_url);
let tasks = url.searchParams.get("tasks");
if (tasks) {
	let taskCounter = document.querySelector(`.task[data-tasks="${tasks}"]`);
	if (taskCounter) taskCounter.click();
}

// if (url.pathname==="/companies/SAS/home/"){
//   let reloadBtn = document.querySelector(".action.action-reload")
//   reloadBtn.click()
// }

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
window.addEventListener("load", function () {
	// This function runs only after ALL resources (images, CSS, etc.) have loaded
	let exportActionBtn = document.querySelector(".action-export");
	let exportActionAnchor = exportActionBtn?.querySelector("a");
	let exportColumnsContainer = document.querySelector(
		"[data-export-columns-container]"
	);
	let exportColumnsClose = document.querySelector(
		"[data-export-columns-close]"
	);
	let exportColumnsSubmit = document.querySelector(
		"[data-export-columns-submit]"
	);
	
	let els = [exportActionAnchor, exportColumnsClose, exportColumnsSubmit]
	els.forEach(
		(element) => {
			// preventing default handler to avoid reload and immediate download
			element.addEventListener("click", (ev) => ev.preventDefault());
		}
	);
	// Handle select/deselect all field
	let fieldGroupToggles = this.document.querySelectorAll(
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

	this.document.addEventListener("keydown", (e) => {
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
		if (tax_year_select_input != null) {
			let tax_year = tax_year_select_input.value;
			url.searchParams.set("tax_year", tax_year);
		}
		
		const selectedFieldNames = getSelectedFieldNames();
		url.searchParams.set("export_fields", selectedFieldNames.join(","));
		// opening a new tab will download the csv file
		this.window.open(url.href);
	});
});
