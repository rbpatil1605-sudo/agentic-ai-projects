# Job Finder Agent — Streamlit UI

A simple chatbot UI that connects to the Job Finder Agent running on Cloud Run.

## Local development

### 1. Install dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure .env
```powershell
# Edit .env and set your token
$env:AUTH_TOKEN = (gcloud auth print-identity-token)
```

### 3. Run locally
```powershell
streamlit run app.py
```
Opens at http://localhost:8501

---

## Deploy to Cloud Run

```powershell
cd job_finder_ui
.\deploy.ps1
```

---

## How authentication works

- **Local dev** — paste your token in `.env` as `AUTH_TOKEN`
- **Cloud Run** — use Workload Identity or set `AUTH_TOKEN` as a Cloud Run secret

## Folder structure

```
job_finder_ui/
  app.py            ← Streamlit chatbot UI
  Dockerfile        ← Container for Cloud Run
  requirements.txt  ← streamlit, requests, python-dotenv
  deploy.ps1        ← One-command deploy script
  .env              ← Local config (never commit)
```
