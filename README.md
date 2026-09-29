# WordSprint — Python FastAPI Backend

WordSprint is a web-based word guessing application built with **Python 3.11**, **FastAPI**, **Uvicorn**, and a **PostgreSQL** relational database. Players guess a secret 5-letter word within a configurable number of attempts (default: 5) and receive letter-by-letter visual feedback (Green = Correct position, Yellow = Present in word, Gray = Absent).

---

## 📋 Features

### Player Features
- **User Authentication**: Secure registration and login with salted BCrypt password hashing (`$2b$12$`) and session cookie management.
- **Word Evaluation Engine**: Real-time 2-pass feedback evaluation (Green / Yellow / Gray) for 5-letter uppercase guesses.
- **Session Resumption**: Automatic recovery of active in-progress games (`/wordsprint/game/current`).
- **Player Profile & History**: Summary statistics, win rates, current/max streaks, and chronological game history logs (`/wordsprint/game/history`).
- **Daily Game Limits**: Enforced daily game allowance (default: 3 games per day).

### Admin Features
- **Control Panel**: Administrative dashboard restricted to users with the `admin` role.
- **Dynamic Configuration Tuning**: Real-time adjustment of `max_attempts` (5–20), `max_daily_games` (default: 3), and global `game_enabled` toggle without restarting the server.
- **System Reports**: Platform-wide player metrics, total game counts, overall win percentages, player directory, and daily activity logs.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.11, FastAPI 0.115+, Uvicorn (ASGI Application Server)
- **Database**: PostgreSQL 16 (Connection Pool & Parameterized Queries)
- **Frontend**: Single-Page Application (HTML5, Vanilla CSS3, JavaScript ES6+)
- **Security**: Passlib (`$2b$12$` BCrypt), Session Cookie Middleware, IDOR Protection, SQL Injection Defense
- **Testing**: Pytest 9, FastAPI `TestClient`, `pytest-cov` (35 Test Scenarios, 100% Pass Rate, 78% Statement Coverage)

---

## 📂 Project Structure

```text
WordSprint_Python/
├── README.md                   # Primary Python project documentation
├── TEST_REPORT.md              # Automated test execution report (35 tests, 100% pass)
├── requirements.txt            # Python package dependencies
├── .env                        # Database & environment configuration
├── database/
│   └── create_tables.sql       # PostgreSQL DDL schema definition
├── app/
│   ├── main.py                 # FastAPI application initialization & routes
│   ├── auth.py                 # Password hashing & session security core
│   ├── game.py                 # Core game engine logic & feedback calculator
│   ├── database.py             # PostgreSQL connection pool manager
│   ├── config.py               # Environment configuration settings
│   └── routers/
│       ├── auth.py             # Authentication endpoints (/register, /login, /logout)
│       ├── game.py             # Game management endpoints (/start, /current, /guess, /history)
│       └── admin.py            # Administration endpoints (/config, /reports)
├── static/                     # Web client frontend static assets (HTML/CSS/JS)
└── tests/
    └── test_main.py            # Pytest test suite (35 Test Scenarios)
```

---

## 🔌 API Endpoint Specifications (Base URL: `http://localhost:8000/wordsprint`)

| Endpoint Path | HTTP Method | Auth Level | Purpose / Description |
| :--- | :---: | :---: | :--- |
| `/wordsprint/register` | `POST` | Public | Register new player account (`role = 'player'`). |
| `/wordsprint/login` | `POST` | Public | Authenticate credentials against BCrypt hash & set session cookie. |
| `/wordsprint/logout` | `POST` / `GET` | Authenticated | Destroy active HTTP session. |
| `/wordsprint/profile` | `GET` | Authenticated | Retrieve user stats, win rates, and streak metrics. |
| `/wordsprint/profile/update` | `POST` | Authenticated | Update user username or password. |
| `/wordsprint/game/start` | `POST` | Authenticated | Create a new game session (assigns secret word). |
| `/wordsprint/game/current` | `GET` | Authenticated | Retrieve active in-progress game and previous guesses. |
| `/wordsprint/guess` | `POST` | Authenticated | Submit 5-letter guess (`{"game_id": 102, "guess": "APPLE"}`). |
| `/wordsprint/game/history` | `GET` | Authenticated | Retrieve chronological history array of completed games. |
| `/wordsprint/admin/config` | `GET` / `POST` | Admin Only | Get or update dynamic settings (`max_attempts` 5–20, `max_daily_games` 3, `game_enabled`). |
| `/wordsprint/admin/reports` | `GET` | Admin Only | Generate system analytics & player directory reports. |

---

## 💾 Database Schema Overview

Operates against the shared PostgreSQL 16 database:
- **`users`**: User credentials, BCrypt hashes, and security roles (`player`, `admin`).
- **`words`**: 5-letter secret target word bank.
- **`games`**: Game sessions tracking player, target word, timestamps, and status (`IN_PROGRESS`, `WON`, `LOST`).
- **`guesses`**: Recorded guesses per game with feedback strings (`GGYBB`) and sequence numbers.
- **`game_config`**: Dynamic system configuration singleton (`max_attempts` default: 5, `max_daily_games` default: 3, `game_enabled`).

---

## 🧪 Testing & Code Coverage Summary

Automated testing was executed via `pytest` with `pytest-cov`:
- **Total Tests**: **35**
- **Passed**: **35 (100.0% Pass Rate)**
- **Failed / Skipped**: **0 / 0**
- **Overall Codebase Coverage**: **78%**

### Statement Coverage Breakdown
- **Core Game Engine (`app/game.py`)**: **88% Coverage**
- **Auth & Security Core (`app/auth.py`)**: **85% Coverage**
- **Admin Router (`app/routers/admin.py`)**: **85% Coverage**
- **Auth Router (`app/routers/auth.py`)**: **80% Coverage**
- **Database Layer (`app/database.py`)**: **74% Coverage**
- **HTTP Game Router (`app/routers/game.py`)**: **62% Coverage**

Complete execution log is available in [`TEST_REPORT.md`](TEST_REPORT.md).

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Set environment variables or edit `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wordsprint
DB_USER=postgres
DB_PASSWORD=postgres
```

### 3. Run FastAPI Application
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Execute Automated Test Suite
```bash
pytest --cov=app -v
```
