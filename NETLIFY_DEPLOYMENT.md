# Netlify Deployment Guide

## Overview
This guide helps you deploy the Ambitious Hub project on Netlify with serverless functions for the backend.

## Prerequisites
- Netlify account (free at https://netlify.com)
- GitHub account (already connected)
- Environment variables ready

## Deployment Steps

### Step 1: Connect GitHub to Netlify
1. Go to https://netlify.com
2. Click **Sign up** or **Log in**
3. Choose **GitHub** as the connection method
4. Authorize Netlify to access your GitHub repositories
5. Select **ambi_hub** repository

### Step 2: Configure Build Settings
When Netlify asks for build configuration:
- **Base directory**: (leave empty)
- **Build command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- **Publish directory**: `frontend/static`
- **Functions directory**: `netlify/functions`

### Step 3: Set Environment Variables
In Netlify dashboard, go to **Site settings → Environment → Environment variables** and add:

```
SECRET_KEY=<generate-random-key-here>
DEBUG=False
ALLOWED_HOSTS=<your-netlify-domain>.netlify.app
DATABASE_URL=<your-database-url>
```

To generate a SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4: Configure Database
Netlify Functions are serverless and stateless, so you MUST use an external database:

**Option A: Use Render PostgreSQL**
- Go to Render.com
- Create a free PostgreSQL database
- Copy the connection string
- Paste as `DATABASE_URL` in Netlify environment variables

**Option B: Use Supabase (PostgreSQL)**
- Go to https://supabase.com
- Create a free project
- Copy the connection string
- Add as `DATABASE_URL`

**Option C: Use MongoDB Atlas**
- Go to https://www.mongodb.com/cloud/atlas
- Create a free cluster
- Update Django settings for MongoDB

### Step 5: Deploy
1. Commit and push changes to GitHub
2. Netlify will automatically build and deploy
3. Your site will be live at `https://<your-domain>.netlify.app`

### Step 6: Run Initial Setup
After first deployment, run migrations:

Option A: Via Netlify CLI
```bash
npm install -g netlify-cli
netlify functions:invoke api
```

Option B: Via external Django admin panel
- Create a separate admin endpoint
- Or use database directly

## Limitations & Considerations

### ⚠️ Important Limitations:
1. **Serverless functions have timeout limits** (typically 10 seconds)
   - Long-running tasks may fail
   - Heavy computations should be moved to background jobs

2. **No persistent storage** on functions
   - All file uploads must go to external storage (AWS S3, Cloudinary, etc.)

3. **Cold starts** may cause initial delay
   - First request after inactivity takes longer
   - Consider upgrading to Pro plan for better performance

4. **Database connections**
   - Must use external database (not SQLite)
   - Connection pooling recommended

### 📊 Performance Tips:
- Optimize Django queries (add `select_related`, `prefetch_related`)
- Use caching (Redis, Memcached)
- Compress static files
- Enable CDN caching

## Alternative: Backend on Render + Frontend on Netlify

If Netlify Functions don't work well, consider:

1. **Deploy Backend on Render.com** (or Railway)
   - Use the Procfile already in the repo
   
2. **Deploy Frontend on Netlify**
   - Build only static templates/SPA
   - Call backend API from frontend

3. **Connect them via API**
   - Update `ALLOWED_HOSTS` on backend
   - Update `CORS` settings
   - Configure API endpoints in frontend

This is the recommended approach for production.

## Troubleshooting

### Build fails
- Check build logs in Netlify dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### Database connection errors
- Check `DATABASE_URL` format
- Verify database is accessible from Netlify
- Check firewall/IP whitelist on database

### 500 errors
- Check function logs in Netlify
- Enable Django debug mode temporarily (not recommended for production)
- Test locally first

## Support
For more info:
- Netlify Docs: https://docs.netlify.com
- Django Docs: https://docs.djangoproject.com
- Render Postgres: https://render.com/docs/databases
