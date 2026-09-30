from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from app.database import fetch_one, fetch_all, execute_query

router = APIRouter(tags=["Admin Operations"])

def check_admin_auth(request: Request):
    user_id = request.session.get("user_id")
    role = request.session.get("role")
    if not user_id or role != "admin":
        return False
    return True

@router.get("/admin/config")
@router.get("/wordsprint/admin/config")
async def get_admin_config(request: Request):
    if not check_admin_auth(request):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": "Admin access required"}
        )
    config = fetch_one("SELECT max_attempts, max_daily_games, game_enabled FROM game_config WHERE config_id = 1")
    if not config:
        config = {"max_attempts": 5, "max_daily_games": 3, "game_enabled": True}

    return {
        "success": True,
        "maxAttempts": config["max_attempts"],
        "maxDailyGames": config["max_daily_games"],
        "gameEnabled": bool(config["game_enabled"])
    }

@router.post("/admin/config")
@router.post("/wordsprint/admin/config")
async def update_admin_config(request: Request):
    if not check_admin_auth(request):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": "Admin access required"}
        )

    content_type = request.headers.get("content-type", "")
    max_attempts = None
    max_daily = None
    game_enabled = None

    if "application/json" in content_type:
        try:
            data = await request.json()
            max_attempts = data.get("maxAttempts")
            max_daily = data.get("maxDailyGames")
            game_enabled = data.get("gameEnabled")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            max_attempts = form.get("maxAttempts")
            max_daily = form.get("maxDailyGames")
            game_enabled = form.get("gameEnabled")
        except Exception:
            pass

    if max_attempts is None or max_daily is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "Missing maxAttempts or maxDailyGames"}
        )

    try:
        attempts_val = int(max_attempts)
        daily_val = int(max_daily)
        enabled_val = True if str(game_enabled).lower() in ("true", "1", "on", "yes") else False
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "Invalid numeric values"}
        )

    execute_query("""
        INSERT INTO game_config (config_id, max_attempts, max_daily_games, game_enabled)
        VALUES (1, %s, %s, %s)
        ON CONFLICT (config_id) DO UPDATE
        SET max_attempts = EXCLUDED.max_attempts,
            max_daily_games = EXCLUDED.max_daily_games,
            game_enabled = EXCLUDED.game_enabled
    """, (attempts_val, daily_val, enabled_val))

    return {
        "success": True,
        "message": "Configuration updated successfully!"
    }

@router.get("/admin/report")
@router.get("/admin/reports")
@router.get("/wordsprint/admin/report")
@router.get("/wordsprint/admin/reports")
async def get_admin_reports(request: Request):
    if not check_admin_auth(request):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": "Admin access required"}
        )

    # 1. System Stats
    users_raw = fetch_all("SELECT role, COUNT(*) as cnt FROM users GROUP BY role")
    games_raw = fetch_all("SELECT status, COUNT(*) as cnt FROM games GROUP BY status")

    total_players = 0
    total_admins = 0
    for r in users_raw:
        if r["role"] == "player":
            total_players = r["cnt"]
        elif r["role"] == "admin":
            total_admins = r["cnt"]

    total_games = 0
    won_games = 0
    lost_games = 0
    in_progress_games = 0

    for g in games_raw:
        cnt = g["cnt"]
        total_games += cnt
        st = g["status"]
        if st == "WON":
            won_games = cnt
        elif st == "LOST":
            lost_games = cnt
        elif st == "IN_PROGRESS":
            in_progress_games = cnt

    stats = {
        "totalPlayers": total_players,
        "totalAdmins": total_admins,
        "totalGames": total_games,
        "wonGames": won_games,
        "lostGames": lost_games,
        "inProgressGames": in_progress_games
    }

    # 2. Daily Activity Reports
    daily_raw = fetch_all("""
        SELECT DATE(started_at) AS game_date,
               COUNT(DISTINCT user_id) AS active_users,
               COUNT(CASE WHEN status = 'WON' THEN 1 END) AS correct_guesses
        FROM games
        GROUP BY DATE(started_at)
        ORDER BY game_date DESC
    """)
    daily_reports = [
        {
            "date": str(r["game_date"]) if r["game_date"] else "",
            "activeUsers": r["active_users"],
            "correctGuesses": r["correct_guesses"]
        }
        for r in daily_raw
    ]

    # 3. User Daily Reports
    user_daily_raw = fetch_all("""
        SELECT u.uname,
               DATE(g.started_at) AS game_date,
               COUNT(DISTINCT g.game_id) AS words_tried,
               COUNT(CASE WHEN g.status = 'WON' THEN 1 END) AS correct_guesses
        FROM games g
        JOIN users u ON g.user_id = u.user_id
        GROUP BY u.uname, DATE(g.started_at)
        ORDER BY game_date DESC, u.uname ASC
    """)
    user_daily_reports = [
        {
            "username": r["uname"],
            "date": str(r["game_date"]) if r["game_date"] else "",
            "wordsTried": r["words_tried"],
            "correctGuesses": r["correct_guesses"]
        }
        for r in user_daily_raw
    ]

    # 4. Player Directory & Reports
    players_raw = fetch_all("""
        SELECT u.user_id, u.uname, u.role, u.created_at,
               COUNT(g.game_id) AS total_games,
               COUNT(CASE WHEN g.status = 'WON' THEN 1 END) AS wins,
               COUNT(CASE WHEN g.status = 'LOST' THEN 1 END) AS losses,
               COUNT(CASE WHEN g.status = 'IN_PROGRESS' THEN 1 END) AS in_progress
        FROM users u
        LEFT JOIN games g ON u.user_id = g.user_id
        GROUP BY u.user_id, u.uname, u.role, u.created_at
        ORDER BY u.created_at DESC
    """)
    reports = [
        {
            "userId": r["user_id"],
            "username": r["uname"],
            "role": r["role"],
            "createdAt": str(r["created_at"]) if r["created_at"] else "",
            "totalGames": r["total_games"],
            "wins": r["wins"],
            "losses": r["losses"],
            "inProgress": r["in_progress"]
        }
        for r in players_raw
    ]

    # 5. Match Activity & Game Logs
    match_raw = fetch_all("""
        SELECT g.game_id, u.uname, w.word, g.started_at, g.completed_at, g.status,
               COUNT(gu.guess_id) AS attempts_made
        FROM games g
        JOIN users u ON g.user_id = u.user_id
        LEFT JOIN words w ON g.word_id = w.word_id
        LEFT JOIN guesses gu ON g.game_id = gu.game_id
        GROUP BY g.game_id, u.uname, w.word, g.started_at, g.completed_at, g.status
        ORDER BY g.started_at DESC
        LIMIT 500
    """)
    match_reports = [
        {
            "gameId": r["game_id"],
            "username": r["uname"],
            "word": r["word"] or "-",
            "startedAt": str(r["started_at"]) if r["started_at"] else "",
            "completedAt": str(r["completed_at"]) if r["completed_at"] else "-",
            "status": r["status"],
            "attempts": r["attempts_made"]
        }
        for r in match_raw
    ]

    return {
        "success": True,
        "stats": stats,
        "dailyReports": daily_reports,
        "userDailyReports": user_daily_reports,
        "reports": reports,
        "matchReports": match_reports
    }
