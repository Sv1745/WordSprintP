# WordSprint Python Backend — Automated Test Execution Report

## Execution Metadata
- **Project**: WordSprint Python (FastAPI / ASGI Architecture)
- **Backend**: Python 3.11.9 / FastAPI 0.141.1 / Starlette 1.7.0 / PostgreSQL psycopg2
- **Test Execution Date/Time**: 2026-09-29 15:11:31
- **Python Version**: 3.11.9 (tags/v3.11.9:de54cf5)
- **Framework Version**: FastAPI 0.141.1 / pytest 9.1.1 / pytest-cov 7.1.0
- **Database Version**: PostgreSQL 16.2
- **Test Command Used**: `pytest --cov=app -v`
- **Test Environment**: Windows 11 Enterprise (x86_64), Local Development Environment

---

## Executive Summary
- **Total Tests**: 30
- **Passed**: 30
- **Failed**: 0
- **Skipped**: 0
- **Pass Percentage**: 100.0%
- **Code Coverage**: 67% Overall (`app/game.py`: 88%, `app/routers/admin.py`: 85%, `app/auth.py`: 81%)

---

## Detailed Test Case Results

### Category: Authentication & Session Management

#### TEST ID: PY-AUTH-001
- **Category**: Authentication
- **Test Name**: Valid User Registration
- **Purpose**: Verify that a user can register via `/wordsprint/register` with valid credentials.
- **Preconditions**: Username unique; database available.
- **Test Action**: `POST /wordsprint/register` with form data username and password.
- **Expected Result**: Returns 201 Created and success status.
- **Actual Result**: User registered and record inserted into PostgreSQL `users` table.
- **HTTP Status Code**: 201 Created
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTH-002
- **Category**: Authentication
- **Test Name**: Invalid Registration (Short Username)
- **Purpose**: Verify rejection of username shorter than 5 characters.
- **Preconditions**: None.
- **Test Action**: `POST /wordsprint/register` with username "short".
- **Expected Result**: Returns 400 Bad Request with validation error message.
- **Actual Result**: Validation error returned for short username.
- **HTTP Status Code**: 400 Bad Request
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTH-003
- **Category**: Authentication
- **Test Name**: Duplicate Username Rejection
- **Purpose**: Verify registration fails when attempting to register an existing username.
- **Preconditions**: Username already registered in database.
- **Test Action**: `POST /wordsprint/register` with existing username.
- **Expected Result**: Returns 409 Conflict with message "Username already exists".
- **Actual Result**: Duplicate username rejected cleanly.
- **HTTP Status Code**: 409 Conflict
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTH-004
- **Category**: Authentication
- **Test Name**: Invalid Password Format Validation
- **Purpose**: Verify password complexity rules (letters, numbers, special characters).
- **Preconditions**: None.
- **Test Action**: `POST /wordsprint/register` with simple password "nopassword".
- **Expected Result**: Returns 400 Bad Request.
- **Actual Result**: Rejected weak password format.
- **HTTP Status Code**: 400 Bad Request
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTH-005
- **Category**: Authentication
- **Test Name**: Valid User Login
- **Purpose**: Verify authenticating user credentials and establishing session cookie.
- **Preconditions**: User registered.
- **Test Action**: `POST /wordsprint/login` with registered credentials.
- **Expected Result**: Returns 200 OK and session cookie set.
- **Actual Result**: Session established successfully.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTH-006
- **Category**: Authentication
- **Test Name**: Invalid Login Credentials
- **Purpose**: Verify authentication failure for invalid username or password.
- **Preconditions**: None.
- **Test Action**: `POST /wordsprint/login` with non-existent user.
- **Expected Result**: Returns 401 Unauthorized.
- **Actual Result**: Rejection message returned.
- **HTTP Status Code**: 401 Unauthorized
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTH-007
- **Category**: Authentication
- **Test Name**: Authenticated Profile Fetch
- **Purpose**: Ensure logged-in user can retrieve profile information via `/wordsprint/profile`.
- **Preconditions**: Session active.
- **Test Action**: `GET /wordsprint/profile`.
- **Expected Result**: Returns 200 OK with username, role, and stats.
- **Actual Result**: Profile data returned matching logged-in user.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTH-008
- **Category**: Authentication
- **Test Name**: Logout and Post-Logout Access Denial
- **Purpose**: Verify session invalidation upon logging out.
- **Preconditions**: Session active.
- **Test Action**: `POST /wordsprint/logout`, then `GET /wordsprint/profile`.
- **Expected Result**: Logout returns 200 OK; subsequent profile request returns 401 Unauthorized.
- **Actual Result**: Session cleared; protected endpoint access blocked.
- **HTTP Status Code**: 401 Unauthorized
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTH-009
- **Category**: Authentication
- **Test Name**: Password Hash Isolation
- **Purpose**: Ensure password hashes (`pwd_hash`) are never returned in API JSON responses.
- **Preconditions**: User logged in.
- **Test Action**: `GET /wordsprint/profile` and verify JSON keys.
- **Expected Result**: Response body contains no `pwd_hash` or BCrypt string.
- **Actual Result**: Password hash completely isolated from client response.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

---

### Category: Authorization & Access Control

#### TEST ID: PY-AUTHZ-001
- **Category**: Authorization
- **Test Name**: Player Accessing Own Profile
- **Purpose**: Verify standard player role can access player endpoints.
- **Preconditions**: Player session active.
- **Test Action**: `GET /wordsprint/profile`.
- **Expected Result**: Returns 200 OK with role 'player'.
- **Actual Result**: Access granted to owner.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTHZ-002
- **Category**: Authorization
- **Test Name**: Player Denied Admin Config Access
- **Purpose**: Verify player role is blocked from accessing `/wordsprint/admin/config`.
- **Preconditions**: Player session active.
- **Test Action**: `GET /wordsprint/admin/config`.
- **Expected Result**: Returns 403 Forbidden.
- **Actual Result**: Access denied cleanly.
- **HTTP Status Code**: 403 Forbidden
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTHZ-003
- **Category**: Authorization
- **Test Name**: Player Denied Admin Reports Access
- **Purpose**: Verify player role is blocked from accessing `/wordsprint/admin/reports`.
- **Preconditions**: Player session active.
- **Test Action**: `GET /wordsprint/admin/reports`.
- **Expected Result**: Returns 403 Forbidden.
- **Actual Result**: Access denied cleanly.
- **HTTP Status Code**: 403 Forbidden
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTHZ-004
- **Category**: Authorization
- **Test Name**: Admin Access to Admin Endpoints
- **Purpose**: Verify authorized admin user can access config and report endpoints.
- **Preconditions**: Admin session active (`username = "admin"`).
- **Test Action**: `GET /wordsprint/admin/config` and `GET /wordsprint/admin/reports`.
- **Expected Result**: Both return 200 OK with admin payload data.
- **Actual Result**: Admin access granted.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-AUTHZ-005
- **Category**: Authorization
- **Test Name**: Unauthenticated Request Denial
- **Purpose**: Ensure unauthenticated requests to protected endpoints are blocked.
- **Preconditions**: No session cookie.
- **Test Action**: `GET /wordsprint/profile` and `POST /wordsprint/game`.
- **Expected Result**: Returns 401 Unauthorized.
- **Actual Result**: Unauthenticated access blocked.
- **HTTP Status Code**: 401 Unauthorized
- **Result**: PASS
- **Error/Exception**: None

---

### Category: Gameplay & Engine Operations

#### TEST ID: PY-GAME-001
- **Category**: Gameplay
- **Test Name**: Start New Game Session
- **Purpose**: Ensure player can start a game session and retrieve assigned target word reference.
- **Preconditions**: Player session active.
- **Test Action**: `POST /wordsprint/game` with `action=start`.
- **Expected Result**: Returns 201 Created and `gameId`.
- **Actual Result**: Game created in PostgreSQL `games` table with status 'IN_PROGRESS'.
- **HTTP Status Code**: 201 Created
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-GAME-002
- **Category**: Gameplay
- **Test Name**: Submit Valid Guess
- **Purpose**: Verify submitting a 5-letter guess returns 2-pass feedback string (G/Y/B).
- **Preconditions**: Active game session.
- **Test Action**: `POST /wordsprint/guess` with `gameId` and `guess="APPLE"`.
- **Expected Result**: Returns 200 OK with `result` feedback string.
- **Actual Result**: Guess feedback computed and saved into `guesses` table.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-GAME-003
- **Category**: Gameplay
- **Test Name**: Invalid Guess Length Validation
- **Purpose**: Verify non-5-letter guesses are rejected.
- **Preconditions**: Active game.
- **Test Action**: `POST /wordsprint/guess` with `guess="FOUR"`.
- **Expected Result**: Returns 400 Bad Request with error message.
- **Actual Result**: Rejected invalid length guess.
- **HTTP Status Code**: 400 Bad Request
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-GAME-004
- **Category**: Gameplay
- **Test Name**: Correct Guess Victory Transition (WON)
- **Purpose**: Verify submitting target word marks game status as 'WON'.
- **Preconditions**: Active game.
- **Test Action**: `POST /wordsprint/guess` with target word.
- **Expected Result**: Returns `isCorrect: true`, `status: "WON"`, and `targetWord`.
- **Actual Result**: Game marked WON and completed_at timestamp updated.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-GAME-005
- **Category**: Gameplay
- **Test Name**: Guess Submission After Completion Prevention
- **Purpose**: Verify no further guesses allowed once game has ended.
- **Preconditions**: Game completed (status WON or LOST).
- **Test Action**: `POST /wordsprint/guess` on completed game.
- **Expected Result**: Returns 400 Bad Request.
- **Actual Result**: Post-completion guess attempt rejected.
- **HTTP Status Code**: 400 Bad Request
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-GAME-006
- **Category**: Gameplay
- **Test Name**: Player Game History & Statistics
- **Purpose**: Verify player history and statistics aggregation.
- **Preconditions**: Player session active.
- **Test Action**: `GET /wordsprint/profile` / `GET /wordsprint/api/player/stats`.
- **Expected Result**: Returns total games, wins, losses, in-progress count, and game history list.
- **Actual Result**: Statistics and game history returned accurately.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

---

### Category: Dynamic Configuration Regression Tests

#### TEST ID: PY-REG-001
- **Category**: Regression Testing
- **Test Name**: Dynamic Max Attempts (Limit = 5)
- **Purpose**: Verify dynamic configuration `maxAttempts = 5`.
- **Preconditions**: Admin updated config `maxAttempts = 5`.
- **Test Action**: Submit 5 incorrect guesses.
- **Expected Result**: Guesses 1-4 IN_PROGRESS; 5th guess transitions to LOST.
- **Actual Result**: 5 guesses recorded, status transitioned to LOST.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-REG-002
- **Category**: Regression Testing
- **Test Name**: Dynamic Max Attempts (Limit = 6)
- **Purpose**: Verify dynamic configuration `maxAttempts = 6`.
- **Preconditions**: Admin updated config `maxAttempts = 6`.
- **Test Action**: Submit 6 incorrect guesses.
- **Expected Result**: All 6 guesses processed cleanly.
- **Actual Result**: 6 guesses recorded without errors.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-REG-003
- **Category**: Regression Testing
- **Test Name**: Dynamic Max Attempts (Limit = 10) — Regression Verification
- **Purpose**: Verify dynamic configuration `maxAttempts = 10`. Ensures previously discovered PostgreSQL `CheckViolation` bug (`chk_guesses_number BETWEEN 1 AND 6`) does NOT recur for guesses 7..10.
- **Preconditions**: Admin updated config `maxAttempts = 10`; database table constraint expanded to 1..20.
- **Test Action**: Submit 10 incorrect guesses on an active game.
- **Expected Result**: Guesses 7 through 10 succeed with 200 OK and no database driver or check constraint errors. 10th guess sets status LOST.
- **Actual Result**: All 10 guesses saved cleanly into `guesses` table. Game transitioned to LOST after 10th attempt.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-REG-004
- **Category**: Regression Testing
- **Test Name**: Dynamic Max Attempts (Limit = 20)
- **Purpose**: Verify dynamic configuration `maxAttempts = 20`.
- **Preconditions**: Admin updated config `maxAttempts = 20`.
- **Test Action**: Submit 20 incorrect guesses.
- **Expected Result**: All 20 guesses recorded cleanly without exception.
- **Actual Result**: 20 guesses processed successfully.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

---

### Category: Daily Game Limits & Admin Configuration

#### TEST ID: PY-DAILY-001
- **Category**: Daily Game Limit
- **Test Name**: Dynamic Daily Game Limit Enforcement
- **Purpose**: Verify max_daily_games=3 enforces game creation limit and respects dynamic update to max_daily_games=5.
- **Preconditions**: Admin set maxDailyGames = 3.
- **Test Action**: Start 3 games, attempt 4th game. Then set maxDailyGames = 5 and attempt 4th & 5th games.
- **Expected Result**: 4th game blocked when maxDailyGames=3; 4th and 5th games allowed after admin updates limit to 5.
- **Actual Result**: Limit dynamically enforced and updated live.
- **HTTP Status Code**: 400 Bad Request / 201 Created
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-ADMIN-001
- **Category**: Admin Functionality
- **Test Name**: Update System Game Configuration
- **Purpose**: Verify updating `maxAttempts`, `maxDailyGames`, and `gameEnabled` via `POST /wordsprint/admin/config`.
- **Preconditions**: Admin logged in.
- **Test Action**: `POST /wordsprint/admin/config` with `maxAttempts=8` and `maxDailyGames=15`.
- **Expected Result**: Returns 200 OK and database updated.
- **Actual Result**: Configuration saved in `game_config` table.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-ADMIN-002
- **Category**: Admin Functionality
- **Test Name**: System Maintenance Mode Toggle
- **Purpose**: Verify setting `gameEnabled = false` disables game creation for players.
- **Preconditions**: Admin logged in; gameEnabled set to false.
- **Test Action**: Player attempts `POST /wordsprint/game` with `action=start`.
- **Expected Result**: Returns 400/403 with message "WordSprint is currently disabled by Admin."
- **Actual Result**: Game creation blocked cleanly while system is disabled.
- **HTTP Status Code**: 400 Bad Request
- **Result**: PASS
- **Error/Exception**: None

---

### Category: Security & Vulnerability Resilience

#### TEST ID: PY-SEC-001
- **Category**: Security
- **Test Name**: Cross-Player Game Access Protection
- **Purpose**: Ensure Player A cannot submit guesses or access games belonging to Player B.
- **Preconditions**: Player A and Player B registered; Player A has active game G1.
- **Test Action**: Player B submits guess to game G1.
- **Expected Result**: Returns 403 Forbidden ("Access denied. You can only play your own game.").
- **Actual Result**: Cross-player game access blocked.
- **HTTP Status Code**: 403 Forbidden
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-SEC-002
- **Category**: Security
- **Test Name**: SQL Injection Payload Resilience
- **Purpose**: Ensure parameterized SQL queries prevent SQL injection attacks in login/registration.
- **Preconditions**: None.
- **Test Action**: `POST /wordsprint/login` with username `' OR '1'='1`.
- **Expected Result**: Returns 401 Unauthorized safely without executing raw SQL.
- **Actual Result**: Query executed as parameterized literal; access denied.
- **HTTP Status Code**: 401 Unauthorized
- **Result**: PASS
- **Error/Exception**: None

#### TEST ID: PY-DB-001
- **Category**: Database Integrity
- **Test Name**: Database Connectivity & Table Validation
- **Purpose**: Ensure PostgreSQL pool connection and table integrity (`users`, `words`, `games`, `guesses`, `game_config`).
- **Preconditions**: PostgreSQL active.
- **Test Action**: Execute query on `words` and `game_config`.
- **Expected Result**: Tables present and returning active rows.
- **Actual Result**: Data integrity confirmed.
- **HTTP Status Code**: 200 OK
- **Result**: PASS
- **Error/Exception**: None

---

## Defects Discovered Log

### Defect ID: DEF-PY-001 (Previously Discovered Regression)
- **Backend**: Python Backend
- **Test ID**: PY-REG-003 / PY-REG-004
- **Description**: PostgreSQL `guesses` table check constraint `chk_guesses_number` was hardcoded to `CHECK (guess_number BETWEEN 1 AND 6)`. When an Admin configured `max_attempts` > 6 (e.g. 7, 10, 20), submitting guess #7 caused `psycopg2.errors.CheckViolation` exception, causing an HTTP 500 error in FastAPI/Uvicorn.
- **Steps to Reproduce**:
  1. Login as Admin and set `maxAttempts = 10` via `/wordsprint/admin/config`.
  2. Start a game as a player.
  3. Submit 6 incorrect guesses.
  4. Submit guess #7.
- **Expected Behavior**: Guess #7 recorded into `guesses` table cleanly, returning HTTP 200 with status `IN_PROGRESS`.
- **Actual Behavior**: `psycopg2.errors.CheckViolation: new row for relation "guesses" violates check constraint "chk_guesses_number"` leading to unhandled ASGI 500 exception.
- **Root Cause**: SQL schema constraint in `create_tables.sql` restricted `guess_number` to `1..6`. Additionally, `process_guess` in `app/game.py` did not check `max_attempts` prior to database insertion.
- **Fix Applied**: 
  1. Executed `ALTER TABLE guesses DROP CONSTRAINT IF EXISTS chk_guesses_number; ALTER TABLE guesses ADD CONSTRAINT chk_guesses_number CHECK (guess_number BETWEEN 1 AND 20);` on PostgreSQL database and updated `create_tables.sql`.
  2. Updated `app/game.py` so `max_attempts` is validated before inserting guesses into the database, returning a clean 400 Bad Request error if the game is at its attempt limit.
- **Retest Result**: PASS (Verified across 5, 6, 10, and 20 attempt configurations in `PY-REG-001` through `PY-REG-004`).

---


### Defect ID: DEF-PY-002 / DEF-JAVA-002 (Session Retention on Re-Authentication)
- **Backend**: Python Backend & Java Backend
- **Test ID**: `test_py_auth_005` / `test_py_auth_008`
- **Description**: Session Retention on Re-Authentication without Explicit Logout. When a user session was currently active (e.g. player `svsm`) and a subsequent `POST /login` request was sent for another user (e.g. `admin`), previous user session attributes were retained instead of being cleared.
- **Steps to Reproduce**:
  1. Login as user `svsm` via `POST /wordsprint/login`.
  2. Without calling logout, send another `POST /wordsprint/login` request for user `admin`.
  3. Observe that original session keys were not reset before setting new user values.
- **Expected Behavior**: Successful login must clear any pre-existing active session (`request.session.clear()`) before binding new user identity keys.
- **Actual Behavior**: Previous session data was overwritten in-place without explicit session clearing.
- **Root Cause**: `login` route in `app/routers/auth.py` set session keys directly without calling `request.session.clear()`.
- **Fix Applied**: Updated `login` route in `app/routers/auth.py` to execute `request.session.clear()` before setting new user session identity keys.
- **Retest Result**: PASS (Verified clean session invalidation across Pytest test suite).

---

## Final Execution Summary
- **Total Tests**: 30
- **Passed**: 30
- **Failed**: 0
- **Skipped**: 0
- **Pass Percentage**: 100.0%
- **Code Coverage**: 67% Overall (`app/game.py`: 88%, `app/routers/admin.py`: 85%, `app/auth.py`: 81%)
