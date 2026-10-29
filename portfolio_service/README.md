# InvestEdge AI Market Intelligence — AI API service

This folder adds a separate, configurable AI API without replacing the repository's existing application.

## Features

- OpenAI-compatible chat-completions integration
- Configurable provider URL and model
- Protected analysis endpoint using a service key
- Input length checks and safe error handling
- Unit tests, Docker image, and GitHub Actions CI

## Configure

Set these environment variables in your local terminal or deployment platform:

- `AI_API_KEY`: your provider's secret key
- `AI_BASE_URL`: provider API base URL (default: `https://api.deepseek.com`)
- `AI_MODEL`: model name (default: `deepseek-chat`)
- `PORTFOLIO_SERVICE_KEY`: a long, random secret for clients calling this API

For OpenAI, use `AI_BASE_URL=https://api.openai.com/v1` and set an appropriate model. For a local Ollama OpenAI-compatible endpoint, use `AI_BASE_URL=http://localhost:11434/v1` and a model available locally. Provider compatibility varies.

## Run locally

From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:AI_API_KEY = "YOUR_PROVIDER_KEY"
$env:PORTFOLIO_SERVICE_KEY = "YOUR_LONG_RANDOM_SERVICE_SECRET"
uvicorn api:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation. Health check: `GET /health`.

## Call the API

```powershell
$headers = @{
  "X-Service-Key" = $env:PORTFOLIO_SERVICE_KEY
}
$body = @{
  text = "Analyze the following request..."
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/v1/analyze" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

## Test

```powershell
python -m unittest discover -s tests -v
```

## Docker

From this folder:

```powershell
docker build -t portfolio-ai-service .
docker run --rm -p 8000:8000 `
  -e AI_API_KEY `
  -e AI_BASE_URL `
  -e AI_MODEL `
  -e PORTFOLIO_SERVICE_KEY `
  portfolio-ai-service
```

## Deployment

The service can be deployed to a container host such as Render, Railway, or another Docker-compatible platform. Configure all secrets as platform environment variables. Do not bake secrets into the image or source code. Add usage limits, monitoring, HTTPS, and provider billing controls before exposing it publicly.

## Limitations

This is an extensible portfolio service, not a claim of production certification. Model responses can be wrong, and the provider may incur costs. The service key is a simple shared-secret gate, not a full identity system.
