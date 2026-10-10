# ========================================================
# SHIVASTREAM DATABASE ENGINE (SQLite)
# Handles database connection, tables creation, and initial seeding
# ========================================================

import sqlite3
import json
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shivastream.db")

def get_db_connection():
    """Returns a connection to the SQLite database with dictionary rows."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables and seeds initial catalog if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Movies Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            genres TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            match_score INTEGER NOT NULL,
            age TEXT NOT NULL,
            duration TEXT NOT NULL,
            quality TEXT NOT NULL,
            badge TEXT,
            poster TEXT NOT NULL,
            backdrop TEXT NOT NULL,
            trailer_id TEXT NOT NULL,
            description TEXT NOT NULL,
            cast_members TEXT NOT NULL,
            director TEXT NOT NULL,
            views_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT 'S',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Watchlist Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            UNIQUE(user_id, movie_id)
        )
    """)

    # 4. Hero Spotlights Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hero_spotlights (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            title TEXT NOT NULL,
            info TEXT NOT NULL,
            description TEXT NOT NULL,
            backdrop TEXT NOT NULL,
            trailer_id TEXT NOT NULL,
            genres TEXT NOT NULL
        )
    """)

    conn.commit()

    # Seed default user if not exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (username, email, password, avatar)
            VALUES (?, ?, ?, ?)
        """, ("Shivanshu", "shivanshu@shivastream.com", "admin123", "S"))
        conn.commit()

    # Seed movies if empty
    cursor.execute("SELECT COUNT(*) FROM movies")
    if cursor.fetchone()[0] == 0:
        seed_movies(cursor)
        seed_heroes(cursor)
        conn.commit()

    conn.close()
    print("Database initialized successfully:", DB_FILE)

def seed_movies(cursor):
    sample_movies = [
        # POPULAR MOVIES
        {
            "id": "inception",
            "title": "Inception",
            "category": "movies",
            "genres": ["Sci-Fi", "Action", "Thriller"],
            "year": 2010,
            "rating": 8.8,
            "match_score": 99,
            "age": "13+",
            "duration": "2h 28m",
            "quality": "4K Ultra HD",
            "badge": "MUST WATCH",
            "poster": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
            "trailer_id": "YoHD9XEInc0",
            "description": "Cobb steals information from his targets by entering their dreams. He is wanted for his alleged role in his wife's murder and his only chance at redemption is to perform the impossible task of planting an idea in a target's mind.",
            "cast_members": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page", "Tom Hardy"],
            "director": "Christopher Nolan"
        },
        {
            "id": "interstellar",
            "title": "Interstellar",
            "category": "movies",
            "genres": ["Sci-Fi", "Adventure", "Drama"],
            "year": 2014,
            "rating": 8.7,
            "match_score": 97,
            "age": "13+",
            "duration": "2h 49m",
            "quality": "4K Ultra HD",
            "badge": "ACADEMY WINNER",
            "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/rAiYTsqJJR0KP8UN8vMzuvsdZ5U.jpg",
            "trailer_id": "zSWdZVtXT7E",
            "description": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft, along with a team of researchers, to find a new planet for humans to call home.",
            "cast_members": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine"],
            "director": "Christopher Nolan"
        },
        {
            "id": "the-dark-knight",
            "title": "The Dark Knight",
            "category": "movies",
            "genres": ["Action", "Crime", "Drama"],
            "year": 2008,
            "rating": 9.0,
            "match_score": 99,
            "age": "16+",
            "duration": "2h 32m",
            "quality": "4K Ultra HD",
            "badge": "TOP RATED #3",
            "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/hkBaDkMWbLaf8B1r5SvR42xVTx7.jpg",
            "trailer_id": "EXeTwQWrcwY",
            "description": "Batman has a new menace in Gotham City — the Joker, a criminal mastermind bent on unleashing chaos and turning the city against its hero and district attorney Harvey Dent.",
            "cast_members": ["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Michael Caine", "Gary Oldman"],
            "director": "Christopher Nolan"
        },
        {
            "id": "avengers-endgame",
            "title": "Avengers: Endgame",
            "category": "movies",
            "genres": ["Action", "Adventure", "Sci-Fi"],
            "year": 2019,
            "rating": 8.4,
            "match_score": 96,
            "age": "13+",
            "duration": "3h 01m",
            "quality": "4K Ultra HD",
            "badge": "BLOCKBUSTER",
            "poster": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg",
            "trailer_id": "TcMBFSGVi1c",
            "description": "After the devastating events of Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more to reverse Thanos' actions and restore balance to the universe.",
            "cast_members": ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo", "Chris Hemsworth", "Scarlett Johansson"],
            "director": "Anthony Russo, Joe Russo"
        },
        {
            "id": "spider-man",
            "title": "Spider-Man: No Way Home",
            "category": "movies",
            "genres": ["Action", "Adventure", "Fantasy"],
            "year": 2021,
            "rating": 8.2,
            "match_score": 94,
            "age": "13+",
            "duration": "2h 28m",
            "quality": "4K Ultra HD",
            "badge": "FAN FAVORITE",
            "poster": "https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/14QbnygCuTO0vl7CAFmPf1fgZfV.jpg",
            "trailer_id": "JfVOs4VSpmA",
            "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other multiverses appear, forcing Peter to discover what it truly means to be Spider-Man.",
            "cast_members": ["Tom Holland", "Zendaya", "Benedict Cumberbatch", "Willem Dafoe", "Andrew Garfield"],
            "director": "Jon Watts"
        },
        {
            "id": "oppenheimer",
            "title": "Oppenheimer",
            "category": "movies",
            "genres": ["Biography", "Drama", "History"],
            "year": 2023,
            "rating": 8.9,
            "match_score": 98,
            "age": "18+",
            "duration": "3h 00m",
            "quality": "4K Ultra HD",
            "badge": "OSCAR WINNER",
            "poster": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/fm6KqXpk3M2HVveHwCrBSSBaO0V.jpg",
            "trailer_id": "uYPbbksJxIg",
            "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II at Los Alamos Laboratory.",
            "cast_members": ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr.", "Florence Pugh"],
            "director": "Christopher Nolan"
        },
        {
            "id": "dune-part-two",
            "title": "Dune: Part Two",
            "category": "movies",
            "genres": ["Sci-Fi", "Adventure", "Action"],
            "year": 2024,
            "rating": 8.6,
            "match_score": 96,
            "age": "13+",
            "duration": "2h 46m",
            "quality": "4K Ultra HD",
            "badge": "NEW RELEASE",
            "poster": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s5200bm.jpg",
            "trailer_id": "Way9Dexny3w",
            "description": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family, facing a choice between love and the fate of the known universe.",
            "cast_members": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Javier Bardem", "Austin Butler"],
            "director": "Denis Villeneuve"
        },

        # TRENDING NOW
        {
            "id": "stranger-things",
            "title": "Stranger Things",
            "category": "trending",
            "genres": ["Sci-Fi", "Horror", "Drama"],
            "year": 2022,
            "rating": 8.7,
            "match_score": 98,
            "age": "16+",
            "duration": "4 Seasons",
            "quality": "4K Ultra HD",
            "badge": "🔥 #1 ON SHIVASTREAM",
            "poster": "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/56v2KjBlU4XaOv9rVYEQypROD7P.jpg",
            "trailer_id": "b9EkMc79ZSU",
            "description": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces and one strange little girl with telekinetic powers.",
            "cast_members": ["Millie Bobby Brown", "Finn Wolfhard", "Winona Ryder", "David Harbour", "Gaten Matarazzo"],
            "director": "The Duffer Brothers"
        },
        {
            "id": "wednesday",
            "title": "Wednesday",
            "category": "trending",
            "genres": ["Comedy", "Crime", "Fantasy"],
            "year": 2022,
            "rating": 8.1,
            "match_score": 95,
            "age": "13+",
            "duration": "1 Season",
            "quality": "4K Ultra HD",
            "badge": "GLOBAL TOP 10",
            "poster": "https://image.tmdb.org/t/p/w500/9PFonBhy4cQy7Jz20NpMygczOkv.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/iHSwvRVsRyxpX7FE7GbviaDvgGZ.jpg",
            "trailer_id": "Di310BC8Ur4",
            "description": "Smart, sarcastic and a little dead inside, Wednesday Addams investigates a murder spree while making new friends — and foes — at Nevermore Academy.",
            "cast_members": ["Jenna Ortega", "Gwendoline Christie", "Riki Lindhome", "Emma Myers", "Christina Ricci"],
            "director": "Tim Burton"
        },
        {
            "id": "money-heist",
            "title": "Money Heist",
            "category": "trending",
            "genres": ["Action", "Crime", "Thriller"],
            "year": 2021,
            "rating": 8.2,
            "match_score": 94,
            "age": "18+",
            "duration": "5 Seasons",
            "quality": "HD 1080p",
            "badge": "TRENDING",
            "poster": "https://image.tmdb.org/t/p/w500/reEMJA1uzscCbkpeRJeTT2bjqUp.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/gFZri2YbFUzgQgnY76PDIBG5Cln.jpg",
            "trailer_id": "_InqQJRqGW4",
            "description": "Eight thieves take hostages and lock themselves in the Royal Mint of Spain as a criminal mastermind manipulates the police to carry out the biggest heist in history.",
            "cast_members": ["Úrsula Corberó", "Álvaro Morte", "Itziar Ituño", "Pedro Alonso", "Miguel Herrán"],
            "director": "Álex Pina"
        },
        {
            "id": "dark",
            "title": "Dark",
            "category": "trending",
            "genres": ["Sci-Fi", "Mystery", "Drama"],
            "year": 2020,
            "rating": 8.7,
            "match_score": 97,
            "age": "16+",
            "duration": "3 Seasons",
            "quality": "4K Ultra HD",
            "badge": "CRITIC'S PICK",
            "poster": "https://image.tmdb.org/t/p/w500/apbrbWs8M9lyOpJYU5WXrpFbk1Z.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/3lBDg3i6nnOccRsgAAss79HGCCv.jpg",
            "trailer_id": "rrwycJ08PSA",
            "description": "A missing child sets four families on a frantic hunt for answers as they unearth a mind-bending mystery that spans three generations and alternate timelines.",
            "cast_members": ["Louis Hofmann", "Oliver Masucci", "Jördis Triebel", "Maja Schöne", "Karoline Eichhorn"],
            "director": "Baran bo Odar, Jantje Friese"
        },
        {
            "id": "peaky-blinders",
            "title": "Peaky Blinders",
            "category": "trending",
            "genres": ["Crime", "Drama"],
            "year": 2022,
            "rating": 8.8,
            "match_score": 96,
            "age": "18+",
            "duration": "6 Seasons",
            "quality": "4K Ultra HD",
            "badge": "TOP 10",
            "poster": "https://image.tmdb.org/t/p/w500/vUUqzWa2LnHIVqkaKVlVGkVcZIW.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/7c9UVPPiTPltouxShY9JfvsWukR.jpg",
            "trailer_id": "oVzVdvGIC7U",
            "description": "A notorious gang in 1919 Birmingham, England, is led by the fierce Tommy Shelby, a crime boss set on moving up in the world no matter the cost.",
            "cast_members": ["Cillian Murphy", "Paul Anderson", "Helen McCrory", "Sophie Rundle", "Tom Hardy"],
            "director": "Steven Knight"
        },
        {
            "id": "the-witcher",
            "title": "The Witcher",
            "category": "trending",
            "genres": ["Action", "Adventure", "Fantasy"],
            "year": 2023,
            "rating": 8.0,
            "match_score": 91,
            "age": "18+",
            "duration": "3 Seasons",
            "quality": "4K Ultra HD",
            "badge": "FANTASY HIT",
            "poster": "https://image.tmdb.org/t/p/w500/AoGsDM02UVt0npBA8OvpDcZbaMi.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/jBJWaqoSCiARWtfV0GlqHrcdidd.jpg",
            "trailer_id": "ndl1W4ltcmg",
            "description": "Geralt of Rivia, a mutated monster-hunter for hire, journeys toward his destiny in a turbulent world where people often prove more wicked than beasts.",
            "cast_members": ["Henry Cavill", "Anya Chalotra", "Freya Allan", "Joey Batey", "Eamon Farren"],
            "director": "Lauren Schmidt Hissrich"
        },

        # TV SHOWS & WEB SERIES
        {
            "id": "breaking-bad",
            "title": "Breaking Bad",
            "category": "series",
            "genres": ["Crime", "Drama", "Thriller"],
            "year": 2013,
            "rating": 9.5,
            "match_score": 99,
            "age": "18+",
            "duration": "5 Seasons",
            "quality": "4K Ultra HD",
            "badge": "HIGHEST RATED",
            "poster": "https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg",
            "trailer_id": "HhesaQXLuRY",
            "description": "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family's financial future.",
            "cast_members": ["Bryan Cranston", "Aaron Paul", "Anna Gunn", "Betsy Brandt", "Dean Norris"],
            "director": "Vince Gilligan"
        },
        {
            "id": "the-boys",
            "title": "The Boys",
            "category": "series",
            "genres": ["Action", "Comedy", "Sci-Fi"],
            "year": 2024,
            "rating": 8.7,
            "match_score": 95,
            "age": "18+",
            "duration": "4 Seasons",
            "quality": "4K Ultra HD",
            "badge": "POPULAR",
            "poster": "https://image.tmdb.org/t/p/w500/in1R2dDc421JxsoRWaIIAqVI2KE.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/n6bUvigpRFqSwmPp1m2YADdbRBc.jpg",
            "trailer_id": "M1bhOaLvCyo",
            "description": "A group of vigilantes set out to take down corrupt superheroes who abuse their superpowers, operating under the sinister mega-corporation Vought International.",
            "cast_members": ["Karl Urban", "Jack Quaid", "Antony Starr", "Erin Moriarty", "Dominique McElligott"],
            "director": "Eric Kripke"
        },
        {
            "id": "loki",
            "title": "Loki",
            "category": "series",
            "genres": ["Action", "Adventure", "Fantasy"],
            "year": 2023,
            "rating": 8.2,
            "match_score": 93,
            "age": "13+",
            "duration": "2 Seasons",
            "quality": "4K Ultra HD",
            "badge": "MARVEL STUDIOS",
            "poster": "https://image.tmdb.org/t/p/w500/kEl2t3OhXc3Zb9FBh1AuYzRTgZp.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/b9UCf9Vs8UMFGZt4f2jX40WpLDO.jpg",
            "trailer_id": "nW948Va-l10",
            "description": "The mercurial villain Loki resumes his role as the God of Mischief following the events of Avengers: Endgame, joining forces with the mysterious Time Variance Authority.",
            "cast_members": ["Tom Hiddleston", "Owen Wilson", "Sophia Di Martino", "Gugu Mbatha-Raw", "Wunmi Mosaku"],
            "director": "Michael Waldron"
        },
        {
            "id": "squid-game",
            "title": "Squid Game",
            "category": "series",
            "genres": ["Action", "Drama", "Mystery"],
            "year": 2021,
            "rating": 8.0,
            "match_score": 95,
            "age": "18+",
            "duration": "1 Season",
            "quality": "4K Ultra HD",
            "badge": "MOST WATCHED",
            "poster": "https://image.tmdb.org/t/p/w500/1QdXdRYfktUSONkl1oD5gc6Be0s.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/qw3J9cNeLioOL0Ukb6UT7BhDrGO.jpg",
            "trailer_id": "oqxAJKy0ii4",
            "description": "Hundreds of cash-strapped players accept a strange invitation to compete in children's games. Inside, a tempting 45.6 billion won prize awaits — with deadly high stakes.",
            "cast_members": ["Lee Jung-jae", "Park Hae-soo", "Wi Ha-joon", "Jung Ho-yeon", "O Yeong-su"],
            "director": "Hwang Dong-hyuk"
        },
        {
            "id": "the-last-of-us",
            "title": "The Last of Us",
            "category": "series",
            "genres": ["Action", "Adventure", "Drama"],
            "year": 2023,
            "rating": 8.8,
            "match_score": 97,
            "age": "18+",
            "duration": "1 Season",
            "quality": "4K Ultra HD",
            "badge": "EMMY WINNER",
            "poster": "https://image.tmdb.org/t/p/w500/dmo6TYuuJgaYinXBPjrgG9mB5od.jpg",
            "backdrop": "https://image.tmdb.org/t/p/original/uDgy6hyPd82kOHh6I95FLtLnj6p.jpg",
            "trailer_id": "uLtkt8BonwM",
            "description": "Twenty years after modern civilization has been destroyed, Joel, a hardened survivor, is hired to smuggle 14-year-old Ellie across a dangerous post-apocalyptic United States.",
            "cast_members": ["Pedro Pascal", "Bella Ramsey", "Gabriel Luna", "Anna Torv", "Nico Parker"],
            "director": "Craig Mazin, Neil Druckmann"
        }
    ]

    for m in sample_movies:
        cursor.execute("""
            INSERT OR IGNORE INTO movies (
                id, title, category, genres, year, rating, match_score, age, duration,
                quality, badge, poster, backdrop, trailer_id, description, cast_members, director
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["id"],
            m["title"],
            m["category"],
            json.dumps(m["genres"]),
            m["year"],
            m["rating"],
            m["match_score"],
            m["age"],
            m["duration"],
            m["quality"],
            m.get("badge"),
            m["poster"],
            m["backdrop"],
            m["trailer_id"],
            m["description"],
            json.dumps(m["cast_members"]),
            m["director"]
        ))

def seed_heroes(cursor):
    heroes = [
        {
            "id": "stranger-things",
            "label": "🔥 #1 ON SHIVASTREAM TODAY",
            "title": "Stranger Things",
            "info": "2022 &bull; 16+ &bull; 4 Seasons &bull; Ultra HD 4K",
            "description": "When a young boy disappears, his friends, family and a local police chief uncover an extraordinary mystery involving secret experiments, terrifying supernatural forces and a strange alternate dimension.",
            "backdrop": "https://image.tmdb.org/t/p/original/56v2KjBlU4XaOv9rVYEQypROD7P.jpg",
            "trailer_id": "b9EkMc79ZSU",
            "genres": ["Sci-Fi", "Horror", "Drama"]
        },
        {
            "id": "the-dark-knight",
            "label": "⭐ CRITICS' CHOICE BLOCKBUSTER",
            "title": "The Dark Knight",
            "info": "2008 &bull; 16+ &bull; 2h 32m &bull; IMDb 9.0",
            "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "backdrop": "https://image.tmdb.org/t/p/original/hkBaDkMWbLaf8B1r5SvR42xVTx7.jpg",
            "trailer_id": "EXeTwQWrcwY",
            "genres": ["Action", "Crime", "Drama"]
        },
        {
            "id": "the-last-of-us",
            "label": "🏆 8 EMMY AWARDS WINNER",
            "title": "The Last of Us",
            "info": "2023 &bull; 18+ &bull; 1 Season &bull; IMDb 8.8",
            "description": "After a global pandemic destroys civilization, a hardened survivor takes charge of a 14-year-old girl who may be humanity's last hope on a ruthless journey across America.",
            "backdrop": "https://image.tmdb.org/t/p/original/uDgy6hyPd82kOHh6I95FLtLnj6p.jpg",
            "trailer_id": "uLtkt8BonwM",
            "genres": ["Action", "Adventure", "Drama"]
        },
        {
            "id": "inception",
            "label": "🌀 MIND-BENDING MASTERPIECE",
            "title": "Inception",
            "info": "2010 &bull; 13+ &bull; 2h 28m &bull; IMDb 8.8",
            "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O., but his tragic past may doom the mission.",
            "backdrop": "https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
            "trailer_id": "YoHD9XEInc0",
            "genres": ["Sci-Fi", "Action", "Thriller"]
        }
    ]

    for h in heroes:
        cursor.execute("""
            INSERT OR IGNORE INTO hero_spotlights (
                id, label, title, info, description, backdrop, trailer_id, genres
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            h["id"],
            h["label"],
            h["title"],
            h["info"],
            h["description"],
            h["backdrop"],
            h["trailer_id"],
            json.dumps(h["genres"])
        ))

if __name__ == "__main__":
    init_db()
