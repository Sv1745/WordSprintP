// admin.js - Handles Admin Dashboard, Reports, and System Configuration

document.addEventListener("DOMContentLoaded", function () {
    const statPlayers = document.getElementById("stat-players");
    const statAdmins = document.getElementById("stat-admins");
    const statGames = document.getElementById("stat-games");
    const statWon = document.getElementById("stat-won");
    const statLost = document.getElementById("stat-lost");
    const statProgress = document.getElementById("stat-progress");

    const playerReportsContainer = document.getElementById("player-reports-container");
    const configForm = document.getElementById("config-form");
    const maxAttemptsInput = document.getElementById("max-attempts");
    const maxDailyInput = document.getElementById("max-daily");
    const gameEnabledCheckbox = document.getElementById("game-enabled");
    const logoutButton = document.getElementById("logout-button");

    const errorMessage = document.getElementById("error-message");
    const successMessage = document.getElementById("success-message");

    function clearMessages() {
        if (errorMessage) {
            errorMessage.style.display = "none";
            errorMessage.textContent = "";
        }
        if (successMessage) {
            successMessage.style.display = "none";
            successMessage.textContent = "";
        }
    }

    function showError(msg) {
        clearMessages();
        if (errorMessage) {
            errorMessage.textContent = msg;
            errorMessage.style.display = "block";
        }
    }

    function showSuccess(msg) {
        clearMessages();
        if (successMessage) {
            successMessage.textContent = msg;
            successMessage.style.display = "block";
        }
    }

    async function loadReports() {
        try {
            const response = await fetch("/wordsprint/admin/reports");
            if (response.status === 401) {
                window.location.href = "login.html";
                return;
            }
            if (response.status === 403) {
                showError("Access Denied: Admin privileges required.");
                setTimeout(() => window.location.href = "dashboard.html", 2000);
                return;
            }

            const data = await response.json();
            if (!response.ok || !data.success) {
                showError(data.message || "Failed to load admin reports.");
                return;
            }

            // Populate Overview Stats
            statPlayers.textContent = data.stats.totalPlayers;
            statAdmins.textContent = data.stats.totalAdmins;
            statGames.textContent = data.stats.totalGames;
            statWon.textContent = data.stats.wonGames;
            statLost.textContent = data.stats.lostGames;
            statProgress.textContent = data.stats.inProgressGames;

            // Render Daily Activity Report Table (Date, Number of Users, Number of Correct Guesses)
            const dailyReportsContainer = document.getElementById("daily-reports-container");
            if (dailyReportsContainer) {
                if (!data.dailyReports || data.dailyReports.length === 0) {
                    dailyReportsContainer.innerHTML = `<p style="color: #6c757d;">No daily game activity recorded yet.</p>`;
                } else {
                    let dHtml = `
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Number of Users</th>
                                    <th>Number of Correct Guesses</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    data.dailyReports.forEach(dr => {
                        dHtml += `
                            <tr>
                                <td><strong>${dr.date}</strong></td>
                                <td>${dr.activeUsers}</td>
                                <td style="color: #2ecc71; font-weight: 600;">${dr.correctGuesses}</td>
                            </tr>
                        `;
                    });
                    dHtml += `</tbody></table>`;
                    dailyReportsContainer.innerHTML = dHtml;
                }
            }

            // Render User Daily Activity Report Table (User, Date, Words Tried, Correct Guesses)
            const userDailyReportsContainer = document.getElementById("user-daily-reports-container");
            if (userDailyReportsContainer) {
                if (!data.userDailyReports || data.userDailyReports.length === 0) {
                    userDailyReportsContainer.innerHTML = `<p style="color: #6c757d;">No user daily activity recorded yet.</p>`;
                } else {
                    let uHtml = `
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Username</th>
                                    <th>Date</th>
                                    <th>Number of Words Tried</th>
                                    <th>Number of Correct Guesses</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    data.userDailyReports.forEach(udr => {
                        uHtml += `
                            <tr>
                                <td><strong>${udr.username}</strong></td>
                                <td>${udr.date}</td>
                                <td>${udr.wordsTried}</td>
                                <td style="color: #2ecc71; font-weight: 600;">${udr.correctGuesses}</td>
                            </tr>
                        `;
                    });
                    uHtml += `</tbody></table>`;
                    userDailyReportsContainer.innerHTML = uHtml;
                }
            }

            // Render Player Directory & Analytics Table
            if (!data.reports || data.reports.length === 0) {
                playerReportsContainer.innerHTML = `<p style="color: #6c757d;">No registered users found.</p>`;
            } else {
                let html = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>User ID</th>
                                <th>Username</th>
                                <th>Role</th>
                                <th>Joined</th>
                                <th>Total Games</th>
                                <th>Wins</th>
                                <th>Losses</th>
                                <th>In-Progress</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                data.reports.forEach(r => {
                    const joinedDate = new Date(r.createdAt).toLocaleDateString();
                    const roleBadge = r.role === "admin" ? "badge-won" : "badge-progress";

                    html += `
                        <tr>
                            <td>#${r.userId}</td>
                            <td><strong>${r.username}</strong></td>
                            <td><span class="badge ${roleBadge}">${r.role}</span></td>
                            <td>${joinedDate}</td>
                            <td>${r.totalGames}</td>
                            <td style="color: #2ecc71; font-weight: 600;">${r.wins}</td>
                            <td style="color: #e74c3c; font-weight: 600;">${r.losses}</td>
                            <td style="color: #f1c40f; font-weight: 600;">${r.inProgress}</td>
                        </tr>
                    `;
                });

                html += `</tbody></table>`;
                playerReportsContainer.innerHTML = html;
            }

        } catch (error) {
            showError("Unable to load admin report data.");
        }
    }

    async function loadConfig() {
        try {
            const response = await fetch("/wordsprint/admin/config");
            if (!response.ok) return;

            const data = await response.json();
            if (data.success) {
                maxAttemptsInput.value = data.maxAttempts;
                maxDailyInput.value = data.maxDailyGames;
                gameEnabledCheckbox.checked = data.gameEnabled;
            }
        } catch (error) {
            // Ignore config load error
        }
    }

    if (configForm) {
        configForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            clearMessages();

            const maxAttempts = maxAttemptsInput.value;
            const maxDailyGames = maxDailyInput.value;
            const gameEnabled = gameEnabledCheckbox.checked;

            try {
                const response = await fetch("/wordsprint/admin/config", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams({
                        maxAttempts: maxAttempts,
                        maxDailyGames: maxDailyGames,
                        gameEnabled: gameEnabled
                    })
                });

                const data = await response.json();
                if (response.ok && data.success) {
                    showSuccess(data.message || "Configuration saved successfully!");
                } else {
                    showError(data.message || "Failed to update configuration.");
                }
            } catch (error) {
                showError("Error saving configuration.");
            }
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

    loadReports();
    loadConfig();
});
