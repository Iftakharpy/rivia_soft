const fetch_url = (await import('/static/js/fetch_data.js')).fetch_url;
const marked = (await import('/static/js/marked/marked.esm.js'));

class GitHubDocsWindow extends HTMLElement {
  static observedAttributes = ["src"];

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._loaded = false;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          all: initial;
          position: fixed;
          top: 80px;
          left: 40px;
          width: 720px;
          height: 70vh;
          z-index: 99999;
          font-family: system-ui, sans-serif;
          display: none;
          user-select: none;
        }
        *, *::before, *::after { box-sizing: border-box; }

        .window {
          display: flex;
          flex-direction: column;
          width: 100%;
          height: 100%;
          background: var(--bg);
          color: var(--fg);
          border-radius: 10px;
          box-shadow: 0 20px 40px rgba(0,0,0,0.25);
          overflow: hidden;
          position: relative;
        }

        .titlebar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px 14px;
          background: var(--title-bg);
          border-bottom: 1px solid var(--border);
          cursor: move;
        }

        .title { font-size: 14px; font-weight: 600; }

        button { background: none; border: none; cursor: pointer; font-size: 16px; color: inherit; }

        .content {
          flex: 1;
          padding: 16px;
          overflow: auto;
        }

        pre { background: var(--code-bg); padding: 12px; border-radius: 6px; overflow-x: auto; }
        code { background: var(--code-bg); padding: 2px 4px; border-radius: 4px; font-family: ui-monospace, monospace; }
        a { color: var(--link); text-decoration: none; }
        a:hover { text-decoration: underline; }

        :host { --bg: #ffffff; --fg: #24292f; --title-bg: #f6f8fa; --border: #d0d7de; --code-bg: #f6f8fa; --link: #0969da; }

        @media (prefers-color-scheme: dark) {
          :host { --bg: #0d1117; --fg: #c9d1d9; --title-bg: #161b22; --border: #30363d; --code-bg: #161b22; --link: #58a6ff; }
        }

        .resize-handle {
          position: absolute;
          width: 16px;
          height: 16px;
          bottom: 0;
          right: 0;
          cursor: se-resize;
          background: transparent;
        }
      </style>

      <div class="window" role="dialog" aria-modal="true">
        <div class="titlebar">
          <div class="title">Documentation</div>
          <div>
            <button class="close" title="Close">✕</button>
          </div>
        </div>
        <div class="content">Loading…</div>
        <div class="resize-handle"></div>
      </div>
    `;

    this.contentEl = this.shadowRoot.querySelector(".content");
    this.closeBtn = this.shadowRoot.querySelector(".close");
    this.titlebar = this.shadowRoot.querySelector(".titlebar");
    this.resizeHandle = this.shadowRoot.querySelector(".resize-handle");

    this._restorePosition();
    this._initEvents();
  }

  connectedCallback() {
    if (this.hasAttribute("open-on-load")) this.open();

    if (!window._githubDocsKeyboardListenerRegistered) {
      window.addEventListener("keydown", e => {
        const tag = e.target.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || e.target.isContentEditable) return;

        document.querySelectorAll("github-docs-window").forEach(win => {
          if (!win.isConnected) return;
          if (e.key === "?") win.toggle();
          if (e.key === "Escape") if (win.style.display !== "none") win.close();
        });
      });
      window._githubDocsKeyboardListenerRegistered = true;
    }
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (name === "src" && newVal && this._loaded) this._loadMarkdown();
  }

  get src() { return this.getAttribute("src"); }

  async _loadMarkdown() {
    if (!this.src) return;
    this.contentEl.textContent = "Loading…";
    const res = await fetch_url({ url: this.src, headers: {} });
    const markdown = await res.text();
    this.contentEl.innerHTML = marked.parse(markdown);
    this._loaded = true;
  }

  open() {
    if (!this._loaded) this._loadMarkdown();
    this.style.display = "block";
  }

  close() { this.style.display = "none"; }
  toggle() { this.style.display === "none" ? this.open() : this.close(); }

  _restorePosition() {
    const key = `docs-pos-${this.id || btoa(this.src || "default")}`;
    const saved = JSON.parse(localStorage.getItem(key) || "null");
    if (saved) {
      this.style.left = saved.left;
      this.style.top = saved.top;
      this.style.width = saved.width;
      this.style.height = saved.height;
    }
  }

  _savePosition() {
    const key = `docs-pos-${this.id || btoa(this.src || "default")}`;
    localStorage.setItem(key, JSON.stringify({
      left: this.style.left,
      top: this.style.top,
      width: this.style.width,
      height: this.style.height
    }));
  }

  _initEvents() {
    this.closeBtn.addEventListener("click", () => this.close());

    // Drag window
    let dragging = false, sx, sy, sl, st;
    this.titlebar.addEventListener("mousedown", e => {
      dragging = true;
      sx = e.clientX; sy = e.clientY;
      const r = this.getBoundingClientRect(); sl = r.left; st = r.top;
      e.preventDefault();
    });
    document.addEventListener("mousemove", e => {
      if (!dragging) return;
      this.style.left = sl + (e.clientX - sx) + "px";
      this.style.top = st + (e.clientY - sy) + "px";
    });
    document.addEventListener("mouseup", () => {
      if (dragging) this._savePosition();
      dragging = false;
    });

    // Resize window
    let resizing = false, rsx, rsy, rw, rh;
    this.resizeHandle.addEventListener("mousedown", e => {
      resizing = true;
      rsx = e.clientX; rsy = e.clientY;
      rw = this.getBoundingClientRect().width;
      rh = this.getBoundingClientRect().height;
      e.preventDefault();
    });
    document.addEventListener("mousemove", e => {
      if (!resizing) return;
      const newWidth = Math.max(300, rw + (e.clientX - rsx));
      const newHeight = Math.max(200, rh + (e.clientY - rsy));
      this.style.width = newWidth + "px";
      this.style.height = newHeight + "px";
    });
    document.addEventListener("mouseup", () => {
      if (resizing) this._savePosition();
      resizing = false;
    });
  }
}

customElements.define("github-docs-window", GitHubDocsWindow);
