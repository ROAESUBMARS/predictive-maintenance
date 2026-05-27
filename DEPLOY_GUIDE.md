# How to Deploy on Render (Free) — Step by Step

## Step 1 — Create a GitHub account
Go to https://github.com and sign up (free).

## Step 2 — Create a new GitHub repository
1. Click the **+** button at the top right
2. Click **New repository**
3. Name it: `predictive-maintenance`
4. Make it **Public**
5. Click **Create repository**

## Step 3 — Upload your project files
Upload ALL these files into the repository:
- app.py
- dashboard.html
- requirements.txt
- Procfile
- runtime.txt
- saved_model.pkl

To upload: click **Add file → Upload files** on GitHub, drag all files in, click **Commit changes**.

## Step 4 — Create a Render account
Go to https://render.com and sign up with your GitHub account (free).

## Step 5 — Deploy the backend (Flask API)
1. On Render dashboard, click **New → Web Service**
2. Connect your GitHub repository
3. Fill in the settings:
   - **Name:** predictive-maintenance-api
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
4. Click **Create Web Service**
5. Wait 2-3 minutes for it to build
6. Render gives you a URL like: `https://predictive-maintenance-api.onrender.com`

## Step 6 — Update the dashboard
Open `dashboard.html` in Notepad.
Find this line:
```
<input id="api-url" value="http://localhost:5000"
```
Change it to your Render URL:
```
<input id="api-url" value="https://predictive-maintenance-api.onrender.com"
```
Save the file.

## Step 7 — Deploy the dashboard (Frontend)
1. On Render, click **New → Static Site**
2. Connect the same GitHub repository
3. Fill in:
   - **Name:** predictive-maintenance-dashboard
   - **Publish Directory:** . (just a dot)
4. Click **Create Static Site**
5. Render gives you a URL like: `https://predictive-maintenance-dashboard.onrender.com`

## Done!
Open that dashboard URL in any browser, on any device, anywhere in the world. 🎉

## Important note about free plan
Render's free plan "sleeps" after 15 minutes of no use.
The first request after sleeping takes ~30 seconds to wake up — that's normal.
