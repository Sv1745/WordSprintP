// dashboard.js - Handles User Dashboard Stats, Daily Games Remaining, Filtering, and Active Games

document.addEventListener("DOMContentLoaded", function () {
    const userWelcome = document.getElementById("user-welcome");
    const statTotal = document.getElementById("stat-total");
    const statWins = document.getElementById("stat-wins");
    const statLosses = document.getElementById("stat-losses");
    const statInProgress = document.getElementById("stat-inprogress");
    const statDailyLeft = document.getElementById("stat-daily-left");

    const activeGamesList = document.getElementById("active-games-list");
    const finishedGamesList = document.getElementById("finished-games-list");
    const activeCountBadge = document.getElementById("active-count-badge");
    const finishedCountBadge = document.getElementById("finished-count-badge");

    const historyDateFilter = document.getElementById("history-date-filter");
    const historyStatusFilter = document.getElementById("history-status-filter");
    const historyResetBtn = document.getElementById("history-reset-btn");

    const logoutButton = document.getElementById("logout-button");
    const errorMessage = document.getElementById("error-message");
    const successMessage = document.getElementById("success-message");

    let allUserGames = [];

    function showError(msg) {
        if (errorMessage) {
            errorMessage.textContent = msg;
            errorMessage.style.display = "block";
        }
    }

    function formatDateToYMD(dateString) {
        if (!dateString) return "";
        try {
            const d = new Date(dateString);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, "0");
            const day = String(d.getDate()).padStart(2, "0");
            return `${year}-${month}-${day}`;
        } catch (e) {
            return "";
        }
    }

    function renderFilteredGames() {
        const selectedDate = historyDateFilter ? historyDateFilter.value.trim() : "";
        const selectedStatus = historyStatusFilter ? historyStatusFilter.value.trim().toUpperCase() : "ALL";

        const filtered = allUserGames.filter(g => {
            // Date Filter Check
            if (selectedDate) {
                const gameDate = formatDateToYMD(g.startedAt);
                if (gameDate !== selectedDate) return false;
            }
            // Status Filter Check
            if (selectedStatus && selectedStatus !== "ALL") {
                if (g.status.toUpperCase() !== selectedStatus) return false;
            }
            return true;
        });

        const activeGames = filtered.filter(g => g.status === "IN_PROGRESS");
        const finishedGames = filtered.filter(g => g.status !== "IN_PROGRESS");

        if (activeCountBadge) {
            activeCountBadge.textContent = `${activeGames.length} active`;
        }
        if (finishedCountBadge) {
            finishedCountBadge.textContent = `${finishedGames.length} completed`;
        }

        // Render Active Games
        if (activeGames.length === 0) {
            activeGamesList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No active games found matching the selected filters.</p>`;
        } else {
            let html = `
                <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Game ID</th>
                            <th>Started At</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            activeGames.forEach(g => {
                const startedDate = new Date(g.startedAt).toLocaleString();
                html += `
                    <tr>
                        <td><strong>#${g.gameId}</strong></td>
                        <td>${startedDate}</td>
                        <td><span class="badge badge-progress">IN PROGRESS</span></td>
                        <td>
                            <a href="game.html?gameId=${g.gameId}" class="btn btn-primary btn-sm">Resume Game</a>
                        </td>
                    </tr>
                `;
            });

            html += `</tbody></table></div>`;
            activeGamesList.innerHTML = html;
        }

        // Render Finished Games
        if (finishedGames.length === 0) {
            finishedGamesList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No completed match history found matching the selected filters.</p>`;
        } else {
            let html = `
                <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Game ID</th>
                            <th>Started At</th>
                            <th>Completed At</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            finishedGames.forEach(g => {
                const startedDate = new Date(g.startedAt).toLocaleString();
                const completedDate = g.completedAt ? new Date(g.completedAt).toLocaleString() : "-";
                const badgeClass = g.status === "WON" ? "badge-won" : "badge-lost";

                html += `
                    <tr>
                        <td><strong>#${g.gameId}</strong></td>
                        <td>${startedDate}</td>
                        <td>${completedDate}</td>
                        <td><span class="badge ${badgeClass}">${g.status}</span></td>
                    </tr>
                `;
            });

            html += `</tbody></table></div>`;
            finishedGamesList.innerHTML = html;
        }
    }

    async function loadDashboard() {
        try {
            const response = await fetch("/wordsprint/profile");
            if (response.status === 401) {
                window.location.href = "login.html";
                return;
            }

            const data = await response.json();
            if (!response.ok || !data.success) {
                showError(data.message || "Failed to load dashboard.");
                return;
            }

            // Render User Header & Stats
            userWelcome.textContent = `Welcome, ${data.username}!`;
            if (data.role === "admin") {
                const nav = document.querySelector("nav");
                if (nav && !document.getElementById("nav-admin-link")) {
                    const adminLink = document.createElement("a");
                    adminLink.id = "nav-admin-link";
                    adminLink.href = "admin.html";
                    adminLink.textContent = "Admin Panel";
                    adminLink.style.color = "var(--accent-orange, #f59e0b)";
                    adminLink.style.fontWeight = "700";
                    nav.insertBefore(adminLink, nav.firstChild);
                }
            }

            statTotal.textContent = data.stats.totalGames;
            statWins.textContent = data.stats.wins;
            statLosses.textContent = data.stats.losses;
            statInProgress.textContent = data.stats.inProgress;

            // Render Daily Games Left
            if (statDailyLeft) {
                const maxDaily = data.stats.maxDailyGames !== undefined ? data.stats.maxDailyGames : 3;
                const dailyLeft = data.stats.dailyGamesLeft !== undefined ? data.stats.dailyGamesLeft : Math.max(0, maxDaily - (data.stats.gamesToday || 0));
                statDailyLeft.textContent = `${dailyLeft} / ${maxDaily}`;
                statDailyLeft.title = `${dailyLeft} games remaining today out of ${maxDaily} allowed daily games.`;
            }

            allUserGames = data.games || [];
            renderFilteredGames();

        } catch (error) {
            showError("Unable to load dashboard data. Please log in again.");
        }
    }

    // Attach Filter Event Listeners
    if (historyDateFilter) {
        historyDateFilter.addEventListener("change", renderFilteredGames);
    }

    if (historyStatusFilter) {
        historyStatusFilter.addEventListener("change", renderFilteredGames);
    }

    if (historyResetBtn) {
        historyResetBtn.addEventListener("click", function () {
            if (historyDateFilter) historyDateFilter.value = "";
            if (historyStatusFilter) historyStatusFilter.value = "ALL";
            renderFilteredGames();
        });
    }

    if (logoutButton) {
        logoutButton.addEventListener("click", async function () {
            try {
                await fetch("/wordsprint/logout", { method: "POST" });
            } finally {
                window.location.href = "login.html";
            }
        });
    }

    loadDashboard();
});
