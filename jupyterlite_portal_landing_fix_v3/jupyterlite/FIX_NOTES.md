# ClassLite JupyterLite portal landing fix v2

## Problem fixed

`/lab/index.html` failed with:

```text
config-utils.js:183 TypeError: Cannot read properties of null (reading 'textContent')
```

The cause was the root `/index.html` redirect page. JupyterLite's Lab startup reads `/lab/index.html` **and also fetches parent `/index.html`** to merge config. The root redirect page had no:

```html
<script id="jupyter-config-data" type="application/json">...</script>
```

So JupyterLite found `null` and crashed.

## What changed

- `/` still redirects to `/portal/index.html`.
- The root `dist/index.html` now keeps a valid `jupyter-config-data` script tag so Lab can parse config.
- Portal is copied to `dist/portal/index.html`.
- Portal launches Lab using `../lab/index.html` from inside `/portal/`.
- `jupyter_lite_config.json` only uses `content` as JupyterLite notebook content; portal files are copied separately after build.
- Optional client-side Lab guard redirects direct `/lab/index.html` visits to the portal if no `classlite_portal_session` token exists.

## Rebuild

```bash
npm run clean
npm run build
python -m http.server 9000 -d dist
```

Open:

```text
http://localhost:9000/
```

Expected flow:

```text
/ -> /portal/index.html -> login -> /lab/index.html?path=EEE355/...
```

## v3 bridge fix

The notebook no longer assumes `from js import window` works. Xeus Python can run in a WebWorker/WASM context where `window` is not available from Python. The notebook now uses a small `anywidget` browser bridge:

1. Run the first setup cell. It displays `ClassLite portal bridge ready`.
2. Run the next cell: `lesson.bootstrap_from_portal()`.

`anywidget` was added to `environment.yml`.
