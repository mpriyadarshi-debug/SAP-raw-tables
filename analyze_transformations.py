"""
Celonis Transformation Analyzer
Connects to your pool, pulls all transformation scripts,
extracts every table and column referenced, and compares
against the CSVs you've uploaded.
"""
import requests, re, json, csv, os
from collections import defaultdict

CELONIS_URL = "https://peech-partner-sandbox.us-1.celonis.cloud"
POOL_ID     = "6239346b-bf8c-4c67-9ee8-a54192b3d151"
API_TOKEN   = "NzYwODk4YTktODIwNS00MTE2LTk0ZjQtMDAwOWU5MmZhOTIzOmlWSkxMSFF1MjcyOUxEbVB3MkMxcmFGTm9LMWpvOTRhaXFQZzkzbWd4RkZz"
HEADERS     = {"Authorization": "AppKey " + API_TOKEN, "Content-Type": "application/json"}

print("=" * 60)
print("Celonis Transformation Analyzer")
print("Pool: OCPM Extractions SAP ECC Order Management (1)")
print("=" * 60)

# ── Step 1: Get all data models in the pool ──────────────────
print("\n[1] Fetching data models...")
r = requests.get(f"{CELONIS_URL}/integration/api/v1/pools/{POOL_ID}/data-models", headers=HEADERS)
if r.status_code != 200:
    # Try alternate path
    r = requests.get(f"{CELONIS_URL}/integration/api/v2/pools/{POOL_ID}/data-models", headers=HEADERS)
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    models = r.json()
    print(f"    Found {len(models) if isinstance(models, list) else 'N/A'} data models")
    print(json.dumps(models, indent=2)[:1000])
else:
    print(f"    Response: {r.text[:300]}")

# ── Step 2: Get transformations ───────────────────────────────
print("\n[2] Fetching transformations...")
for path in [
    f"/integration/api/v1/pools/{POOL_ID}/transformations",
    f"/integration/api/v2/pools/{POOL_ID}/transformations",
    f"/integration/api/v1/data-push/{POOL_ID}/transformations",
]:
    r = requests.get(CELONIS_URL + path, headers=HEADERS)
    print(f"    {r.status_code} {path}")
    if r.status_code == 200:
        print(f"    Got data: {r.text[:500]}")
        break

# ── Step 3: Try the data model endpoint to get tables ────────
print("\n[3] Fetching pool overview / tables...")
for path in [
    f"/integration/api/v1/pools/{POOL_ID}",
    f"/integration/api/v2/pools/{POOL_ID}",
    f"/integration/api/v1/pools/{POOL_ID}/tables",
    f"/integration/api/v1/pools/{POOL_ID}/data-connections",
]:
    r = requests.get(CELONIS_URL + path, headers=HEADERS)
    print(f"    {r.status_code} {path}")
    if r.status_code == 200:
        print(f"    Response: {r.text[:800]}")
        break

# ── Step 4: Studio API — find packages/analyses for this pool ──
print("\n[4] Searching Studio for analyses linked to this pool...")
for path in [
    "/studio/api/v2/spaces",
    "/api/v1/spaces",
    "/apps/api/v1/spaces",
]:
    r = requests.get(CELONIS_URL + path, headers=HEADERS)
    print(f"    {r.status_code} {path}")
    if r.status_code == 200:
        print(f"    Response: {r.text[:500]}")
        break

print("\n[5] Raw pool info dump...")
r = requests.get(f"{CELONIS_URL}/integration/api/v1/pools", headers=HEADERS)
print(f"    /pools list status: {r.status_code}")
if r.status_code == 200:
    print(r.text[:2000])
else:
    print(r.text[:300])
