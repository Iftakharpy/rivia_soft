import DATA from "./parse_data.js";
import { fetch_url } from "./fetch_data.js";
import { makeSafeHTML, URL_HasQueryParams, dateFormat } from "./utilities.js";

const ObserverCallback = (entries, observer) => {
	entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.onVisible();
	});
};

const OBSERVER = new IntersectionObserver(ObserverCallback, {
	root: null, // Root element, null means the browser viewport
  rootMargin: "200px 0px 200px 0px", // Margin around the root
	threshold: 0.005, // Trigger the callback when 100% of the target is visible
});

let CLIENT_RATING_FIELDS = [
	{
		model: "companies.selfassesment",
		fields: ["client_rating"],
		rating_symbol: "🔷",
	},
	{
		model: "companies.limited",
		fields: ["client_rating"],
		rating_symbol: "🔷",
	},
];

let template_querySelector = "template#data-template";
let template = document.querySelector(template_querySelector);
// Prepare row for data table
export async function get_tr_for_table(
	data,
	template = template,
	model_fields = DATA.model_fields,
	update_url = DATA.update_url,
	delete_url = DATA.delete_url
) {
	// prepare table row for table using template and data
	let selfassesmentAccountSubmission_home_pathname = "/companies/SAS/home/";

	let instance = template.content.cloneNode(true);
	let serial_num = instance.getElementById("pk");

	if (
		serial_num &&
		location.pathname == selfassesmentAccountSubmission_home_pathname
	) {
		serial_num.innerHTML = `<a target="_blank" href="/accounts/?pk=${data.pk}">${data.pk}</a>`;
	} else if (serial_num) {
		serial_num.textContent = data.pk;
	}

	let update_link;
	if (update_url.includes("{pk}"))
		update_link = update_url.replace("{pk}", data.pk);
	else update_link = `${update_url}${data.pk}/`;

	let delete_link;
	if (delete_url.includes("{pk}"))
		delete_link = delete_url.replace("{pk}", data.pk);
	else delete_link = `${delete_url}${data.pk}/`;

	instance.getElementById("edit").href = `${update_link}`;
	instance.getElementById("delete").href = `${delete_link}`;
	if (
		["/", "/companies/", "/companies/MTrc/home/"].includes(
			location.pathname
		)
	) {
		instance.getElementById("edit").target = `blank`;
		instance.getElementById("delete").target = `blank`;
	}

	// fill the template
	for (let field of model_fields) {
		let field_data = data.fields[field];
		let formatted_text = document.createElement("pre");
		let td = instance.getElementById(field);
		if (!td) continue;

		let data_field = td.getAttribute("data-field");
		if (data_field) {
			let field_data_format = `{${data_field}}`;
			field_data = field_data_format.format(data);
		}
		if (field_data == null) continue;

		formatted_text.innerHTML = makeSafeHTML(`${field_data}`);

		td.classList.add("whitespace-nowrap"); // show text in one line

		// data to compare elements in table_sort.js
		td.setAttribute("data-cmp", field_data);
		td.setAttribute("data-identifier", field);

		let matched_for_client_rating = CLIENT_RATING_FIELDS.find(
			(field) => field.model === data.model
		);
		if (
			matched_for_client_rating &&
			matched_for_client_rating.fields.includes(field)
		) {
			td.textContent =
				matched_for_client_rating.rating_symbol.repeat(field_data);
			continue;
		}

		// Foreign Data
		let data_url = td.getAttribute("data-url");

		if (data_url && field_data) {
			//this is a foreign key field. fetch the data and format it
			// populate_with_foreign_data(td, field, field_data, data);
			td.onVisible = () => {
        OBSERVER.unobserve(td);
        td.onVisible = null;
				populate_with_foreign_data(td, field, field_data, data);
			};
			OBSERVER.observe(td);
			continue;
		}

		// Number data
		if (typeof field_data == "number") {
			td.textContent = field_data;
			continue;
		}

		// Boolean data
		if (typeof field_data === "boolean") {
			//data is boolean so show it as checkbox
			let checked_checkbox = `<input type="checkbox" checked="" disabled>`;
			let unchecked_checkbox = `<input type="checkbox" disabled>`;
			if (field_data) {
				td.innerHTML = checked_checkbox;
			} else {
				td.innerHTML = unchecked_checkbox;
			}
			continue;
		}

		// date/time data
		let date = dayjs(field_data);
		if (
			!isNaN(date) &&
			typeof field_data === "string" &&
			((field_data[4] === "-" && field_data[7] === "-") ||
				field_data[2] === ":")
		) {
			//this is date field so show it in local format
			td.textContent = dateFormat(date, field_data);
			continue;
		}

		if (
			location.pathname ===
				selfassesmentAccountSubmission_home_pathname &&
			field === "unique_public_view_key"
		) {
			let public_view_link = instance.getElementById(
				"unique_public_view_key"
			);
			public_view_link.innerHTML = `<a data-field="${field}" href='/accounts/public_tax_report/${data.pk}/${data.fields.unique_public_view_key}/'>${data.fields.unique_public_view_key}</a>`;
			continue;
		}

		// show preformatted text
		td.appendChild(formatted_text);

		// pretty-format text
		td.classList.add("whitespace-normal");
		td.style.textAlign = "justify";
		td.style.minWidth = `${field_data.length + 1}ch`;
		if (field_data.length >= 37) {
			td.classList.remove("whitespace-nowrap");
			td.style.minWidth = "37ch";
			formatted_text.style.maxWidth = "37ch";
			formatted_text.style.whiteSpace = "pre-wrap";
		}
	}
	return instance;
}

export async function populate_with_foreign_data(td, field, field_data, data) {
	// console.log("populate_with_foreign_data", field, field_data, data);
	if (field_data == "null") return;
	td.setAttribute("data-foreign-data", "true");
	td.setAttribute("data-foreign-model", data.model);
	td.setAttribute("data-foreign-field-name", field);

	let data_url = td.getAttribute("data-url");
	let repr_format = td.getAttribute("data-repr-format");
	let url_ending = td.getAttribute("data-url-ending");
	let has_ending_slash = data_url.slice(-1) == "/";
	let has_query_params = data_url.includes("?");

	if (!has_ending_slash && !has_query_params) data_url = `${data_url}/`;

	if (url_ending) data_url = `${data_url}${field_data}${url_ending}`;
	else if (has_query_params) data_url = `${data_url}${field_data}`;
	else data_url = `${data_url}${field_data}/`;

	let kwargs = {
		url: data_url,
		req_method: "GET",
	};
	let resp = await fetch_url(kwargs).then((response) => response.json());

	let string = repr_format.formatMultiplication(resp);
	string = string.format(resp);

	td.textContent = string;
	td.removeAttribute("data-url");
	td.removeAttribute("data-repr-format");
	td.setAttribute("data-cmp", string);

	td.classList.add("whitespace-normal");
	td.style.textAlign = "justify";
	td.style.whiteSpace = "nowrap";
	td.style.minWidth = `${field_data.length + 1}ch`;
	if (string.length >= 37) {
		td.classList.remove("whitespace-nowrap");
		td.style.minWidth = "37ch";
		td.style.maxWidth = "37ch";
		td.style.whiteSpace = "pre-wrap";
	}

	let hrefURL = td.getAttribute("data-href-url");
	if (hrefURL) {
		let url = hrefURL.format(data);
		if (!hrefURL.includes("{")) {
			url = `${hrefURL}${field_data}/`;
		}
		td.innerHTML = `<a data-field="${field}" href="${url}">${makeSafeHTML(
			string
		)}</a>`;
	}
}

// Update table date with the provided data
export async function populate_with_data(
	data_array,
	template_querySelector_string = template_querySelector,
	model_fields = DATA.model_fields,
	update_url = DATA.update_url,
	delete_url = DATA.delete_url,
	clear_table_before_insertion = true
) {
	let template = document.querySelector(template_querySelector_string); //find template

	let tbody = document.querySelector("tbody#data"); // find data container
	if (clear_table_before_insertion) tbody.innerHTML = ""; // clear the container

	// Populate the table using the provided data
	for (let record of data_array) {
		let table_row = await get_tr_for_table(
			record,
			template,
			model_fields,
			update_url,
			delete_url
		);
		tbody.appendChild(table_row);
	}
}

export async function populate_with_merged_data(
	merged_data,
	selfassesment_template_querySelector_string = template_querySelector,
	selfassesment_model_fields = DATA.model_fields,
	selfassesment_update_url = DATA.update_url,
	selfassesment_delete_url = DATA.delete_url,
	limited_template_querySelector_string = template_querySelector,
	limited_model_fields = DATA.model_fields,
	limited_update_url = DATA.update_url,
	limited_delete_url = DATA.delete_url,
	clear_table_before_insertion = true
) {
	let selfassesment_template = document.querySelector(
		selfassesment_template_querySelector_string
	); //find template
	let limited_template = document.querySelector(
		limited_template_querySelector_string
	); //find template

	let tbody = document.querySelector("tbody#data"); // find data container
	if (clear_table_before_insertion) tbody.innerHTML = ""; // clear the container

	// Populate the table using the provided data
	for (let record of merged_data) {
		let table_row = null;
		if (record.model === "companies.selfassesmenttracker")
			table_row = await get_tr_for_table(
				record,
				selfassesment_template,
				selfassesment_model_fields,
				selfassesment_update_url,
				selfassesment_delete_url
			);
		if (record.model === "companies.limitedtracker")
			table_row = await get_tr_for_table(
				record,
				limited_template,
				limited_model_fields,
				limited_update_url,
				limited_delete_url
			);
		tbody.appendChild(table_row);
	}
}
