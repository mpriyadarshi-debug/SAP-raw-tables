import requests, time

CELONIS_URL = "https://peech-partner-sandbox.us-1.celonis.cloud"
POOL_ID     = "6239346b-bf8c-4c67-9ee8-a54192b3d151"
API_TOKEN   = "NzYwODk4YTktODIwNS00MTE2LTk0ZjQtMDAwOWU5MmZhOTIzOmlWSkxMSFF1MjcyOUxEbVB3MkMxcmFGTm9LMWpvOTRhaXFQZzkzbWd4RkZz"
GITHUB_RAW  = "https://raw.githubusercontent.com/mpriyadarshi-debug/SAP-raw-tables/main"
BASE        = CELONIS_URL + "/integration/api/v1/data-push/" + POOL_ID
HEADERS     = {"Authorization": "AppKey " + API_TOKEN}

TABLES = ["EBAN","EKKO","EKPO","EKET","EKBE","RBKP","RSEG","BKPF","BSEG","CDHDR","CDPOS","VBAK","VBAP","VBEP","VBUK","VBUP","VBKD","VBFA","LIKP","LIPS","VTTK","VTTP","VBRK","VBRP","BKPF_AR","BSEG_AR","BSID","JCDS","NAST","MKPF","MSEG","MARDH","MBEWH","MARA","MAKT","MARC","MARD","MBEW","LFA1","LFB1","KNA1","KNB1","ADRP","T001","T001W","T001K","T001L","T006","T006D","T023T","T134T","T156","T156T","T003T","T005T","T024E","T161T","TVAKT","TVAPT","TVKOT","TVLST","TCURR","TCURF","TCURX","USR02","MARM","TVAGT","TVTWT"]

ok=0; fail=0
print("Pushing " + str(len(TABLES)) + " tables...\n")

for table in TABLES:
    try:
        r = requests.get(GITHUB_RAW + "/" + table + ".csv", timeout=30)
        if r.status_code != 200:
            print("  X " + table + ": GitHub " + str(r.status_code)); fail+=1; continue

        job = requests.post(BASE + "/jobs", headers=HEADERS, json={"dataPoolId":POOL_ID,"targetName":table,"type":"REPLACE","csvParsingOptions":{"columnSeparator":",","quoteChar":"\"","header":True}})
        if job.status_code not in (200,201):
            print("  X " + table + " job: " + str(job.status_code) + " " + job.text[:150]); fail+=1; continue
        job_id = job.json().get("id") or job.json().get("jobId")

        chunk = requests.post(BASE + "/jobs/" + job_id + "/chunks/upserted", headers=dict(list(HEADERS.items()) + [("Content-Type","text/csv")]), data=r.content)
        if chunk.status_code not in (200,201,204):
            print("  X " + table + " chunk: " + str(chunk.status_code) + " " + chunk.text[:150]); fail+=1; continue

        exe = requests.post(BASE + "/jobs/" + job_id, headers=HEADERS)
        rows = len(r.content.decode("utf-8").strip().split("\n")) - 1
        if exe.status_code in (200,201,204):
            print("  OK " + table.ljust(15) + str(rows).rjust(6) + " rows"); ok+=1
        else:
            print("  X " + table + " execute: " + str(exe.status_code) + " " + exe.text[:150]); fail+=1
        time.sleep(0.5)
    except Exception as e:
        print("  X " + table + ": " + str(e)); fail+=1

print("\nDone: " + str(ok) + " OK, " + str(fail) + " failed")
