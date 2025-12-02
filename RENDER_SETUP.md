# IMPORTANT: Root Directory Configuration for Render

## Your Repository Structure
```
(root of repository)
├── manage.py          ← Django project is HERE at root
├── build.sh
├── requirements.txt
├── render.yaml
├── news/
├── news_aggregator/
├── templates/
└── static/
```

## Render Configuration

### If Using Render Dashboard (Manual Setup):
**Root Directory field MUST be empty or set to `.`**

1. Go to: https://dashboard.render.com/
2. Select your web service
3. Go to **Settings** tab
4. Find **"Root Directory"** field
5. **CLEAR IT** (leave blank) or set to `.`
6. Click **Save Changes**
7. Click **Manual Deploy** → **Deploy latest commit**

### If Using render.yaml (Blueprint):
The `render.yaml` file already specifies `rootDir: .` which means current directory.

**To deploy using blueprint:**
1. Go to: https://dashboard.render.com/
2. Click **New +** → **Blueprint**
3. Connect this repository
4. Render will read `render.yaml` and configure everything automatically

---

## Common Error
```
==> Service Root Directory "/opt/render/project/src/ojt" is missing
```

**Cause:** Root Directory is set to "ojt" but your files are at repository root  
**Fix:** Clear the Root Directory field in Render dashboard Settings
