function getFormData(form) {
	let data = {};
	Array.from(form.elements).forEach((element) => {
		if (["button", "submit"].includes(element.type)) return;

		let value = null;
		if (element.type == "checkbox") {
			value = element.checked;
		} else if (element.type == "select-multiple") {
			let selectedOptions = [];
			Array.from(element.selectedOptions).forEach((op) =>
				selectedOptions.push(op.value)
			);
			value = selectedOptions;
		} else {
			value = element.value;
		}
		data[element.name] = value;
		// console.log(
		// 	`(${element.type})${element.name}=${data[element.name]} : ${element}`
		// );
	});
	return JSON.stringify(data);
}

let oldFormRef = document.querySelector("form");
const formDataSnapshots = {
	initial: getFormData(document.querySelector("form")),
	latest: getFormData(document.querySelector("form")),
	isSubmitClicked: false,
};
const setIsSubmitClicked = (ev) => {
	formDataSnapshots.isSubmitClicked = true;
};
const unsetIsSubmitClicked = (ev) => {
	formDataSnapshots.isSubmitClicked = false;
};
Array.from(document.querySelectorAll("a")).forEach((a) =>
	a.addEventListener("click", unsetIsSubmitClicked)
);

let eventNames = ["click", "keyup"];
eventNames.forEach((ev) => {
	document.addEventListener(ev, (e) => {
		if (ev == "click" && e.target.type == "submit") {
			formDataSnapshots.isSubmitClicked = true;
		}
		formDataSnapshots.latest = getFormData(document.querySelector("form"));
	});

	// needed because when the form attribute changes the reference to
	// old form is useless
	let newFormRef = document.querySelector("form");
	if (oldFormRef != newFormRef) {
		oldFormRef = newFormRef;
		oldFormRef.removeEventListener("submit", setIsSubmitClicked);
		newFormRef.addEventListener("submit", setIsSubmitClicked);
	}
});
window.addEventListener("beforeunload", (e) => {
	let wasFormEdited = formDataSnapshots.initial != formDataSnapshots.latest;
	if (wasFormEdited && !formDataSnapshots.isSubmitClicked) e.preventDefault();
});
