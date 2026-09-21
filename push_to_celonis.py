"""
Push all 65 SAP ECC CSV tables from GitHub → Celonis Data Pool
Uses Celonis Data Push API (the simplest, most reliable method for CSV files)

Usage:
  1. Fill in your CELONIS_URL, POOL_ID, API_TOKEN below
  2. Run: python push_to_celonis.py
  3. All 65 tables appear in your pool — done.

Future updates:
  After any patch, just run this script again.
  TRUNCATE_AND_INSERT replaces old data cleanly.
"""

import requests
import time

# ── CONFIG — fill these in ────────────────────────────────────────────────────
CELONIS_URL = "https://peech-partner-sandbox.us-1.celonis.cloud"
POOL_ID     = "6239346b-bf8c-4c67-9ee8-a54192b3d151"
API_TOKEN   = "YOUR_API_TOKEN_HERE"   # paste your token here

GITHUB_RAW  = "https://raw.githubusercontent.com/mpriyadarshi-debug/SAP-raw-tables/main"
# ─────────────────────────────────────────────────────────────────────────────

TABLES = [
    # P2P
    "EBAN","EKKO","EKPO","EKET","EKBE",
    "RBKP","RSEG","BKPF","BSEG","CDHDR","CDPOS",
    # O2C
    "VBAK","VBAP","VBEP","VBUK","VBUP","VBKD","VBFA",
    "LIKP","LIPS","VTTK","VTTP",
    "VBRK","VBRP","BKPF_AR","BSEG_AR","BSID",
    "JCDS","NAST",
    # Inventory
    "MKPF","MSEG","MARDH","MBEWH",
    # Master Data
    "MARA","MAKT","MARC","MARD","MBEW",
    "LFA1","LFB1","KNA1","KNB1","ADRP",
    # Config
    "T001","T001W","T001K","T001L",
    "T006","T006D","T023T","T134T","T156","T156T","T003T",
    "T005T","T024E","T161T",
    "TVAKT","TVAPT","TVKOT","TVLST",
    "TCURR","TCURF","TCURX","USR02",
]

HEADERS = {
    "Authorization": f"AppKey {API_TOKEN}",
    "Content-Type":  "application/json",
}

def get_or_create_job():
    """Create a new data push job for the pool."""
    url = f"{CELONIS_URL}/integration/api/v1/data-push/{POOL_ID}/jobs"
    resp = requests.post(url, headers=HEADERS, json={})
    if resp.status_code in (200, 201):
        job_id = resp.json().get("id") or resp.json().get("jobId")
        print(f"  ✅ Push job created: {job_id}")
        return job_id
    else:
        print(f"  ❌ Failed to create job: {resp.status_code} {resp.text}")
        return None

def push_table(table_name):
    """Fetch CSV from GitHub and push to Celonis."""
    # Step 1: fetch CSV from GitHub
    csv_url = f"{GITHUB_RAW}/{table_name}.csv"
    r = requests.get(csv_url, timeout=30)
    if r.status_code != 200:
        print(f"  ❌ {table_name}: GitHub fetch failed ({r.status_code})")
        return False
    csv_content = r.content

    # Step 2: push to Celonis using upsert endpoint
    push_url = (
        f"{CELONIS_URL}/integration/api/v1/data-push/{POOL_ID}"
        f"/tables/{table_name}/rows"
    )
    push_headers = {
        "Authorization": f"AppKey {API_TOKEN}",
        "Content-Type": "text/csv",
        "upsertStrategy": "TRUNCATE_AND_INSERT",
    }
    resp = requests.post(push_url, headers=push_headers, data=csv_content, timeout=60)

    if resp.status_code in (200, 201, 204):
        rows = len(csv_content.decode("utf-8").strip().split("\n")) - 1
        print(f"  ✅ {table_name:<15} {rows:>5} rows pushed")
        return True
    else:
        print(f"  ❌ {table_name:<15} FAILED: {resp.status_code} — {resp.text[:120]}")
        return False

def commit_job(job_id):
    """Commit the push job so Celonis applies all changes."""
    url = f"{CELONIS_URL}/integration/api/v1/data-push/{POOL_ID}/jobs/{job_id}/upsert"
    resp = requests.post(url, headers=HEADERS, json={})
    if resp.status_code in (200,201,204):
        print(f"\n  ✅ Job committed — tables now live in Celonis pool")
    else:
        print(f"\n  ⚠️  Commit response: {resp.status_code} {resp.text[:200]}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Celonis Data Push — 65 SAP ECC Tables")
    print("=" * 55)

    if API_TOKEN == "YOUR_API_TOKEN_HERE":
        print("\n❌ Please fill in your API_TOKEN before running.")
        exit(1)

    ok = 0; fail = 0
    start = time.time()

    print(f"\nPushing {len(TABLES)} tables to pool {POOL_ID[:8]}...\n")

    for table in TABLES:
        success = push_table(table)
        if success: ok += 1
        else: fail += 1
        time.sleep(0.3)   # gentle rate limiting

    elapsed = round(time.time() - start, 1)
    print(f"\n{'='*55}")
    print(f"  Done in {elapsed}s — {ok} succeeded, {fail} failed")
    if ok == len(TABLES):
        print(f"  ✅ All {len(TABLES)} tables loaded into Celonis")
    print(f"{'='*55}")
