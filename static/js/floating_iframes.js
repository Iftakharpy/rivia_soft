const keyPressStack = []
document.addEventListener("keydown", (e) => {
	const IFRAMES_CONTAINER = document.querySelector("[data-iframes-container]");

	if (!(e.target==document.body)) return // avoid messing with text inputs

	let shouldShow = false
	if (["Escape", "h", "H", "q", "Q"].includes(e.key)) { 
		shouldShow = false
	} else if (["s", "S", "f", "F"].includes(e.key)) { 
		shouldShow = true && IFRAMES_CONTAINER.classList.contains("hidden")
	}

	if (shouldShow) IFRAMES_CONTAINER.classList.remove("hidden"); // show iframes
	else IFRAMES_CONTAINER.classList.add("hidden"); // hide iframes
});

document.addEventListener("contextmenu", (e) => {
	let anchor = getElementOrAncestorMatching(e.target, (e)=>e.tagName=='A')
	if (anchor && !(e.shiftKey||e.ctrlKey||e.altKey)) e.preventDefault();
	
	console.log("menu", e, e.target);
});


/**
 * Recursively checks whether the given element or any of its ancestor elements
 * satisfies a specified condition.
 *
 * @param {HTMLElement | null} element - The DOM element to start checking from.
 * @param {(el: HTMLElement) => boolean} callback - A function that receives each element
 *     (starting from the element itself, then moving up the DOM tree)
 *     and should return `true` if the condition is met (e.g., checking if it has a certain class or ID).
 * @returns {boolean} `true` if the element itself or any of its ancestors
 *     satisfies the callback condition, otherwise `false`.
 *
 * @example
 * // Check if an element or any of its parents has the class "container"
 * const isInContainer = getElementOrAncestorMatching(someElement, el => el.classList.contains("container"));
 * console.log(isInContainer); // true or false
 */
function getElementOrAncestorMatching(element, callback) {
	if (element == null) return false;
	if (callback(element)) return true;
	return getElementOrAncestorMatching(element.parentElement, callback);
}
