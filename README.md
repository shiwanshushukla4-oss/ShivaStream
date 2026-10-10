# 🎬 ShivaStream - Full-Stack Movie & Web Series Platform

> **Developer:** Shivanshu  
> **Project Type:** B.Tech Mini Project / Full-Stack Web Application  
> **Architecture:** Decoupled Frontend + Python Flask REST API + SQLite Database  

---

## 🚀 Overview

**ShivaStream** is a high-performance streaming web application built with a modern cinematic dark interface. It delivers responsive catalog browsing, real-time search, YouTube trailer integration, user watchlists, and dynamic featured hero spotlight carousels.

It features **Dual-Mode Operation**:
1. **Full-Stack Mode:** Powered by a Python Flask REST API connected to an SQLite database (`shivastream.db`).
2. **Standalone / Offline Mode:** Seamlessly falls back to local data and browser `localStorage` if the backend server is stopped.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3 (Glassmorphism, CSS Grid, Flexbox), Vanilla JavaScript (ES6+) |
| **Backend** | Python 3, Flask, Flask-CORS |
| **Database** | SQLite3 (`shivastream.db`) with relational tables and indexing |
| **Media Player** | Embedded YouTube Player API (16:9 Cinema Modal) |
| **Artwork & Metadata** | TMDB CDN (high-res posters & backdrops), IMDb ratings |

---

## 📁 Project Structure

```text
ShivaStream/
│
├── index.html           # Main user interface & semantic layout
├── style.css            # Responsive dark mode stylesheet with glassmorphism
├── script.js            # Client-side engine with API sync & offline fallback
├── data.js              # Offline backup catalog & spotlight definitions
│
├── app.py               # Flask REST API server & static asset handler
├── database.py          # SQLite database connection, tables & auto-seeding
├── shivastream.db       # Portable SQLite database file
├── requirements.txt     # Python backend dependencies
├── run_backend.bat      # 1-click Windows launcher for backend
│
└── backup_v1/           # Safe backup of original project files
```

---

## ⚡ Quick Start Guide

### 1. Launch Full-Stack Server (Recommended)
You can start the backend in either of two ways:

#### Option A: 1-Click Launcher (Windows)
Double-click **`run_backend.bat`**.

#### Option B: Terminal / PowerShell
```powershell
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the Flask server
python app.py
```

Then open your browser and go to:
👉 **`http://localhost:5000`**

The navbar will show: **`🟢 SQLite API`** indicating that the frontend is dynamically connected to the Python backend!

---

### 2. Run in Standalone / Local Mode (Zero-Config)
If you do not want to run a server, simply double-click **`index.html`** in File Explorer to open it in Chrome or Edge.

The navbar will display: **`⚡ Local Mode`**, and all features (trailers, modal details, watchlist, search, filters) will continue to work offline using browser storage.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & system status |
| `GET` | `/api/stats` | Platform statistics (total titles, views, watchlist items) |
| `GET` | `/api/movies` | Get all titles (supports `?category=`, `?genre=`, `?search=`) |
| `GET` | `/api/movies/<id>` | Get details for a specific movie |
| `POST` | `/api/movies` | Admin endpoint to insert a new title into database |
| `POST` | `/api/movies/<id>/view` | Increments trailer view count |
| `GET` | `/api/heroes` | Get featured hero banner spotlights |
| `GET` | `/api/watchlist` | Get user's saved titles (`?user_id=1`) |
| `POST` | `/api/watchlist` | Add a title to watchlist (`{ "movie_id": "...", "user_id": 1 }`) |
| `DELETE` | `/api/watchlist/<id>`| Remove a title from watchlist |
| `POST` | `/api/auth/login` | Simple user login |
| `GET` | `/api/auth/profile` | Current user profile details |

---

## 🗄️ Database Schema (`shivastream.db`)

### `movies`
- `id` (TEXT PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `category` (TEXT NOT NULL)
- `genres` (TEXT - JSON array)
- `year` (INTEGER)
- `rating` (REAL)
- `match_score` (INTEGER)
- `age` (TEXT)
- `duration` (TEXT)
- `quality` (TEXT)
- `badge` (TEXT)
- `poster` (TEXT)
- `backdrop` (TEXT)
- `trailer_id` (TEXT)
- `description` (TEXT)
- `cast_members` (TEXT - JSON array)
- `director` (TEXT)
- `views_count` (INTEGER DEFAULT 0)

### `watchlist`
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `user_id` (INTEGER NOT NULL)
- `movie_id` (TEXT NOT NULL, FOREIGN KEY -> `movies.id`)
- `added_at` (TIMESTAMP)

### `users`
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `username` (TEXT UNIQUE)
- `email` (TEXT UNIQUE)
- `password` (TEXT)
- `avatar` (TEXT)

---

## 🎓 Academic / Viva Highlights
- **Decoupled Architecture:** Separation of Concerns between presentation and business logic.
- **Resilience:** Graceful offline degradation if the REST API is unavailable.
- **Database Normalization:** Relational SQLite schema with foreign keys and unique constraints.
- **Security & Performance:** Asynchronous non-blocking fetch calls, lazy loading images, and sanitized query parameters.
