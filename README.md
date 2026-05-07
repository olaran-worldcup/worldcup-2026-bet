# ⚽ World Cup 2026 | WW Hub Delivery Betting Pool

A web app for managing a World Cup 2026 betting pool. Share the URL with your team — no installation needed for participants.

## Scoring System

| Phase | Points per correct prediction |
|-------|------|
| Group stage match (1/X/2) | 1 pt |
| Group final position (tiebreaker) | 2 pts per team |
| Round of 32 | 4 pts |
| Round of 16 | 6 pts |
| Quarter-finals | 10 pts |
| Semi-finals | 16 pts |
| Third place | 10 pts |
| Final | 25 pts |
| Golden Ball (Best Player) | 10 pts |
| Golden Boot (Top Goalscorer) | 10 pts |
| Golden Glove (Best Goalkeeper) | 10 pts |

**Maximum possible: ~417 points**
(72 group + 96 tiebreakers + 64 R32 + 48 R16 + 40 QF + 32 SF + 10 third + 25 final + 30 awards)

Later rounds are worth progressively more because they're harder to predict.

## Deploy Online (Free)

### Option 1: Render.com (recommended)

1. Push this code to a GitHub/GitLab repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repo
4. Render auto-detects the `render.yaml` config
5. Click Deploy — you get a public URL like `https://worldcup-2026-betting.onrender.com`

### Option 2: Railway.app

1. Push to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. It auto-detects Python + the Procfile
4. You get a public URL instantly

### Option 3: PythonAnywhere

1. Upload files to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Set up a Flask web app pointing to `app.main:app`
3. Free tier gives you `yourusername.pythonanywhere.com`

## Run Locally

```bash
pip install -r requirements.txt
python run.py
```

Open http://localhost:5000

## How It Works

### For Players
1. Open the shared URL
2. Enter your login name (auto-registers on first use)
3. For each match, select **1** (home wins), **X** (draw), or **2** (away wins)
4. For each group, rank teams 1-4 by predicted goal difference
5. For knockout matches, pick who advances (including via penalties)
6. **Save Draft** to save progress, **Submit** to lock permanently

### For Admin
1. Login as `admin`
2. **Participants**: see who submitted
3. **Enter Results**: enter actual results as games are played
4. **Reports**: generate top-10 rankings per phase

## Project Structure

```
app/
  main.py          - Flask routes and scoring logic
  models.py        - SQLite database
  game_data.py     - Teams and groups
  game_data2.py    - Group matches (A-H)
  game_data3.py    - Group matches (I-L) + knockout bracket
  templates/       - HTML pages
  static/style.css - Minimal styling
run.py             - Local dev entry point
requirements.txt   - Python dependencies
render.yaml        - Render.com deployment config
Procfile           - Generic WSGI deployment
```
