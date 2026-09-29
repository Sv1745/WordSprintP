// auth.js - Handles User Registration and Login Forms

document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("register-form");
    const loginForm = document.getElementById("login-form");
    const errorMessage = document.getElementById("error-message");
    const successMessage = document.getElementById("success-message");

    // Utility function to hide alert messages
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

    // Utility function to display error alerts
    function showError(message) {
        clearMessages();
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = "block";
        }
    }

    // Utility function to display success alerts
    function showSuccess(message) {
        clearMessages();
        if (successMessage) {
            successMessage.textContent = message;
            successMessage.style.display = "block";
        }
    }

    // Handle User Registration
    if (registerForm) {
        registerForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            clearMessages();

            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value;
            const role = document.getElementById("role").value;

            // Validate Username (at least 5 letters, both uppercase and lowercase)
            if (username.length < 5 || !/[A-Z]/.test(username) || !/[a-z]/.test(username)) {
                showError("Username must be at least 5 characters long and contain both uppercase and lowercase letters (e.g. TestUser).");
                return;
            }

            // Validate Password (at least 5 characters, alpha, numeric, and special char $, %, *, @, #, !, &)
            const hasAlpha = /[A-Za-z]/.test(password);
            const hasNumeric = /\d/.test(password);
            const hasSpecial = /[$%*@#&!]/.test(password);
            if (password.length < 5 || !hasAlpha || !hasNumeric || !hasSpecial) {
                showError("Password must be at least 5 characters long and include letters, numbers, and a special character ($, %, *, @, #, !, &).");
                return;
            }

            try {
                const response = await fetch("/wordsprint/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams({
                        username: username,
                        password: password,
                        role: role
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showSuccess(data.message || "Registration successful! Redirecting to login...");
                    setTimeout(function () {
                        window.location.href = "login.html";
                    }, 1500);
                } else {
                    showError(data.message || "Registration failed. Please try again.");
                }
            } catch (error) {
                showError("Something went wrong on the server. Please try again later.");
            }
        });
    }

    // Handle User Login
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            clearMessages();

            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value;

            try {
                const response = await fetch("/wordsprint/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams({
                        username: username,
                        password: password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showSuccess("Login successful! Redirecting to dashboard...");
                    setTimeout(function () {
                        window.location.href = "dashboard.html";
                    }, 1000);
                } else {
                    showError(data.message || "Invalid username or password.");
                }
            } catch (error) {
                showError("Something went wrong on the server. Please try again later.");
            }
        });
    }
});
