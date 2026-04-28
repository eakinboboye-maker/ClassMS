# Xeus-fixed JupyterLite files

Use these files to replace the broken Xeus/Pyodide-mixed version.

## Replace
- `content/_shared/classlite_jupyter.py`
- `content/EEE355/week01_class_note_xeus_fixed.ipynb`
- `requirements.txt`
- `environment.yml`

## Build
```bash
cd jupyterlite
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lite build --config jupyter_lite_config.json --output-dir dist
rm -f dist/package.json dist/package-lock.json dist/yarn.lock
printf '{\n  "framework": null,\n  "cleanUrls": false\n}\n' > dist/vercel.json
cd dist
vercel --prod
```
