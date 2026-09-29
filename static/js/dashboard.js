// dashboard.js - Handles User Dashboard Stats, Active Games, and Resume Game links

document.addEventListener("DOMContentLoaded", function () {
    const userWelcome = document.getElementById("user-welcome");
    const statTotal = document.getElementById("stat-total");
    const statWins = document.getElementById("stat-wins");
    const statLosses = document.getElementById("stat-losses");
    const statInProgress = document.getElementById("stat-inprogress");

    const activeGamesList = document.getElementById("active-games-list");
    const finishedGamesList = document.getElementById("finished-games-list");
    const logoutButton = document.getElementById("logout-button");

    const errorMessage = document.getElementById("error-message");
    const successMessage = document.getElementById("success-message");

    function showError(msg) {
        if (errorMessage) {
            errorMessage.textContent = msg;
            errorMessage.style.display = "block";
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
                    adminLink.style.color = "var(--accent-orange)";
                    adminLink.style.fontWeight = "600";
                    nav.insertBefore(adminLink, nav.firstChild);
                }
            }

            statTotal.textContent = data.stats.totalGames;
            statWins.textContent = data.stats.wins;
            statLosses.textContent = data.stats.losses;
            statInProgress.textContent = data.stats.inProgress;

            // Separate Games into Active (IN_PROGRESS) and Finished (WON/LOST)
            const activeGames = data.games.filter(g => g.status === "IN_PROGRESS");
            const finishedGames = data.games.filter(g => g.status !== "IN_PROGRESS");

            // Render Active / Unfinished Games
            if (activeGames.length === 0) {
                activeGamesList.innerHTML = `<p style="color: var(--text-muted);">No active games in progress. Click 'Start New Game' to play!</p>`;
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
                            <td>#${g.gameId}</td>
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

            // Render Recent Finished Games
            if (finishedGames.length === 0) {
                finishedGamesList.innerHTML = `<p style="color: var(--text-muted);">No completed games yet.</p>`;
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
                            <td>#${g.gameId}</td>
                            <td>${startedDate}</td>
                            <td>${completedDate}</td>
                            <td><span class="badge ${badgeClass}">${g.status}</span></td>
                        </tr>
                    `;
                });

                html += `</tbody></table></div>`;
                finishedGamesList.innerHTML = html;
            }

        } catch (error) {
            showError("Unable to load dashboard data. Please log in again.");
        }
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
