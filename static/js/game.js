// game.js - Handles WordSprint Game Interface, Guesses, and Session Logout

document.addEventListener("DOMContentLoaded", function () {
    // Current active game state
    let currentGameId = null;
    let currentAttempt = 0;
    let maxAttempts = 6;
    let letterStates = {};

    // DOM Elements
    const startGameButton = document.getElementById("start-game-button");
    const guessForm = document.getElementById("guess-form");
    const guessInput = document.getElementById("guess-input");
    const logoutButton = document.getElementById("logout-button");

    const attemptCountText = document.getElementById("attempt-count");
    const maxAttemptsCountText = document.getElementById("max-attempts-count");
    const gameStatusText = document.getElementById("game-status");
    const errorMessage = document.getElementById("error-message");
    const successMessage = document.getElementById("success-message");
    const startSection = document.getElementById("start-section");

    // Helper to update status pill UI
    function setGameStatus(statusStr) {
        if (!gameStatusText) return;
        gameStatusText.textContent = statusStr;
        const normalized = (statusStr || "IDLE").toLowerCase().replace(/_/g, "-");
        gameStatusText.className = "status-pill status-" + normalized;
    }

    // Clear alert messages
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

    // Display error message
    function showError(message) {
        clearMessages();
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = "block";
        }
    }

    // Display success message
    function showSuccess(message) {
        clearMessages();
        if (successMessage) {
            successMessage.textContent = message;
            successMessage.style.display = "block";
        }
    }

    // Live Tile Row Typing Preview
    function updateActiveRowPreview() {
        if (!currentGameId || currentAttempt < 0 || (currentAttempt + 1) > maxAttempts) return;
        const activeAttemptNum = currentAttempt + 1;
        const row = document.querySelector(`.board-row[data-row="${activeAttemptNum}"]`);
        if (!row) return;

        const tiles = row.querySelectorAll(".tile");
        if (tiles.length === 0 || tiles[0].classList.contains("tile-green") || tiles[0].classList.contains("tile-yellow") || tiles[0].classList.contains("tile-grey")) {
            return;
        }

        const text = guessInput ? guessInput.value.toUpperCase() : "";
        for (let i = 0; i < 5; i++) {
            const letter = text.charAt(i) || "";
            tiles[i].textContent = letter;
        }
    }

    if (guessInput) {
        guessInput.addEventListener("input", function () {
            guessInput.value = guessInput.value.toUpperCase();
            updateActiveRowPreview();
        });
    }

    // Update letter color states for the 26 English letters tracker keyboard
    function updateKeyboard(guessWord, resultFeedback) {
        if (!guessWord || !resultFeedback) return;
        const priority = { 'G': 3, 'Y': 2, 'B': 1 };

        const word = guessWord.toUpperCase().trim();
        const feedback = resultFeedback.toUpperCase().trim();

        for (let i = 0; i < word.length && i < feedback.length; i++) {
            const letter = word.charAt(i);
            const feedbackChar = feedback.charAt(i);

            if (letter >= 'A' && letter <= 'Z') {
                const currentPriority = priority[letterStates[letter]] || 0;
                const newPriority = priority[feedbackChar] || 0;

                if (newPriority > currentPriority) {
                    letterStates[letter] = feedbackChar;
                }
            }
        }

        renderKeyboardState();
    }

    // Render CSS classes and inline styles on keyboard letter buttons
    function renderKeyboardState() {
        const keys = document.querySelectorAll(".key[data-key]");
        keys.forEach(key => {
            const letter = (key.getAttribute("data-key") || "").toUpperCase();
            if (letter.length === 1 && letter >= 'A' && letter <= 'Z') {
                const state = letterStates[letter];
                key.classList.remove("key-green", "key-yellow", "key-grey");
                if (state === 'G') {
                    key.classList.add("key-green");
                    key.style.backgroundColor = "#059669";
                    key.style.borderColor = "#059669";
                    key.style.color = "#ffffff";
                    key.style.opacity = "1";
                } else if (state === 'Y') {
                    key.classList.add("key-yellow");
                    key.style.backgroundColor = "#d97706";
                    key.style.borderColor = "#d97706";
                    key.style.color = "#ffffff";
                    key.style.opacity = "1";
                } else if (state === 'B') {
                    key.classList.add("key-grey");
                    key.style.backgroundColor = "#64748b";
                    key.style.borderColor = "#64748b";
                    key.style.color = "#ffffff";
                    key.style.opacity = "0.6";
                } else {
                    key.style.backgroundColor = "";
                    key.style.borderColor = "";
                    key.style.color = "";
                    key.style.opacity = "";
                }
            }
        });
    }

    // Reset letter states and keyboard key colors
    function resetKeyboardState() {
        letterStates = {};
        const keys = document.querySelectorAll(".key[data-key]");
        keys.forEach(key => {
            key.classList.remove("key-green", "key-yellow", "key-grey");
            key.style.backgroundColor = "";
            key.style.borderColor = "";
            key.style.color = "";
            key.style.opacity = "";
        });
    }

    // Attach click listeners for on-screen 26-letter keyboard
    function initKeyboardListeners() {
        const keyboardContainer = document.getElementById("keyboard-container");
        if (!keyboardContainer) return;

        keyboardContainer.addEventListener("click", function (event) {
            const keyBtn = event.target.closest(".key");
            if (!keyBtn) return;

            event.preventDefault();

            const keyValue = (keyBtn.getAttribute("data-key") || "").toUpperCase();
            if (!keyValue) return;

            if (keyValue === "ENTER") {
                if (!currentGameId) {
                    startNewGame();
                    return;
                }
                if (guessForm && guessForm.style.display !== "none") {
                    handleGuessSubmit(new Event("submit"));
                }
            } else if (keyValue === "BACKSPACE") {
                if (guessInput) {
                    guessInput.value = guessInput.value.slice(0, -1);
                    updateActiveRowPreview();
                    guessInput.focus();
                }
            } else if (keyValue.length === 1 && keyValue >= 'A' && keyValue <= 'Z') {
                if (!currentGameId) {
                    showError("Please click 'Start New Game' to play.");
                    return;
                }
                if (guessInput && guessInput.value.length < 5) {
                    guessInput.value = (guessInput.value + keyValue).toUpperCase();
                    updateActiveRowPreview();
                    guessInput.focus();
                }
            }
        });
    }

    initKeyboardListeners();

    // Global physical keyboard listener for frictionless typing anywhere on the page
    window.addEventListener("keydown", function (event) {
        if (event.ctrlKey || event.altKey || event.metaKey) return;

        const activeEl = document.activeElement;
        if (activeEl && (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA") && activeEl !== guessInput) {
            return;
        }

        const key = event.key;

        if (key === "Enter") {
            if (guessForm && guessForm.style.display !== "none") {
                event.preventDefault();
                handleGuessSubmit(new Event("submit"));
            }
        } else if (key === "Backspace") {
            if (guessInput && guessForm && guessForm.style.display !== "none") {
                event.preventDefault();
                guessInput.value = guessInput.value.slice(0, -1);
                updateActiveRowPreview();
            }
        } else if (/^[a-zA-Z]$/.test(key)) {
            if (guessInput && guessForm && guessForm.style.display !== "none" && guessInput.value.length < 5) {
                event.preventDefault();
                guessInput.value = (guessInput.value + key).toUpperCase();
                updateActiveRowPreview();
            }
        }
    });

    // Render/Reset the game board grid dynamically based on row count
    function renderBoard(numRows) {
        const rows = numRows || maxAttempts;
        if (maxAttemptsCountText) {
            maxAttemptsCountText.textContent = maxAttempts;
        }

        const boardContainer = document.getElementById("game-board");
        if (!boardContainer) return;

        boardContainer.innerHTML = "";
        for (let r = 1; r <= rows; r++) {
            const rowDiv = document.createElement("div");
            rowDiv.className = "board-row";
            rowDiv.setAttribute("data-row", r);

            for (let t = 0; t < 5; t++) {
                const tileDiv = document.createElement("div");
                tileDiv.className = "tile";
                rowDiv.appendChild(tileDiv);
            }
            boardContainer.appendChild(rowDiv);
        }
    }

    // Initial board render with default maxAttempts (6)
    renderBoard(maxAttempts);

    // Fetch live game config on page load to update maxAttempts immediately
    async function fetchInitialConfig() {
        try {
            const response = await fetch("/wordsprint/game?action=config");
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.maxAttempts) {
                    renderBoard(data.maxAttempts);
                }
            }
        } catch (e) {
            // Silence error
        }
    }
    fetchInitialConfig();

    // Update a specific row on the board with guess letters and feedback colors
    function updateRow(rowNumber, guessWord, resultFeedback) {
        const row = document.querySelector(`.board-row[data-row="${rowNumber}"]`);
        if (!row) return;

        const tiles = row.querySelectorAll(".tile");
        for (let i = 0; i < 5; i++) {
            const letter = guessWord.charAt(i).toUpperCase();
            const feedbackChar = resultFeedback.charAt(i);

            tiles[i].textContent = letter;

            // Apply feedback class based on backend response character
            if (feedbackChar === 'G') {
                tiles[i].classList.add("tile-green");
            } else if (feedbackChar === 'Y') {
                tiles[i].classList.add("tile-yellow");
            } else {
                tiles[i].classList.add("tile-grey");
            }
        }
    }

    // Start a New Game
    async function startNewGame() {
        clearMessages();

        try {
            const response = await fetch("/wordsprint/game", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    action: "start"
                })
            });

            let data = {};
            try {
                data = await response.json();
            } catch (e) {
                // Response was not JSON (e.g. Tomcat HTML error page)
            }

            if (response.ok && data.success) {
                currentGameId = data.gameId || data.game_id;
                currentAttempt = 0;
                resetKeyboardState();

                if (data.maxAttempts) {
                    maxAttempts = data.maxAttempts;
                }
                renderBoard(maxAttempts);

                attemptCountText.textContent = "0";
                setGameStatus("IN_PROGRESS");

                guessForm.style.display = "flex";
                startSection.style.display = "none";
                guessInput.value = "";
                guessInput.focus();

                showSuccess("Game started! Make your first guess.");
            } else if (response.status === 403) {
                showError(data.message || "Daily game limit reached for today.");
            } else if (response.status === 401) {
                showError(data.message || "Please log in first to play WordSprint.");
                setTimeout(() => window.location.href = "login.html", 1500);
            } else {
                showError(data.message || "Unable to start game. Please try again.");
            }
        } catch (error) {
            showError("Network or server error while starting game.");
        }
    }

    // Submit a Word Guess
    async function handleGuessSubmit(event) {
        if (event && event.preventDefault) {
            event.preventDefault();
        }
        clearMessages();

        if (!currentGameId) {
            showError("No active game found. Please click 'Start New Game'.");
            return;
        }

        const guessWord = guessInput.value.trim().toUpperCase();

        if (guessWord.length !== 5) {
            showError("Please enter a valid 5-letter word.");
            return;
        }

        currentAttempt++;

        try {
            const response = await fetch("/wordsprint/guess", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    gameId: currentGameId,
                    guess: guessWord,
                    guessNumber: currentAttempt
                })
            });

            let data = {};
            try {
                data = await response.json();
            } catch (e) {
                // Not JSON
            }

            if (response.ok && data.success) {
                if (data.maxAttempts) {
                    maxAttempts = data.maxAttempts;
                    if (maxAttemptsCountText) {
                        maxAttemptsCountText.textContent = maxAttempts;
                    }
                }

                updateRow(currentAttempt, guessWord, data.result);
                updateKeyboard(guessWord, data.result);
                attemptCountText.textContent = currentAttempt;
                guessInput.value = "";

                if (data.status === "WON") {
                    setGameStatus("WON");
                    showSuccess("Congratulations! You guessed the secret word!");
                    guessForm.style.display = "none";
                    startSection.style.display = "flex";
                    startGameButton.textContent = "Play Again";
                    setTimeout(() => {
                        alert("Congratulations! You guessed the secret word!");
                    }, 100);
                } else if (data.status === "LOST") {
                    setGameStatus("LOST");
                    const target = data.targetWord ? ` The word was: ${data.targetWord}` : "";
                    showError(`Better luck next time!${target}`);
                    guessForm.style.display = "none";
                    startSection.style.display = "flex";
                    startGameButton.textContent = "Try Again";
                    setTimeout(() => {
                        alert(`Better luck next time!${target}`);
                    }, 100);
                } else {
                    guessInput.focus();
                }
            } else {
                currentAttempt--; // Revert attempt count if request failed
                showError(data.message || "Failed to submit guess.");
            }
        } catch (error) {
            currentAttempt--;
            showError("Something went wrong on the server while submitting your guess.");
        }
    }

    // User Logout
    async function handleLogout() {
        try {
            await fetch("/wordsprint/logout", {
                method: "POST"
            });
            window.location.href = "login.html";
        } catch (error) {
            window.location.href = "login.html";
        }
    }

    // Rules Dropdown Popover Handlers
    const rulesToggleBtn = document.getElementById("rules-toggle-btn");
    const rulesDropdown = document.getElementById("rules-dropdown");
    const closeRulesDropdownBtn = document.getElementById("close-rules-dropdown-btn");

    function toggleRulesDropdown(event) {
        if (event) event.stopPropagation();
        if (!rulesDropdown) return;
        const isOpen = rulesDropdown.style.display === "flex" || rulesDropdown.style.display === "block";
        if (isOpen) {
            closeRulesDropdown();
        } else {
            openRulesDropdown();
        }
    }

    function openRulesDropdown() {
        if (rulesDropdown) {
            rulesDropdown.style.display = "flex";
            if (rulesToggleBtn) {
                rulesToggleBtn.classList.add("active");
                rulesToggleBtn.setAttribute("aria-expanded", "true");
            }
        }
    }

    function closeRulesDropdown() {
        if (rulesDropdown) {
            rulesDropdown.style.display = "none";
            if (rulesToggleBtn) {
                rulesToggleBtn.classList.remove("active");
                rulesToggleBtn.setAttribute("aria-expanded", "false");
            }
        }
    }

    if (rulesToggleBtn) {
        rulesToggleBtn.addEventListener("click", toggleRulesDropdown);
    }

    if (closeRulesDropdownBtn) {
        closeRulesDropdownBtn.addEventListener("click", function (event) {
            event.stopPropagation();
            closeRulesDropdown();
        });
    }

    // Dismiss dropdown when clicking anywhere outside
    document.addEventListener("click", function (event) {
        if (!rulesDropdown || rulesDropdown.style.display === "none") return;
        if (!rulesDropdown.contains(event.target) && !rulesToggleBtn.contains(event.target)) {
            closeRulesDropdown();
        }
    });

    window.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && rulesDropdown && rulesDropdown.style.display !== "none") {
            closeRulesDropdown();
        }
    });

    // Attach Event Listeners
    if (startGameButton) {
        startGameButton.addEventListener("click", startNewGame);
    }

    if (guessForm) {
        guessForm.addEventListener("submit", handleGuessSubmit);
    }

    if (logoutButton) {
        logoutButton.addEventListener("click", handleLogout);
    }

    // Resume Game Handler
    async function resumeGame(gameId) {
        clearMessages();
        try {
            const response = await fetch(`/wordsprint/game?gameId=${gameId}`);
            if (response.status === 401) {
                window.location.href = "login.html";
                return;
            }

            const data = await response.json();
            if (response.ok && data.success) {
                currentGameId = data.gameId || data.game_id || gameId;
                currentAttempt = 0;
                resetKeyboardState();

                if (data.maxAttempts) {
                    maxAttempts = data.maxAttempts;
                }

                const totalGuesses = data.guesses ? data.guesses.length : 0;
                const boardRows = data.boardRows || Math.max(maxAttempts, totalGuesses);
                renderBoard(boardRows);

                if (data.guesses && data.guesses.length > 0) {
                    data.guesses.forEach(g => {
                        currentAttempt++;
                        const word = g.guessedWord || g.guess;
                        updateRow(currentAttempt, word, g.result);
                        updateKeyboard(word, g.result);
                    });
                }

                attemptCountText.textContent = currentAttempt;
                maxAttemptsCountText.textContent = maxAttempts;
                setGameStatus(data.status);

                if (data.status === "IN_PROGRESS") {
                    guessForm.style.display = "flex";
                    startSection.style.display = "none";
                    guessInput.value = "";
                    guessInput.focus();
                    const remaining = Math.max(0, maxAttempts - currentAttempt);
                    showSuccess(`Resumed Game #${currentGameId}. ${remaining} attempts remaining.`);
                } else {
                    guessForm.style.display = "none";
                    startSection.style.display = "flex";
                    if (data.status === "LOST" && currentAttempt >= maxAttempts) {
                        showError(`Game #${currentGameId} is LOST (maximum attempt limit of ${maxAttempts} reached).`);
                    } else {
                        showError(`Game #${currentGameId} is already ${data.status}.`);
                    }
                }
            } else {
                showError(data.message || "Failed to load game details.");
            }
        } catch (error) {
            showError("Unable to load game details.");
        }
    }

    // Auto-check for ?gameId=X in URL to resume game
    const urlParams = new URLSearchParams(window.location.search);
    const paramGameId = urlParams.get("gameId");
    if (paramGameId) {
        resumeGame(paramGameId);
    }
});
