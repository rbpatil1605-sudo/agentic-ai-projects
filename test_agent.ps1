$TOKEN = (gcloud auth print-identity-token)
$APP_URL = "https://job-finder-agent-890743251258.us-central1.run.app"

Write-Host "=== Creating Session ===" -ForegroundColor Cyan
curl.exe -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{}" "$APP_URL/apps/job_finder_agent/users/user_123/sessions/session_abc"

Write-Host "`n=== Running Agent ===" -ForegroundColor Cyan
curl.exe -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "@body.json" "$APP_URL/run_sse"