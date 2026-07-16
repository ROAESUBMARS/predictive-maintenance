# How to Deploy — Step by Step (Render or Vercel)

## Step 1 — Create a GitHub account
Go to https://github.com and sign up (free).

## Step 2 — Create a new GitHub repository
1. Click the **+** button at the top right
2. Click **New repository**
3. Name it: `predictive-maintenance`
4. Make it **Public**
5. Click **Create repository**

## Step 3 — Upload your project files
Upload all project files into the repository, **excluding any `.env` file**:
- `app.py`
- `index.html`
- `requirements.txt`
- `Procfile`
- `runtime.txt`
- `vercel.json`
- `saved_model.pkl`
- `static/` (containing `script.js` and `style.css`)
- `predictive_maintenance_dataset.csv`
- `maintenance_scheduler.py`, `ai_recommendation.py`, `alert_service.py`

> [!WARNING]
> Do NOT upload the `.env` file or any file containing plaintext credentials (like passwords or API keys) to your public GitHub repository. The `.env` file is ignored by default via `.gitignore`.

To upload: click **Add file → Upload files** on GitHub, drag the allowed files in, and click **Commit changes**.

---

## Option A — Deploy on Render (Web Service)

### 1. Create a Render account
Go to https://render.com and sign up with your GitHub account (free).

### 2. Deploy the Web Service
1. On the Render dashboard, click **New → Web Service**
2. Connect your GitHub repository
3. Fill in the settings:
   - **Name:** `predictive-maintenance`
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan:** `Free`

### 3. Configure Render Environment Variables (CRITICAL)
1. In your Render Web Service dashboard, navigate to the **Environment** tab.
2. Click **Add Environment Variable** and enter the variables listed in the **Common Environment Variables** section below.
3. Click **Save Changes** to trigger a fresh secure rebuild.

---

## Option B — Deploy on Vercel (Serverless)

Vercel is optimized for serverless deployments. The project is pre-configured with a `vercel.json` configuration mapping the Flask server to Vercel's Python Serverless Functions runtime.

### 1. Create a Vercel account
Go to https://vercel.com and sign up with your GitHub account (free).

### 2. Deploy the Project
1. On the Vercel dashboard, click **Add New → Project**
2. Import your `predictive-maintenance` repository from GitHub.
3. Keep the defaults for **Framework Preset** (Other).
4. Expand the **Environment Variables** section.
5. Add the environment variables listed in the **Common Environment Variables** section below.
6. Click **Deploy**.
7. Vercel will install the requirements from `requirements.txt`, bundle the serverless functions, and generate your live deployment link.

---

## Common Environment Variables (CRITICAL FOR SECURITY)

Regardless of whether you choose Render or Vercel, you **must** configure these environment variables in your deployment dashboard settings.

| Key | Value | Description |
| :--- | :--- | :--- |
| `FLASK_SECRET_KEY` | `[Secure Random String]` | **(Required)** Cryptographic key used to sign session tokens. Generating a random string (e.g. 32 hex chars) prevents token spoofing. |
| `API_PASSWORD` | `[Your Secure Password]` | **(Required)** Secure password for technician/engineer login. Do not use default passwords like `admin` in production. |
| `ALLOWED_CORS_ORIGINS` | `https://your-app-url.onrender.com` or `https://your-app.vercel.app` | **(Required)** Restricts backend access to your frontend web client origin. |
| `DEV_BYPASS_TOKEN` | `[Secure Development Key]` | *(Optional)* Dedicated key for automated testing bypass. Keep unset in production to fully secure endpoints. |
| `GEMINI_API_KEY` | `[Your Gemini API Key]` | *(Optional)* Required to enable Google Generative AI diagnostic suggestions. |
| `AZURE_OPENAI_API_KEY` | `[Your Azure API Key]` | *(Optional)* Required to enable Azure OpenAI fallback diagnostic suggestions. |

---

## Important note about free plans & limitations

1. **Render Free Plan Inactivity:** Render's free plan "sleeps" after 15 minutes of inactivity. Vercel, being serverless, does not go to sleep, but has a slight "cold start" latency (~1-2 seconds) on initial requests.
2. **Ephemeral/Read-Only Filesystem:** Both Render's free tier (ephemeral) and Vercel's serverless functions (read-only) do not support persistent local file modifications. Never save configurations or modifications directly to disk. Always manage configurations using the dashboard environment variable panels.
3. **Dynamic Settings Dashboard Configurator:** The dashboard's "Settings" setup page attempts to write non-sensitive variables directly to a local `.env` file via the `/api/config` POST endpoint. Since production server filesystems are read-only or ephemeral, this API endpoint will return a clear error in production. You **must** manage all configurations and API keys directly inside your hosting platform's environment variables configuration dashboard (Render Web Service Settings or Vercel Project Environment Variables).
4. **In-Memory Rate Limiting Limitation:** The backend utilizes an in-memory rate limiter (`_rate_limit_records`) to prevent API abuse. In serverless environments (like Vercel) or multi-worker production configurations (like Render with multiple Gunicorn workers), this memory state is isolated to each independent container/process and resets constantly. As a result, rate limits are not shared across separate instances or cold-start functions and cannot be fully enforced in these architectures. For strict enforcement in production, a persistent database/cache store (like Redis) or an API Gateway should be configured.
