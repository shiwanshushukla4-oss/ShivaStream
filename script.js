// ========================================================
// SHIVASTREAM - MODERN FULL-STACK CLIENT ENGINE
// Connects to Flask REST API with graceful offline fallback
// ========================================================

document.addEventListener("DOMContentLoaded", () => {
    // --- State Management ---
    let currentHeroIndex = 0;
    let heroAutoInterval = null;
    let isBackendConnected = false;
    const API_BASE = "http://127.0.0.1:5000/api";

    // Working datasets (default to data.js, updated if API connects)
    let moviesList = (typeof MOVIES_DATA !== "undefined") ? [...MOVIES_DATA] : [];
    let heroesList = (typeof FEATURED_HEROES !== "undefined") ? [...FEATURED_HEROES] : [];
    let watchlist = loadWatchlistLocal();

    // --- DOM Elements ---
    const mainNavbar = document.getElementById("mainNavbar");
    const mobileToggle = document.getElementById("mobileToggle");
    const navMenu = document.getElementById("navMenu");
    const serverStatusPill = document.getElementById("serverStatusPill");
    const serverStatusText = document.getElementById("serverStatusText");
    const mobileNavStatus = document.querySelector(".mobile-nav-status");
    const mobileStatusText = document.getElementById("mobileStatusText");

    const searchInput = document.getElementById("searchInput");
    const clearSearchBtn = document.getElementById("clearSearchBtn");
    const searchResultsSection = document.getElementById("searchResultsSection");
    const searchResultsTitle = document.getElementById("searchResultsTitle");
    const searchGrid = document.getElementById("searchGrid");
    const closeSearchSection = document.getElementById("closeSearchSection");

    // Hero Elements
    const heroBackdrop = document.getElementById("heroBackdrop");
    const heroBadge = document.getElementById("heroBadge");
    const heroTitle = document.getElementById("heroTitle");
    const heroMeta = document.getElementById("heroMeta");
    const heroGenres = document.getElementById("heroGenres");
    const heroDesc = document.getElementById("heroDesc");
    const heroPlayBtn = document.getElementById("heroPlayBtn");
    const heroListBtn = document.getElementById("heroListBtn");
    const heroListIcon = document.getElementById("heroListIcon");
    const heroListText = document.getElementById("heroListText");
    const heroInfoBtn = document.getElementById("heroInfoBtn");
    const heroDots = document.getElementById("heroDots");

    // Modal Elements - Video Trailer
    const videoModal = document.getElementById("videoModal");
    const videoPlayerTitle = document.getElementById("videoPlayerTitle");
    const trailerIframe = document.getElementById("trailerIframe");
    const closeVideoModalBtn = document.getElementById("closeVideoModal");

    // Modal Elements - Movie Details
    const movieModal = document.getElementById("movieModal");
    const closeModalBtn = document.getElementById("closeModal");
    const modalBanner = document.getElementById("modalBanner");
    const modalTitle = document.getElementById("modalTitle");
    const modalMatch = document.getElementById("modalMatch");
    const modalYear = document.getElementById("modalYear");
    const modalAge = document.getElementById("modalAge");
    const modalDuration = document.getElementById("modalDuration");
    const modalQuality = document.getElementById("modalQuality");
    const modalDescription = document.getElementById("modalDescription");
    const modalCast = document.getElementById("modalCast");
    const modalGenres = document.getElementById("modalGenres");
    const modalDirector = document.getElementById("modalDirector");
    const modalRating = document.getElementById("modalRating");
    const modalPlayBtn = document.getElementById("modalPlayBtn");
    const modalWatchlistBtn = document.getElementById("modalWatchlistBtn");

    // Containers
    const trendingContainer = document.getElementById("trendingContainer");
    const moviesContainer = document.getElementById("moviesContainer");
    const seriesContainer = document.getElementById("seriesContainer");
    const actionContainer = document.getElementById("actionContainer");
    const myListSection = document.getElementById("mylist");
    const myListContainer = document.getElementById("myListContainer");
    const navWatchlistCount = document.getElementById("navWatchlistCount");
    const watchlistCount = document.getElementById("watchlistCount");
    const toastNotification = document.getElementById("toastNotification");
    const toastMessage = document.getElementById("toastMessage");

    // Active Movie for Modals
    let activeMovie = null;

    // ==========================================
    // 1. INITIALIZATION & BACKEND SYNC
    // ==========================================

    async function init() {
        // Initial render with offline data first (ensures immediate 0ms render)
        renderHeroDots();
        updateHero(0);
        startHeroAutoRotate();
        populateSections();
        updateWatchlistUI();

        // Check if Flask backend is running
        await syncWithBackend();

        // Setup Carousel arrows & general UI
        setupCarouselControls();
        setupSearchControls();
        setupGenreFilterControls();
        setupNavbarControls();
    }

    async function syncWithBackend() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 1200);

            const res = await fetch(`${API_BASE}/health`, { signal: controller.signal });
            clearTimeout(timeoutId);

            if (res.ok) {
                isBackendConnected = true;
                if (serverStatusPill) {
                    serverStatusPill.classList.add("online");
                    serverStatusText.textContent = "SQLite API";
                    serverStatusPill.title = "Connected to Python Flask REST API & SQLite DB";
                }
                if (mobileNavStatus) {
                    mobileNavStatus.classList.add("online");
                    mobileStatusText.textContent = "Server: SQLite API Online";
                }

                // Fetch live movies from database
                const moviesRes = await fetch(`${API_BASE}/movies`);
                if (moviesRes.ok) {
                    const data = await moviesRes.json();
                    if (data.movies && data.movies.length > 0) {
                        moviesList = data.movies;
                        populateSections();
                    }
                }

                // Fetch live heroes
                const heroesRes = await fetch(`${API_BASE}/heroes`);
                if (heroesRes.ok) {
                    const heroes = await heroesRes.json();
                    if (heroes && heroes.length > 0) {
                        heroesList = heroes;
                        renderHeroDots();
                        updateHero(currentHeroIndex);
                    }
                }

                // Fetch live watchlist
                const wlRes = await fetch(`${API_BASE}/watchlist`);
                if (wlRes.ok) {
                    const wlData = await wlRes.json();
                    if (wlData.watchlist) {
                        watchlist = wlData.watchlist;
                        saveWatchlistLocal();
                        updateWatchlistUI();
                    }
                }
            }
        } catch {
            // Backend offline - Local Mode active
            isBackendConnected = false;
            if (serverStatusPill) {
                serverStatusPill.classList.remove("online");
                serverStatusText.textContent = "Local Mode";
                serverStatusPill.title = "Running in Local Offline Mode. Start Flask server to connect SQLite.";
            }
            if (mobileNavStatus) {
                mobileNavStatus.classList.remove("online");
                mobileStatusText.textContent = "Server: Local Mode";
            }
        }
    }

    // ==========================================
    // 2. DATA RENDERING
    // ==========================================

    function populateSections() {
        // Trending
        const trending = moviesList.filter(m => m.category === "trending");
        renderCarousel(trendingContainer, trending);

        // Movies
        const movies = moviesList.filter(m => m.category === "movies");
        renderCarousel(moviesContainer, movies);

        // TV Shows
        const series = moviesList.filter(m => m.category === "series");
        renderCarousel(seriesContainer, series);

        // Action & Sci-Fi Spotlight
        const actionSciFi = moviesList.filter(m => {
            const genres = Array.isArray(m.genres) ? m.genres : [];
            return genres.includes("Action") || genres.includes("Sci-Fi");
        });
        renderCarousel(actionContainer, actionSciFi);
    }

    function createMovieCard(movie) {
        const card = document.createElement("div");
        card.className = "movie-card";
        card.setAttribute("data-id", movie.id);
        card.setAttribute("data-title", movie.title);

        const inWatchlist = isMovieInWatchlist(movie.id);

        card.innerHTML = `
            ${movie.badge ? `<span class="card-badge">${movie.badge}</span>` : ""}
            <img class="card-poster" src="${movie.poster}" alt="${movie.title}" loading="lazy" />
            <div class="card-overlay">
                <h4 class="card-title">${movie.title}</h4>
                <div class="card-meta">
                    <span class="card-rating">★ ${movie.rating}</span>
                    <span class="card-year">${movie.year}</span>
                    <span class="card-age">${movie.age}</span>
                </div>
                <div class="card-actions">
                    <button class="action-btn play" title="Play Trailer">▶</button>
                    <button class="action-btn watchlist ${inWatchlist ? "active" : ""}" title="${inWatchlist ? "Remove from My List" : "Add to My List"}">
                        ${inWatchlist ? "✓" : "+"}
                    </button>
                    <button class="action-btn info" title="More Info">ⓘ</button>
                </div>
            </div>
        `;

        card.addEventListener("click", (e) => {
            if (e.target.closest(".action-btn")) return;
            openMovieModal(movie);
        });

        const playBtn = card.querySelector(".action-btn.play");
        playBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            openVideoModal(movie);
        });

        const wlBtn = card.querySelector(".action-btn.watchlist");
        wlBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleWatchlist(movie);
        });

        const infoBtn = card.querySelector(".action-btn.info");
        infoBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            openMovieModal(movie);
        });

        return card;
    }

    function renderCarousel(container, list) {
        if (!container) return;
        container.innerHTML = "";
        list.forEach(movie => {
            container.appendChild(createMovieCard(movie));
        });
    }

    // ==========================================
    // 3. HERO SPOTLIGHT CAROUSEL
    // ==========================================

    function renderHeroDots() {
        if (!heroDots) return;
        heroDots.innerHTML = "";
        heroesList.forEach((_, index) => {
            const dot = document.createElement("div");
            dot.className = `dot ${index === 0 ? "active" : ""}`;
            dot.addEventListener("click", () => {
                clearInterval(heroAutoInterval);
                updateHero(index);
                startHeroAutoRotate();
            });
            heroDots.appendChild(dot);
        });
    }

    function updateHero(index) {
        if (heroesList.length === 0) return;
        currentHeroIndex = index;
        const hero = heroesList[index];
        const fullMovie = moviesList.find(m => m.id === hero.id) || hero;

        heroBackdrop.style.backgroundImage = `url('${hero.backdrop}')`;
        heroBadge.innerHTML = hero.label;
        heroTitle.textContent = hero.title;
        heroMeta.innerHTML = hero.info;
        heroDesc.textContent = hero.description;

        heroGenres.innerHTML = "";
        const genres = Array.isArray(hero.genres) ? hero.genres : [];
        genres.forEach(g => {
            const pill = document.createElement("span");
            pill.className = "genre-pill";
            pill.textContent = g;
            heroGenres.appendChild(pill);
        });

        const inList = isMovieInWatchlist(fullMovie.id);
        heroListIcon.textContent = inList ? "✓" : "+";
        heroListText.textContent = inList ? "In My List" : "My List";

        const dots = heroDots.querySelectorAll(".dot");
        dots.forEach((dot, idx) => {
            dot.classList.toggle("active", idx === index);
        });

        heroPlayBtn.onclick = () => openVideoModal(fullMovie);
        heroListBtn.onclick = () => toggleWatchlist(fullMovie);
        heroInfoBtn.onclick = () => openMovieModal(fullMovie);
    }

    function startHeroAutoRotate() {
        if (heroAutoInterval) clearInterval(heroAutoInterval);
        heroAutoInterval = setInterval(() => {
            if (heroesList.length === 0) return;
            const nextIndex = (currentHeroIndex + 1) % heroesList.length;
            updateHero(nextIndex);
        }, 7000);
    }

    window.openHeroTrailer = function() {
        if (heroesList.length === 0) return;
        const hero = heroesList[currentHeroIndex];
        const fullMovie = moviesList.find(m => m.id === hero.id) || hero;
        openVideoModal(fullMovie);
    };

    // ==========================================
    // 4. VIDEO TRAILER MODAL
    // ==========================================

    function openVideoModal(movie) {
        if (!movie) return;
        activeMovie = movie;

        videoPlayerTitle.textContent = `${movie.title} (Official Trailer)`;
        const trailerId = movie.trailerId || movie.trailer_id || "b9EkMc79ZSU";
        trailerIframe.src = `https://www.youtube-nocookie.com/embed/${trailerId}?autoplay=1&rel=0&modestbranding=1`;

        videoModal.style.display = "flex";
        document.body.style.overflow = "hidden";

        // Record view count on backend if connected
        if (isBackendConnected && movie.id) {
            fetch(`${API_BASE}/movies/${movie.id}/view`, { method: "POST" }).catch(() => {});
        }
    }

    function closeVideoModal() {
        trailerIframe.src = "";
        videoModal.style.display = "none";
        document.body.style.overflow = "";
    }

    closeVideoModalBtn.addEventListener("click", closeVideoModal);
    videoModal.addEventListener("click", (e) => {
        if (e.target === videoModal) closeVideoModal();
    });

    // ==========================================
    // 5. MOVIE DETAILS MODAL
    // ==========================================

    function openMovieModal(movie) {
        if (!movie) return;
        activeMovie = movie;

        modalBanner.style.backgroundImage = `url('${movie.backdrop || movie.poster}')`;
        modalTitle.textContent = movie.title;
        modalMatch.textContent = `${movie.match || movie.match_score || 98}% Match`;
        modalYear.textContent = movie.year;
        modalAge.textContent = movie.age;
        modalDuration.textContent = movie.duration;
        modalQuality.textContent = movie.quality || "4K Ultra HD";
        modalDescription.textContent = movie.description;

        const castList = movie.cast || movie.cast_members || ["Featured Ensemble"];
        modalCast.textContent = Array.isArray(castList) ? castList.join(", ") : castList;

        const genreList = Array.isArray(movie.genres) ? movie.genres.join(", ") : movie.genres;
        modalGenres.textContent = genreList;
        modalDirector.textContent = movie.director || "Production Team";
        modalRating.textContent = `★ ${movie.rating} / 10 (IMDb)`;

        const inList = isMovieInWatchlist(movie.id);
        modalWatchlistBtn.textContent = inList ? "✓ In My List" : "+ Add to My List";

        modalPlayBtn.onclick = () => {
            closeMovieModal();
            openVideoModal(movie);
        };

        modalWatchlistBtn.onclick = () => {
            toggleWatchlist(movie);
            const updatedInList = isMovieInWatchlist(movie.id);
            modalWatchlistBtn.textContent = updatedInList ? "✓ In My List" : "+ Add to My List";
        };

        movieModal.style.display = "flex";
        document.body.style.overflow = "hidden";
    }

    function closeMovieModal() {
        movieModal.style.display = "none";
        document.body.style.overflow = "";
    }

    closeModalBtn.addEventListener("click", closeMovieModal);
    movieModal.addEventListener("click", (e) => {
        if (e.target === movieModal) closeMovieModal();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            if (videoModal.style.display === "flex") closeVideoModal();
            if (movieModal.style.display === "flex") closeMovieModal();
        }
    });

    // ==========================================
    // 6. WATCHLIST (LOCAL & BACKEND SYNC)
    // ==========================================

    function loadWatchlistLocal() {
        try {
            const saved = localStorage.getItem("shivastream_watchlist");
            return saved ? JSON.parse(saved) : [];
        } catch {
            return [];
        }
    }

    function saveWatchlistLocal() {
        try {
            localStorage.setItem("shivastream_watchlist", JSON.stringify(watchlist));
        } catch (e) {
            console.error("Local storage error:", e);
        }
    }

    function isMovieInWatchlist(id) {
        return watchlist.some(m => m.id === id);
    }

    async function toggleWatchlist(movie) {
        const index = watchlist.findIndex(m => m.id === movie.id);
        const willAdd = index === -1;

        if (willAdd) {
            watchlist.push(movie);
            showToast(`Added "${movie.title}" to My List`);
        } else {
            watchlist.splice(index, 1);
            showToast(`Removed "${movie.title}" from My List`);
        }

        saveWatchlistLocal();
        updateWatchlistUI();
        updateCardWatchlistButtons(movie.id);

        // Update hero button if current
        if (heroesList.length > 0) {
            const currentHero = heroesList[currentHeroIndex];
            if (currentHero && currentHero.id === movie.id) {
                heroListIcon.textContent = willAdd ? "✓" : "+";
                heroListText.textContent = willAdd ? "In My List" : "My List";
            }
        }

        // Sync with SQLite backend if online
        if (isBackendConnected) {
            try {
                if (willAdd) {
                    await fetch(`${API_BASE}/watchlist`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ movie_id: movie.id, user_id: 1 })
                    });
                } else {
                    await fetch(`${API_BASE}/watchlist/${movie.id}?user_id=1`, {
                        method: "DELETE"
                    });
                }
            } catch (err) {
                console.warn("Backend watchlist sync error:", err);
            }
        }
    }

    function updateCardWatchlistButtons(movieId) {
        const inList = isMovieInWatchlist(movieId);
        const buttons = document.querySelectorAll(`.movie-card[data-id="${movieId}"] .action-btn.watchlist`);
        buttons.forEach(btn => {
            btn.classList.toggle("active", inList);
            btn.textContent = inList ? "✓" : "+";
            btn.title = inList ? "Remove from My List" : "Add to My List";
        });
    }

    function updateWatchlistUI() {
        const count = watchlist.length;
        navWatchlistCount.textContent = count;
        watchlistCount.textContent = count;

        if (count > 0) {
            myListSection.style.display = "block";
            renderCarousel(myListContainer, watchlist);
        } else {
            myListSection.style.display = "none";
            myListContainer.innerHTML = "";
        }
    }

    // ==========================================
    // 7. CAROUSEL ARROWS
    // ==========================================

    function setupCarouselControls() {
        document.querySelectorAll(".carousel-nav").forEach(arrow => {
            arrow.addEventListener("click", () => {
                const targetId = arrow.getAttribute("data-target");
                const container = document.getElementById(targetId);
                if (!container) return;

                const isNext = arrow.classList.contains("next");
                const scrollDistance = container.clientWidth * 0.75;

                container.scrollBy({
                    left: isNext ? scrollDistance : -scrollDistance,
                    behavior: "smooth"
                });
            });
        });
    }

    // ==========================================
    // 8. SEARCH
    // ==========================================

    function setupSearchControls() {
        function handleSearch() {
            const query = searchInput.value.trim().toLowerCase();

            if (!query) {
                clearSearch();
                return;
            }

            clearSearchBtn.style.display = "block";

            const matches = moviesList.filter(movie => {
                const titleMatch = movie.title.toLowerCase().includes(query);
                const genres = Array.isArray(movie.genres) ? movie.genres : [];
                const genreMatch = genres.some(g => g.toLowerCase().includes(query));
                const cast = movie.cast || movie.cast_members || [];
                const castMatch = Array.isArray(cast) && cast.some(c => c.toLowerCase().includes(query));
                const directorMatch = movie.director && movie.director.toLowerCase().includes(query);
                return titleMatch || genreMatch || castMatch || directorMatch;
            });

            displaySearchResults(matches, query);
        }

        function displaySearchResults(results, query) {
            searchResultsSection.style.display = "block";
            searchResultsTitle.textContent = `Search Results for "${query}" (${results.length})`;
            searchGrid.innerHTML = "";

            if (results.length === 0) {
                searchGrid.innerHTML = `
                    <div class="no-results">
                        <h3>No Titles Found</h3>
                        <p>We couldn't find any matches for "<strong>${query}</strong>".</p>
                        <p style="margin-top: 8px; font-size: 13px; color: #888;">Try searching for "Batman", "Stranger Things", "Sci-Fi", or "Christopher Nolan".</p>
                    </div>
                `;
                return;
            }

            results.forEach(movie => {
                searchGrid.appendChild(createMovieCard(movie));
            });

            searchResultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }

        function clearSearch() {
            searchInput.value = "";
            clearSearchBtn.style.display = "none";
            searchResultsSection.style.display = "none";
            searchGrid.innerHTML = "";
        }

        searchInput.addEventListener("input", handleSearch);
        clearSearchBtn.addEventListener("click", clearSearch);
        closeSearchSection.addEventListener("click", clearSearch);
    }

    // ==========================================
    // 9. GENRE FILTER CHIPS
    // ==========================================

    function setupGenreFilterControls() {
        document.querySelectorAll(".filter-pill").forEach(pill => {
            pill.addEventListener("click", () => {
                document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
                pill.classList.add("active");

                const filter = pill.getAttribute("data-filter");

                if (filter === "all") {
                    document.getElementById("home").scrollIntoView({ behavior: "smooth" });
                    return;
                }

                if (filter === "movies") {
                    document.getElementById("movies").scrollIntoView({ behavior: "smooth" });
                    return;
                }

                if (filter === "series") {
                    document.getElementById("series").scrollIntoView({ behavior: "smooth" });
                    return;
                }

                if (filter === "trending") {
                    document.getElementById("trending").scrollIntoView({ behavior: "smooth" });
                    return;
                }

                // Filter by Genre
                const genreMatches = moviesList.filter(m => {
                    const genres = Array.isArray(m.genres) ? m.genres : [];
                    return genres.includes(filter);
                });

                searchInput.value = filter;
                clearSearchBtn.style.display = "block";

                searchResultsSection.style.display = "block";
                searchResultsTitle.textContent = `${filter} Titles (${genreMatches.length})`;
                searchGrid.innerHTML = "";

                genreMatches.forEach(movie => {
                    searchGrid.appendChild(createMovieCard(movie));
                });

                searchResultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
            });
        });
    }

    // ==========================================
    // 10. NAVBAR & TOAST
    // ==========================================

    function setupNavbarControls() {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 40) {
                mainNavbar.classList.add("scrolled");
            } else {
                mainNavbar.classList.remove("scrolled");
            }
        });

        mobileToggle.addEventListener("click", () => {
            navMenu.classList.toggle("show");
            mobileToggle.textContent = navMenu.classList.contains("show") ? "✕" : "☰";
        });

        document.querySelectorAll("#navMenu a").forEach(link => {
            link.addEventListener("click", () => {
                navMenu.classList.remove("show");
                mobileToggle.textContent = "☰";
            });
        });

        // Close mobile drawer when tapping outside
        document.addEventListener("click", (e) => {
            if (navMenu.classList.contains("show") && !navMenu.contains(e.target) && !mobileToggle.contains(e.target)) {
                navMenu.classList.remove("show");
                mobileToggle.textContent = "☰";
            }
        });
    }

    let toastTimer = null;
    function showToast(message) {
        if (toastTimer) clearTimeout(toastTimer);
        toastMessage.textContent = message;
        toastNotification.classList.add("show");

        toastTimer = setTimeout(() => {
            toastNotification.classList.remove("show");
        }, 2800);
    }

    // Launch Engine
    init();
});