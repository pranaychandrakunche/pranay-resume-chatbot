# Azure deployment

Recommended split:

| Piece | Azure service | Why |
|-------|---------------|-----|
| FastAPI + LangGraph | **Azure App Service** (Linux, Docker) | Simple, supports env vars / Key Vault |
| React UI | **Azure Static Web Apps** | Free tier, global CDN, easy GitHub deploy |

## Prerequisites

- Azure CLI (`az login`)
- Docker Desktop
- OpenAI API key in Azure App Settings (never bake into git)
- Resource group, e.g. `rg-pranay-chatbot`

## 1. Backend — Azure App Service (Docker)

```bash
# Variables
RG=rg-pranay-chatbot
LOC=centralindia
ACR=pranaychatbotacr
APP=pranay-resume-api
PLAN=plan-pranay-chatbot

az group create -n $RG -l $LOC

az acr create -n $ACR -g $RG --sku Basic --admin-enabled true

az acr build -r $ACR -t pranay-resume-api:latest -f Dockerfile .

az appservice plan create -n $PLAN -g $RG --is-linux --sku B1

az webapp create -n $APP -g $RG -p $PLAN \
  --container-image-name $ACR.azurecr.io/pranay-resume-api:latest

# Wire ACR credentials
ACR_USER=$(az acr credential show -n $ACR --query username -o tsv)
ACR_PASS=$(az acr credential show -n $ACR --query passwords[0].value -o tsv)
az webapp config container set -n $APP -g $RG \
  --docker-custom-image-name $ACR.azurecr.io/pranay-resume-api:latest \
  --docker-registry-server-url https://$ACR.azurecr.io \
  --docker-registry-server-user $ACR_USER \
  --docker-registry-server-password $ACR_PASS

# App settings (replace key + frontend origin after Static Web App exists)
az webapp config appsettings set -n $APP -g $RG --settings \
  OPENAI_API_KEY="YOUR_KEY" \
  OPENAI_MODEL="gpt-4o-mini" \
  OPENAI_EMBEDDING_MODEL="text-embedding-3-small" \
  APP_ENV="azure" \
  CORS_ORIGINS="https://YOUR_STATIC_APP.azurestaticapps.net" \
  WEBSITES_PORT=8000

az webapp restart -n $APP -g $RG
```

API URL: `https://<APP>.azurewebsites.net`

## 2. Frontend — Azure Static Web Apps

1. Push this repo to GitHub.
2. In Azure Portal → Static Web Apps → Create.
3. Connect the repo; set:
   - App location: `frontend`
   - Output location: `dist`
   - Build: `npm run build` (default for Vite)
4. Add application setting:
   - `VITE_API_URL` = `https://<APP>.azurewebsites.net`

Or use SWA CLI:

```bash
cd frontend
npm run build
npx @azure/static-web-apps-cli deploy ./dist \
  --deployment-token <TOKEN> \
  --env production
```

## 3. CORS

After you have both URLs, set backend `CORS_ORIGINS` to the Static Web App URL (no trailing slash), then restart the App Service.

## 4. First request note

If the Docker image was built **without** `OPENAI_API_KEY`, the API rebuilds the FAISS index on first startup using the App Setting key (takes ~10–30s once).
