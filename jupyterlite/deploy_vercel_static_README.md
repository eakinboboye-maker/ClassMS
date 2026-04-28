# deploy_vercel_static.sh

This script updates the JupyterLite site on Vercel from localhost by uploading the already-built `dist/` folder.

## Why this version

Use this when Vercel's hosted build fails and you want Vercel to behave as a static host only.

## Normal production deploy

```bash
bash deploy_vercel_static.sh
```

## Preview deploy

```bash
PROD=false bash deploy_vercel_static.sh
```

## Skip content sync

```bash
SKIP_SYNC=true bash deploy_vercel_static.sh
```

## Skip local build

```bash
SKIP_LOCAL_BUILD=true bash deploy_vercel_static.sh
```

## Recommended workflow

```bash
python scripts/sync_course_content.py
jupyter lite build --config jupyter_lite_config.json --output-dir dist
vercel dist --prod
```
