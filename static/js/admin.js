// admin.js - Handles Admin Dashboard, Reports, Date/Status Filtering, and System Configuration

document.addEventListener("DOMContentLoaded", function () {
    const statPlayers = document.getElementById("stat-players");
    const statAdmins = document.getElementById("stat-admins");
    const statGames = document.getElementById("stat-games");
    const statWon = document.getElementById("stat-won");
    const statLost = document.getElementById("stat-lost");
    const statProgress = document.getElementById("stat-progress");

    const matchReportsContainer = document.getElementById("match-reports-container");
    const dailyReportsContainer = document.getElementById("daily-reports-container");
    const userDailyReportsContainer = document.getElementById("user-daily-reports-container");
    const playerReportsContainer = document.getElementById("player-reports-container");

    const matchCountBadge = document.getElementById("match-count-badge");
    const dailyCountBadge = document.getElementById("daily-count-badge");
    const userDailyCountBadge = document.getElementById("user-daily-count-badge");
    const playerCountBadge = document.getElementById("player-count-badge");

    const adminDateFilter = document.getElementById("admin-date-filter");
    const adminStatusFilter = document.getElementById("admin-status-filter");
    const adminSearchFilter = document.getElementById("admin-search-filter");
    const adminResetFilterBtn = document.getElementById("admin-reset-filter-btn");

    const configForm = document.getElementById("config-form");
    const maxAttemptsInput = document.getElementById("max-attempts");
    const maxDailyInput = document.getElementById("max-daily");
    const gameEnabledCheckbox = document.getElementById("game-enabled");
    const logoutButton = document.getElementById("logout-button");

    const errorMessage = document.getElementById("error-message");
    const successMessage = document.getElementById("success-message");

    // In-memory data store for client-side filtering
    let rawData = {
        stats: {},
        matchReports: [],
        dailyReports: [],
        userDailyReports: [],
        reports: []
    };

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

    function formatDateToYMD(dateString) {
        if (!dateString) return "";
        try {
            const d = new Date(dateString);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, "0");
            const day = String(d.getDate()).padStart(2, "0");
            return `${year}-${month}-${day}`;
        } catch (e) {
            return String(dateString).slice(0, 10);
        }
    }

    function renderAllFilteredReports() {
        const selectedDate = adminDateFilter ? adminDateFilter.value.trim() : "";
        const selectedStatus = adminStatusFilter ? adminStatusFilter.value.trim().toUpperCase() : "ALL";
        const searchUser = adminSearchFilter ? adminSearchFilter.value.trim().toLowerCase() : "";

        // 1. Render Match Activity Report
        if (matchReportsContainer) {
            const filteredMatches = (rawData.matchReports || []).filter(m => {
                if (selectedDate) {
                    const matchDate = formatDateToYMD(m.startedAt);
                    if (matchDate !== selectedDate) return false;
                }
                if (selectedStatus && selectedStatus !== "ALL") {
                    if (String(m.status).toUpperCase() !== selectedStatus) return false;
                }
                if (searchUser) {
                    if (!String(m.username).toLowerCase().includes(searchUser)) return false;
                }
                return true;
            });

            if (matchCountBadge) {
                matchCountBadge.textContent = `${filteredMatches.length} of ${rawData.matchReports.length} matches`;
            }

            if (filteredMatches.length === 0) {
                matchReportsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No match records found matching the selected filters.</p>`;
            } else {
                let mHtml = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Game ID</th>
                                <th>Player</th>
                                <th>Target Word</th>
                                <th>Attempts</th>
                                <th>Started At</th>
                                <th>Completed At</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                filteredMatches.forEach(m => {
                    const started = new Date(m.startedAt).toLocaleString();
                    const completed = m.completedAt && m.completedAt !== "-" ? new Date(m.completedAt).toLocaleString() : "-";
                    let badgeClass = "badge-progress";
                    if (m.status === "WON") badgeClass = "badge-won";
                    else if (m.status === "LOST") badgeClass = "badge-lost";

                    mHtml += `
                        <tr>
                            <td><strong>#${m.gameId}</strong></td>
                            <td><strong>${m.username}</strong></td>
                            <td><span style="font-family: monospace; font-weight: 700; color: var(--brand-blue);">${m.word || "-"}</span></td>
                            <td>${m.attempts !== undefined ? m.attempts : "-"}</td>
                            <td>${started}</td>
                            <td>${completed}</td>
                            <td><span class="badge ${badgeClass}">${m.status}</span></td>
                        </tr>
                    `;
                });
                mHtml += `</tbody></table>`;
                matchReportsContainer.innerHTML = mHtml;
            }
        }

        // 2. Render Daily System Activity Report
        if (dailyReportsContainer) {
            const filteredDaily = (rawData.dailyReports || []).filter(dr => {
                if (selectedDate) {
                    const drDate = formatDateToYMD(dr.date);
                    if (drDate !== selectedDate) return false;
                }
                return true;
            });

            if (dailyCountBadge) {
                dailyCountBadge.textContent = `${filteredDaily.length} days recorded`;
            }

            if (filteredDaily.length === 0) {
                dailyReportsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No daily activity found for selected date.</p>`;
            } else {
                let dHtml = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Number of Active Users</th>
                                <th>Won Games / Correct Guesses</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                filteredDaily.forEach(dr => {
                    dHtml += `
                        <tr>
                            <td><strong>${dr.date}</strong></td>
                            <td>${dr.activeUsers}</td>
                            <td style="color: var(--tile-green); font-weight: 700;">${dr.correctGuesses}</td>
                        </tr>
                    `;
                });
                dHtml += `</tbody></table>`;
                dailyReportsContainer.innerHTML = dHtml;
            }
        }

        // 3. Render User Daily Activity Report
        if (userDailyReportsContainer) {
            const filteredUserDaily = (rawData.userDailyReports || []).filter(udr => {
                if (selectedDate) {
                    const udrDate = formatDateToYMD(udr.date);
                    if (udrDate !== selectedDate) return false;
                }
                if (searchUser) {
                    if (!String(udr.username).toLowerCase().includes(searchUser)) return false;
                }
                return true;
            });

            if (userDailyCountBadge) {
                userDailyCountBadge.textContent = `${filteredUserDaily.length} entries`;
            }

            if (filteredUserDaily.length === 0) {
                userDailyReportsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No user daily activity found matching filters.</p>`;
            } else {
                let uHtml = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Date</th>
                                <th>Number of Words Tried</th>
                                <th>Correct Guesses</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                filteredUserDaily.forEach(udr => {
                    uHtml += `
                        <tr>
                            <td><strong>${udr.username}</strong></td>
                            <td>${udr.date}</td>
                            <td>${udr.wordsTried}</td>
                            <td style="color: var(--tile-green); font-weight: 700;">${udr.correctGuesses}</td>
                        </tr>
                    `;
                });
                uHtml += `</tbody></table>`;
                userDailyReportsContainer.innerHTML = uHtml;
            }
        }

        // 4. Render User Directory Summary
        if (playerReportsContainer) {
            const filteredPlayers = (rawData.reports || []).filter(r => {
                if (searchUser) {
                    if (!String(r.username).toLowerCase().includes(searchUser)) return false;
                }
                if (selectedStatus && selectedStatus !== "ALL") {
                    if (selectedStatus === "WON" && (r.wins || 0) === 0) return false;
                    if (selectedStatus === "LOST" && (r.losses || 0) === 0) return false;
                    if (selectedStatus === "IN_PROGRESS" && (r.inProgress || 0) === 0) return false;
                }
                return true;
            });

            if (playerCountBadge) {
                playerCountBadge.textContent = `${filteredPlayers.length} users`;
            }

            if (filteredPlayers.length === 0) {
                playerReportsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No users found matching filters.</p>`;
            } else {
                let pHtml = `
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
                filteredPlayers.forEach(r => {
                    const joinedDate = new Date(r.createdAt).toLocaleDateString();
                    const roleBadge = r.role === "admin" ? "badge-won" : "badge-progress";

                    pHtml += `
                        <tr>
                            <td>#${r.userId}</td>
                            <td><strong>${r.username}</strong></td>
                            <td><span class="badge ${roleBadge}">${r.role}</span></td>
                            <td>${joinedDate}</td>
                            <td>${r.totalGames}</td>
                            <td style="color: var(--tile-green); font-weight: 700;">${r.wins}</td>
                            <td style="color: var(--btn-danger-bg); font-weight: 700;">${r.losses}</td>
                            <td style="color: var(--tile-yellow); font-weight: 700;">${r.inProgress}</td>
                        </tr>
                    `;
                });
                pHtml += `</tbody></table>`;
                playerReportsContainer.innerHTML = pHtml;
            }
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

            rawData = {
                stats: data.stats || {},
                matchReports: data.matchReports || [],
                dailyReports: data.dailyReports || [],
                userDailyReports: data.userDailyReports || [],
                reports: data.reports || []
            };

            // Populate Overview Stats
            statPlayers.textContent = data.stats.totalPlayers || 0;
            statAdmins.textContent = data.stats.totalAdmins || 0;
            statGames.textContent = data.stats.totalGames || 0;
            statWon.textContent = data.stats.wonGames || 0;
            statLost.textContent = data.stats.lostGames || 0;
            statProgress.textContent = data.stats.inProgressGames || 0;

            renderAllFilteredReports();

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

    // Filter event listeners
    if (adminDateFilter) {
        adminDateFilter.addEventListener("change", renderAllFilteredReports);
    }

    if (adminStatusFilter) {
        adminStatusFilter.addEventListener("change", renderAllFilteredReports);
    }

    if (adminSearchFilter) {
        adminSearchFilter.addEventListener("input", renderAllFilteredReports);
    }

    if (adminResetFilterBtn) {
        adminResetFilterBtn.addEventListener("click", function () {
            if (adminDateFilter) adminDateFilter.value = "";
            if (adminStatusFilter) adminStatusFilter.value = "ALL";
            if (adminSearchFilter) adminSearchFilter.value = "";
            renderAllFilteredReports();
        });
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
