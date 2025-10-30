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
const search_bar = document.querySelector('[name="search"]');
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
