# ========================================================
# SHIVASTREAM FLASK REST API & WEB SERVER
# Built with Python 3, Flask, SQLite3, CORS
# ========================================================

from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
import sqlite3
import json
import os
from database import init_db, get_db_connection

# Initialize Flask app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)  # Enable Cross-Origin requests

# Helper to format movie dictionary from sqlite Row
def format_movie(row):
    d = dict(row)
    if "genres" in d and isinstance(d["genres"], str):
        try:
            d["genres"] = json.loads(d["genres"])
        except Exception:
            d["genres"] = [g.strip() for g in d["genres"].split(",") if g.strip()]
    if "cast_members" in d and isinstance(d["cast_members"], str):
        try:
            d["cast_members"] = json.loads(d["cast_members"])
        except Exception:
            d["cast_members"] = [c.strip() for c in d["cast_members"].split(",") if c.strip()]
        d["cast"] = d["cast_members"]
    return d

# ==========================================
# 1. STATIC FILES SERVING (FRONTEND)
# ==========================================

@app.route("/")
def index():
    """Serves the main ShivaStream homepage."""
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    """Serves CSS, JS, images, and other static assets."""
    if os.path.exists(os.path.join(BASE_DIR, filename)):
        return send_from_directory(BASE_DIR, filename)
    abort(404)

# ==========================================
# 2. HEALTH & STATS API
# ==========================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "online",
        "app": "ShivaStream Backend API",
        "version": "1.0.0",
        "developer": "Shivanshu",
        "database": "SQLite3"
    })

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Provides streaming platform metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM movies")
    total_movies = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(views_count) FROM movies")
    total_views = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM watchlist")
    total_saved = cursor.fetchone()[0]

    cursor.execute("SELECT title, views_count FROM movies ORDER BY views_count DESC LIMIT 3")
    top_viewed = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return jsonify({
        "total_titles": total_movies,
        "total_views": total_views,
        "watchlist_items": total_saved,
        "trending_picks": top_viewed
    })

# ==========================================
# 3. MOVIES REST API
# ==========================================

@app.route("/api/movies", methods=["GET"])
def get_movies():
    """
    Get all movies with optional filters:
    - ?category=movies|series|trending
    - ?genre=Sci-Fi|Action
    - ?search=query
    """
    category = request.args.get("category")
    genre = request.args.get("genre")
    search_query = request.args.get("search", "").strip().lower()

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if genre:
        query += " AND genres LIKE ?"
        params.append(f"%{genre}%")

    if search_query:
        query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(genres) LIKE ? OR LOWER(director) LIKE ?)"
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    query += " ORDER BY rating DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    movies = [format_movie(r) for r in rows]
    return jsonify({
        "count": len(movies),
        "movies": movies
    })

@app.route("/api/movies/<string:movie_id>", methods=["GET"])
def get_movie_by_id(movie_id):
    """Retrieve details for a single movie."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Movie not found"}), 404

    return jsonify(format_movie(row))

@app.route("/api/movies", methods=["POST"])
def add_movie():
    """Add a new movie or web series into ShivaStream catalog."""
    data = request.get_json() or {}

    required = ["id", "title", "category", "genres", "year", "rating", "poster", "backdrop", "trailer_id", "description"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO movies (
                id, title, category, genres, year, rating, match_score, age, duration,
                quality, badge, poster, backdrop, trailer_id, description, cast_members, director
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id"],
            data["title"],
            data["category"],
            json.dumps(data.get("genres", [])),
            data["year"],
            data["rating"],
            data.get("match_score", 95),
            data.get("age", "16+"),
            data.get("duration", "2h"),
            data.get("quality", "4K Ultra HD"),
            data.get("badge", "NEW"),
            data["poster"],
            data["backdrop"],
            data["trailer_id"],
            data["description"],
            json.dumps(data.get("cast", [])),
            data.get("director", "Unknown")
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Movie ID already exists"}), 409
    finally:
        conn.close()

    return jsonify({"message": f"Movie '{data['title']}' added successfully!", "id": data["id"]}), 201

@app.route("/api/movies/<string:movie_id>/view", methods=["POST"])
def record_movie_view(movie_id):
    """Increment trailer playback views count."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE movies SET views_count = views_count + 1 WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "View recorded", "movie_id": movie_id})

# ==========================================
# 4. FEATURED HEROES API
# ==========================================

@app.route("/api/heroes", methods=["GET"])
def get_heroes():
    """Returns featured spotlight titles for top banner."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM hero_spotlights")
    rows = cursor.fetchall()
    conn.close()

    heroes = []
    for r in rows:
        d = dict(r)
        if "genres" in d:
            try:
                d["genres"] = json.loads(d["genres"])
            except Exception:
                d["genres"] = []
        heroes.append(d)

    return jsonify(heroes)

# ==========================================
# 5. WATCHLIST API (PERSISTENT IN SQLITE)
# ==========================================

@app.route("/api/watchlist", methods=["GET"])
def get_watchlist():
    """Fetch all saved movies in watchlist."""
    user_id = request.args.get("user_id", 1, type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.*, w.added_at 
        FROM watchlist w
        JOIN movies m ON w.movie_id = m.id
        WHERE w.user_id = ?
        ORDER BY w.added_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    items = [format_movie(r) for r in rows]
    return jsonify({
        "user_id": user_id,
        "count": len(items),
        "watchlist": items
    })

@app.route("/api/watchlist", methods=["POST"])
def add_to_watchlist():
    """Add a title to watchlist in SQLite."""
    data = request.get_json() or {}
    movie_id = data.get("movie_id")
    user_id = data.get("user_id", 1)

    if not movie_id:
        return jsonify({"error": "movie_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO watchlist (user_id, movie_id)
            VALUES (?, ?)
        """, (user_id, movie_id))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

    conn.close()
    return jsonify({"message": "Added to watchlist", "movie_id": movie_id}), 201

@app.route("/api/watchlist/<string:movie_id>", methods=["DELETE"])
def remove_from_watchlist(movie_id):
    """Remove a title from watchlist in SQLite."""
    user_id = request.args.get("user_id", 1, type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?
    """, (user_id, movie_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Removed from watchlist", "movie_id": movie_id})

# ==========================================
# 6. AUTHENTICATION & USER PROFILE API
# ==========================================

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Simple demo login endpoint."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, avatar FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "message": "Login successful",
            "user": dict(user),
            "token": f"demo-jwt-token-{user['id']}"
        })

    return jsonify({"error": "Invalid username or password"}), 401

@app.route("/api/auth/profile", methods=["GET"])
def get_profile():
    """Returns profile for currently active user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, avatar, created_at FROM users WHERE id = 1")
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify(dict(user))
    return jsonify({"error": "User not found"}), 404

# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    init_db()
    print("==================================================")
    print("🔥 SHIVASTREAM FULL-STACK SERVER RUNNING")
    print("📡 Local URL: http://127.0.0.1:5000")
    print("🎬 Serving frontend & SQLite REST API")
    print("==================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)
