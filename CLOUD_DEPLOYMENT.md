# 🚀 Cloud Deployment Guide - वाणीCheck API

## ✅ Your Code is Ready!

Your codebase has been pushed to GitHub with all sensitive files protected:

```
📍 Repository: https://github.com/aaswani-v/lang-api
📌 Branch: master
✅ Status: Production-ready
🔒 Secrets: Protected by .gitignore
```

---

## 🎯 Quick Deploy (Choose One)

### **FASTEST: Railway.app** ⭐ (5 minutes)

1. **Go to:** https://railway.app
2. **Click:** "New Project" → "Deploy from GitHub"
3. **Search:** `lang-api`
4. **Select:** `aaswani-v/lang-api` → `master` branch
5. **Wait:** 2-3 minutes for deployment
6. **Copy:** Your public URL from Railway dashboard

**You get:** `https://lang-api-production-xxxx.railway.app/v1/detect`

---

### **EASIEST: Replit** (3 minutes)

1. **Go to:** https://replit.com
2. **Click:** "Create Repl" → "Import from GitHub"
3. **Paste:** `https://github.com/aaswani-v/lang-api`
4. **Click:** "Run" (auto-deploys)
5. **Get:** Public URL in webview

**You get:** `https://vanicheck-api.your-username.repl.co/v1/detect`

---

### **RECOMMENDED: Render.com** (10 minutes)

1. **Go to:** https://render.com
2. **Sign up** with GitHub
3. **Create Web Service**
4. **Connect:** `aaswani-v/lang-api`
5. **Configure:**
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
6. **Deploy** (3-5 minutes)

**You get:** `https://vanicheck-api.onrender.com/v1/detect`

---

### **TRADITIONAL: Heroku** (15 minutes, Paid)

```powershell
# Install Heroku CLI
scoop install heroku

# Login
heroku login

# Create app
heroku create vanicheck-api

# Deploy
git push heroku master

# Set API key
heroku config:set VANICHECK_API_KEY=vanicheck-secret-key-2026

# Get logs
heroku logs --tail
```

**You get:** `https://vanicheck-api.herokuapp.com/v1/detect`

---

## 📝 What to Submit to Hackathon

Once deployed, share these details:

```
📌 API Endpoint: https://your-deployed-url/v1/detect
🔑 API Key: vanicheck-secret-key-2026
🌐 Language: english
🎵 Audio Format: WAV
```

---

## ✅ Verify Deployment Works

### Test Health (No Auth)
```bash
curl https://your-deployed-url/health
```

### Test with Auth
```bash
curl -H "X-API-KEY: vanicheck-secret-key-2026" \
  https://your-deployed-url/v1/health
```

### Full Detection Test
```bash
curl -X POST https://your-deployed-url/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"audio_data":"SUQz...", "language":"english"}'
```

---

## 🔒 What Was Protected

✅ **Hidden files** (in .gitignore):
- `.env` - Real API keys
- `__pycache__/` - Compiled Python
- `venv/` - Virtual environment
- `*.wav` - Test audio files
- `.vscode/`, `.idea/` - IDE settings

✅ **Safe to share:**
- Source code (main.py, etc.)
- Documentation
- Test scripts
- Configuration examples

---

## 📊 Platform Comparison

| Platform | Time | Cost | Effort | Free Tier |
|----------|------|------|--------|-----------|
| Railway ⭐ | 5 min | Free | ⭐⭐⭐⭐⭐ | Yes |
| Replit | 3 min | Free | ⭐⭐⭐⭐⭐ | Yes |
| Render | 10 min | Free | ⭐⭐⭐⭐ | Yes |
| Heroku | 15 min | $7/mo | ⭐⭐⭐ | No |
| AWS | 20 min | Variable | ⭐⭐ | Yes (limited) |

---

## 🚀 Start Deployment NOW

**Recommended for hackathon:**

```
Railway.app
├─ Fastest setup
├─ Free tier available
├─ Auto-deploys on git push
└─ Best for quick submission
```

**Steps:**
1. Go to https://railway.app
2. Sign with GitHub
3. Deploy from `aaswani-v/lang-api`
4. Wait 3 minutes
5. Share URL with hackathon ✅

---

## 🎓 Environment Variables

All platforms need this set:

```
VANICHECK_API_KEY=vanicheck-secret-key-2026
```

**Railway:** Settings → Variables
**Render:** Environment
**Heroku:** `heroku config:set`
**Replit:** Secrets panel

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements.txt` dependencies |
| Port error | Use `0.0.0.0` host (already set ✅) |
| API key fails | Set env var in dashboard |
| Slow startup | App auto-sleeps on free tier, restart needed |
| Timeout | Increase timeout to 30s+ |

---

## 📞 Support Resources

- **Railway:** https://docs.railway.app
- **Render:** https://render.com/docs
- **Replit:** https://docs.replit.com
- **Heroku:** https://devcenter.heroku.com

---

## ✨ You're All Set!

Your API is:
- ✅ Production-ready
- ✅ Code on GitHub (secured)
- ✅ Ready to deploy
- ✅ Ready for hackathon

**Next:** Choose a platform and deploy! 🚀
