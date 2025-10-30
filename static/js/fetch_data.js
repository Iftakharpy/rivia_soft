import { deepCompare, catchErrorAndLog } from "./utilities.js";
import DATA from "./parse_data.js";

//====================================================================================================================================
// get data from backend
export async function db_all_records(all_url = DATA.all_url, tax_year = null) {
	if (tax_year === null) tax_year = DATA.tax_year;
	let params = { tax_year: tax_year };
	let search_param = new URLSearchParams(params).toString();

	let url_to_fetch = `${all_url}?${search_param}`;

	let kwargs = {
		url: url_to_fetch,
		req_method: "GET",
	};
	const records = await fetch_url(kwargs).then((res) => res.json()); // convert response to JSON
	return records; // return data
}

export async function db_search_records(
	search_text,
	search_url = DATA.search_url,
	tax_year = null
) {
	if (tax_year === null) tax_year = DATA.tax_year;
	let params = { q: search_text, tax_year: tax_year };
	let search_param = new URLSearchParams(params).toString();

	let url_to_fetch = `${search_url}?${search_param}`;

	let kwargs = {
		url: url_to_fetch,
		req_method: "GET",
	};
	const records = await fetch_url(kwargs).then((res) => res.json()); // convert response to JSON
	return records; // return data
}
export async function db_search_records_client_id(
	client_id,
	search_url = DATA.search_url
) {
	let params = { client_id: client_id };
	let search_param = new URLSearchParams(params).toString();
	let kwargs = {
		url: `${search_url}?${search_param}`,
		req_method: "GET",
	};
	const records = await fetch_url(kwargs).then((res) => res.json()); // convert response to JSON
	return records; // return data
}

// =============================================================================================================================
// Api caller

function cache_duration_calc({
	hours = 0,
	minutes = 0,
	seconds = 0,
	milliseconds = 0,
}) {
	return (hours * 60 * 60 + minutes * 60 + seconds) * 1000 + milliseconds;
}
let API_CACHE = null;
let cache_duration_obj = { hours: 3 };
const max_cache_duration = cache_duration_calc(cache_duration_obj);

async function evict_cache() {
	if (API_CACHE !== null) return;

	let keys = await caches.keys();
	let new_key = new Date().getTime();
	let keys_to_number = keys.map((key) => Number(key)).sort((a, b) => a - b);

	let is_latest_key_valid =
		new Date().getTime() - keys_to_number[keys_to_number.length - 1] <
		max_cache_duration;
	if (is_latest_key_valid) {
		// Reuse valid cache
		new_key = keys_to_number.pop();
	}

	for (let key of keys_to_number) {
		// Remove expired caches
		caches.delete(key.toString());
	}

	caches.open(new_key.toString()).then((cache) => {
		console.log("Cache duration:", cache_duration_obj);
		console.log("Cache created:", new Date(new_key).toISOString());
		console.log(
			"Eviction time:",
			new Date(new_key + max_cache_duration).toISOString()
		);
		API_CACHE = cache;
		globalThis.API_CACHE = cache;
	});
}
await evict_cache();

// Evict cache after max_cache_duration
// setTimeout(() => {
//   evict_cache();
// }, max_cache_duration);

// =========================================================================================================
// Show and hide loading indicator when data is loading
const loading_indicator_selector = "#loading-indicator";

export function showLoadingIndicator() {
	let loading_indicator = document.querySelector(loading_indicator_selector);
	if (loading_indicator !== null)
		loading_indicator.classList.remove("hidden");
}

export function hideLoadingIndicator() {
	let loading_indicator = document.querySelector(loading_indicator_selector);
	if (loading_indicator !== null) loading_indicator.classList.add("hidden");
}

// =========================================================================================================
// Handle http requests
export function prepareRequest({
	url,
	req_method = "GET",
	data_object = null,
	headers = {},
	others = {},
}) {
	req_method = req_method.toUpperCase();

	// Apply default options if missing
	if (Object.keys(others).length === 0) {
		others = {
			credentials: "same-origin",
			cache: "no-cache",
			mode: "cors",
			redirect: "follow",
			referrerPolicy: "no-referrer",
		};
	}

	// Determine body & headers
	let body = undefined;
	const contentType = (
		headers["Content-Type"] ||
		headers["content-type"] ||
		""
	).toLowerCase();

	if (req_method !== "GET" && req_method !== "HEAD") {
		// Automatically infer encoding
		if (contentType.includes("application/json")) {
			body =
				typeof data_object === "string"
					? data_object
					: JSON.stringify(data_object || {});
		} else if (contentType.includes("application/x-www-form-urlencoded")) {
			body = new URLSearchParams(data_object || {}).toString();
		} else if (data_object instanceof FormData) {
			// FormData: don't override Content-Type — browser sets boundary
			delete headers["Content-Type"];
			delete headers["content-type"];
			body = data_object;
		} else if (contentType.includes("multipart/form-data")) {
			const formData = new FormData();
			for (const [key, value] of Object.entries(data_object || {})) {
				formData.append(key, value);
			}
			delete headers["Content-Type"];
			delete headers["content-type"];
			body = formData;
		} else {
			body = data_object;
		}
	}

	return new Request(url, {
		method: req_method,
		headers,
		body,
		...others,
	});
}

const CACHE_URL_MATCH_RULES = [RegExp("/details|id=")];
const NO_CACHE_URL_MATCH_RULES = [RegExp("/search")];
const FETCHING_URLS = {};
globalThis.FETCHING_URLS = FETCHING_URLS;
const THROTTLE_DURATION_SAME_URL = cache_duration_calc({ milliseconds: 750 });

export async function fetch_url({
	url,
	req_method = "GET",
	data_object = {},
	headers = { "Content-Type": "application/json" },
	others = {},
}) {
	req_method = req_method.toUpperCase();

	// Build the full Request object
	let request = prepareRequest({
		url,
		req_method,
		data_object,
		headers,
		others,
	});
	let request_cpy = request.clone();

	let response = null;
	catchErrorAndLog(showLoadingIndicator);

	// Handle GET caching logic
	if (req_method === "GET") {
		if (
			NO_CACHE_URL_MATCH_RULES.some((rule) => rule.test(url)) ||
			!CACHE_URL_MATCH_RULES.some((rule) => rule.test(url))
		) {
			response = await fetch(request);
		} else {
			if (!API_CACHE) await evict_cache();
			while (FETCHING_URLS[url] === true)
				await sleep(THROTTLE_DURATION_SAME_URL);
			if (FETCHING_URLS[url] === undefined) FETCHING_URLS[url] = true;

			response = await API_CACHE.match(request);
			if (response) {
				FETCHING_URLS[url] += 1;
			} else {
				response = await fetch(request);
				API_CACHE.put(request, response.clone());
				FETCHING_URLS[url] = 1;
			}
		}
	} else {
		// Send non-GET request
		response = await fetch(request);
	}

	catchErrorAndLog(hideLoadingIndicator);

	// Store request/response copies for debugging
	let response_cpy = response.clone();
	window.last_request = request_cpy;
	window.last_response = response_cpy;

	// Show any errors in UI
	let response_content_type = response_cpy.headers.get("content-type") || "";
	if (response_content_type.includes("json")) {
		let json_response = await response_cpy.json();
		let errors = json_response?.errors || json_response?.error;

		if (errors) {
			let errorList = Array.isArray(errors) ? errors : [errors];
			errorList.forEach(async (errorMsg) => {
				let msg = await formatHTTPErrorMessage({
					request: request_cpy,
					response,
					jsonResponse: json_response,
					errorMsg,
				});
				msg = `${msg}Query docs -> https://github.com/Iftakharpy/rivia_soft`
				showMessage(msg);
			});
		}
	} else if (response_cpy.status >= 400) {
		let msg = await formatHTTPErrorResponse({
			request: request_cpy,
			response: response_cpy,
			showRequest: false,
			// showResponse: false,
		});
		showMessage(msg);
	}
	return response;
}

function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

// =========================================================================================================
// propagate http errors to users instead of dropping them silently
export function showMessage(message, message_type_class = "error") {
	let messagesContainer = document.querySelector("[data-messages]");
	let messageElement = document.createElement("pre");
	messageElement.classList.add("message", message_type_class);
	messageElement.innerText = message;
	let style = messageElement.style;
	let newStyles = {
		maxWidth: "100%",
		boxSizing: "border-box",

		// lineBreak: 'anywhere',
		wordWrap: "break-word",
		whiteSpace: "pre-wrap",
		wordBreak: "break-word",
		overflowWrap: "anywhere",
	};
	Object.entries(newStyles).forEach(([key, value]) => {
		style[key] = value;
	});
	messagesContainer.appendChild(messageElement);
}

export async function formatHTTPErrorMessage({
	request: request,
	response: response,
	jsonResponse: jsonResponse,
	errorMsg: errorMsg,
}) {
	let formattedHTTPError = await formatHTTPErrorResponse({
		request,
		response,
		showRequest: false,
		showResponse: false,
	});
	return `${errorMsg}\n\n${formattedHTTPError}`;
}

export async function formatHTTPErrorResponse({ 
	request,
	response,
	showRequest=true,
	showResponse=true
}) {
	if (!(request instanceof Request) || !(response instanceof Response)) {
		return "[Invalid request or response object]";
	}

	// Clone request and response so we can safely read their bodies
	const reqClone = request.clone();
	const resClone = response.clone();

	// Collect request headers
	const reqHeaders = {};
	for (const [key, value] of reqClone.headers.entries()) {
		reqHeaders[key] = value;
	}

	// Collect response headers
	const resHeaders = {};
	for (const [key, value] of resClone.headers.entries()) {
		resHeaders[key] = value;
	}

	// Try reading request body
	let reqBody = "[empty]";
	try {
		const text = await reqClone.text();
		if (text) {
			const contentType = reqClone.headers.get("content-type") || "";
			if (contentType.includes("application/json"))
				reqBody = JSON.parse(text);
			else reqBody = text;
		}
	} catch (e) {
		reqBody = `[unreadable: ${e.message}]`;
	}

	// Try reading response body
	let resBody = "[empty]";
	try {
		const text = await resClone.text();
		if (text) {
			const contentType = resClone.headers.get("content-type") || "";
			if (contentType.includes("application/json"))
				resBody = JSON.parse(text);
			else resBody = text;
		}
	} catch (e) {
		resBody = `[unreadable: ${e.message}]`;
	}

	// Build formatted output
	return `${
		showRequest ? 
		`STATUS: ${reqClone.method} -> ${resClone.status} ${resClone.statusText}
ReqURL: ${decodeURI(reqClone.url)}
ReqBody: ${ typeof reqBody === "object" ? 
				JSON.stringify(reqBody, null, 2) : reqBody
			}`: ''}${showResponse? `RESPONSE: ${typeof resBody === "object" ? JSON.stringify(resBody, null, 2) : resBody}`: ''}`;
}



// =========================================================================================================
// Shows detailed info for debugging
export async function formatHTTPErrorRequestResponse({ request, response }) {
	if (!(request instanceof Request) || !(response instanceof Response)) {
		return "[Invalid request or response object]";
	}

	// Clone request and response so we can safely read their bodies
	const reqClone = request.clone();
	const resClone = response.clone();

	// Collect request headers
	const reqHeaders = {};
	for (const [key, value] of reqClone.headers.entries()) {
		reqHeaders[key] = value;
	}

	// Collect response headers
	const resHeaders = {};
	for (const [key, value] of resClone.headers.entries()) {
		resHeaders[key] = value;
	}

	// Try reading request body
	let reqBody = "[empty]";
	try {
		const text = await reqClone.text();
		if (text) {
			const contentType = reqClone.headers.get("content-type") || "";
			if (contentType.includes("application/json"))
				reqBody = JSON.parse(text);
			else reqBody = text;
		}
	} catch (e) {
		reqBody = `[unreadable: ${e.message}]`;
	}

	// Try reading response body
	let resBody = "[empty]";
	try {
		const text = await resClone.text();
		if (text) {
			const contentType = resClone.headers.get("content-type") || "";
			if (contentType.includes("application/json"))
				resBody = JSON.parse(text);
			else resBody = text;
		}
	} catch (e) {
		resBody = `[unreadable: ${e.message}]`;
	}

	// Build formatted output
	return `
----- HTTP ERROR -----
REQUEST:
  Method: ${reqClone.method}
  URL: ${decodeURI(reqClone.url)}
  Mode: ${reqClone.mode}
  Credentials: ${reqClone.credentials}
  Cache: ${reqClone.cache}
  Redirect: ${reqClone.redirect}
  Referrer: ${reqClone.referrer}
  Headers: ${JSON.stringify(reqHeaders, null, 2)}
  Body: ${
		typeof reqBody === "object" ? JSON.stringify(reqBody, null, 2) : reqBody
  }

RESPONSE:
  Status: ${resClone.status} ${resClone.statusText}
  Headers: ${JSON.stringify(resHeaders, null, 2)}
  Body: ${
		typeof resBody === "object" ? JSON.stringify(resBody, null, 2) : resBody
  }
----------------------
`;
}
