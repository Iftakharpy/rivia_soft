const messagesContainer = document.querySelector("[data-messages-container]");
const messagesHeader = messagesContainer.querySelector("[data-header]");
const messagesCloseBtn = messagesHeader.querySelector("[data-close-messages]");
const messagesList = messagesContainer.querySelector("[data-messages-list]");

// --- STATE VARIABLES ---
let isDraggingMessages = false;
let initialX;
let initialY;
let xOffset = 0;
let yOffset = 0;
let hasMoved = false;
const storageKey = 'allMessagesContainerPositions';

// --- INITIAL SETUP ---
messagesContainer.style.position = 'fixed';
messagesCloseBtn.addEventListener("click", () => messagesList.textContent = '');

// --- HELPER FUNCTIONS ---

/**
 * Gets a generalized URL key, ignoring numeric segments.
 */
function getGeneralizedUrlKey() {
    const path = window.location.pathname;
    return path.split('/').map(segment => /^\d+$/.test(segment) ? '' : segment).join('/').replace(/\/+/g, '/');
}

/**
 * Calculates the full outer dimensions of an element, including margins.
 */
function getOuterDimensions(el) {
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    const marginLeft = parseFloat(style.marginLeft);
    const marginRight = parseFloat(style.marginRight);
    const marginTop = parseFloat(style.marginTop);
    const marginBottom = parseFloat(style.marginBottom);
    const paddingLeft = parseFloat(style.paddingLeft);
    const paddingRight = parseFloat(style.paddingRight);
    const paddingTop = parseFloat(style.paddingTop);
    const paddingBottom = parseFloat(style.paddingBottom);

    return {
        width: rect.width + marginLeft + marginRight + paddingLeft + paddingRight,
        height: rect.height + marginTop + marginBottom + paddingTop + paddingBottom
    };
}

/**
 * Extracts clientX/clientY from mouse or touch events.
 */
function getEventCoords(e) {
    return e.touches ? { x: e.touches[0].clientX, y: e.touches[0].clientY } : { x: e.clientX, y: e.clientY };
}

/**
 * Calculates the element's position, constrained within the viewport.
 */
function getConstrainedPosition(currentX, currentY) {
    const { width, height } = getOuterDimensions(messagesContainer);
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    const constrainedX = Math.max(0, Math.min(currentX, viewportWidth - width));
    const constrainedY = Math.max(0, Math.min(currentY, viewportHeight - height));

    return { x: constrainedX, y: constrainedY };
}

/**
 * Applies the transform to move the element.
 */
function setTranslate(xPos, yPos, el) {
    el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
}


// --- CORE LOGIC FUNCTIONS ---

/**
 * Checks and corrects the container's position on resize or load.
 */
function constrainToViewport() {
    const { x: correctedX, y: correctedY } = getConstrainedPosition(xOffset, yOffset);

    if (correctedX !== xOffset || correctedY !== yOffset) {
        xOffset = correctedX;
        yOffset = correctedY;
        setTranslate(xOffset, yOffset, messagesContainer);
    }
}

function loadPosition() {
    const allPositionsRaw = localStorage.getItem(storageKey);
    if (!allPositionsRaw) return;

    const allPositions = JSON.parse(allPositionsRaw);
    const currentPageKey = getGeneralizedUrlKey();
    const savedPosition = allPositions[currentPageKey];

    if (savedPosition) {
        xOffset = savedPosition.x;
        yOffset = savedPosition.y;
        setTranslate(xOffset, yOffset, messagesContainer);
        constrainToViewport();
    }
}

function savePosition() {
    if (hasMoved) {
        const allPositionsRaw = localStorage.getItem(storageKey);
        const allPositions = allPositionsRaw ? JSON.parse(allPositionsRaw) : {};
        const currentPageKey = getGeneralizedUrlKey();
        allPositions[currentPageKey] = { x: xOffset, y: yOffset };
        localStorage.setItem(storageKey, JSON.stringify(allPositions));
    }
}

// --- DRAG EVENT HANDLERS ---

function dragStart(e) {
    isDraggingMessages = true;
    hasMoved = false;

    const { x, y } = getEventCoords(e);
    initialX = x - xOffset;
    initialY = y - yOffset;

    messagesHeader.style.cursor = 'grabbing';
}

function dragEnd(e) {
    isDraggingMessages = false;
    messagesHeader.style.cursor = 'grab';
    savePosition();
}

function drag(e) {
    if (!isDraggingMessages) return;

    e.preventDefault();
    hasMoved = true;

    const { x: clientX, y: clientY } = getEventCoords(e);
    const currentX = clientX - initialX;
    const currentY = clientY - initialY;

    // Use the helper to get the corrected position
    const constrainedPos = getConstrainedPosition(currentX, currentY);
    xOffset = constrainedPos.x;
    yOffset = constrainedPos.y;

    setTranslate(xOffset, yOffset, messagesContainer);
}

// --- EVENT LISTENERS ---

// Mouse events
messagesHeader.addEventListener('mousedown', dragStart);
addEventListener('mouseup', dragEnd);
addEventListener('mousemove', drag);

// Touch events
messagesHeader.addEventListener('touchstart', dragStart);
addEventListener('touchend', dragEnd);
addEventListener('touchmove', drag, { passive: false });

// Viewport resize event
addEventListener('resize', constrainToViewport);

// --- INITIALIZATION ---
loadPosition();
