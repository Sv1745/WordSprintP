import pytest
from fastapi.testclient import TestClient
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import fetch_one, fetch_all, execute_query
from app.game import get_game_config

client = TestClient(app)

def unique_username(prefix="TestUser"):
    return f"{prefix}{uuid.uuid4().hex[:6]}"

@pytest.fixture(autouse=True)
def reset_default_config():
    """Ensure config is reset to standard defaults after tests if modified."""
    yield
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname="wordsprint",
            user="postgres",
            password=os.environ.get("DB_PASSWORD", "postgres"),
            host="localhost",
            port=5432
        )
        cur = conn.cursor()
        cur.execute("UPDATE game_config SET max_attempts = 5, max_daily_games = 3, game_enabled = TRUE WHERE config_id = 1")
        conn.commit()
        conn.close()
    except Exception:
        pass

# ==========================================
# 1. PYTHON AUTHENTICATION TESTS
# ==========================================

def test_py_auth_001_valid_registration():
    uname = unique_username("RegValid")
    res = client.post("/wordsprint/register", data={"username": uname, "password": "Pass123!$%*@#&"})
    assert res.status_code == 201
    assert res.json()["success"] is True

def test_py_auth_002_invalid_registration_username():
    res = client.post("/wordsprint/register", data={"username": "short", "password": "Pass123!$%*@#&"})
    assert res.status_code == 400
    assert res.json()["success"] is False

def test_py_auth_003_duplicate_username():
    uname = unique_username("DupUser")
    client.post("/wordsprint/register", data={"username": uname, "password": "Pass123!$%*@#&"})
    res = client.post("/wordsprint/register", data={"username": uname, "password": "Pass123!$%*@#&"})
    assert res.status_code == 409
    assert "already exists" in res.json()["message"]

def test_py_auth_004_invalid_password_format():
    res = client.post("/wordsprint/register", data={"username": unique_username("BadPass"), "password": "nopassword"})
    assert res.status_code == 400
    assert res.json()["success"] is False

def test_py_auth_005_valid_login():
    uname = unique_username("LogValid")
    pwd = "Pass123!$%*@#&"
    client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    
    login_res = client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    assert login_res.status_code == 200
    assert login_res.json()["success"] is True

def test_py_auth_006_invalid_login():
    res = client.post("/wordsprint/login", data={"username": "NonExistentUser123", "password": "WrongPassword!1"})
    assert res.status_code == 401
    assert res.json()["success"] is False

def test_py_auth_007_auth_check_profile():
    test_client = TestClient(app)
    uname = unique_username("ProfileAuth")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    profile_res = test_client.get("/wordsprint/profile")
    assert profile_res.status_code == 200
    assert profile_res.json()["username"] == uname

def test_py_auth_008_logout_and_access_after_logout():
    test_client = TestClient(app)
    uname = unique_username("LogoutUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    logout_res = test_client.post("/wordsprint/logout")
    assert logout_res.status_code == 200
    
    after_logout = test_client.get("/wordsprint/profile")
    assert after_logout.status_code == 401

def test_py_auth_009_password_hash_never_exposed():
    test_client = TestClient(app)
    uname = unique_username("NoHash")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    res = test_client.get("/wordsprint/profile")
    body_str = str(res.json())
    assert "pwd_hash" not in body_str
    assert "passwordHash" not in body_str
    assert "$2b$" not in body_str

# ==========================================
# 2. PYTHON AUTHORIZATION TESTS
# ==========================================

def test_py_authz_001_player_accesses_own_profile():
    test_client = TestClient(app)
    uname = unique_username("AuthzPlayer")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    res = test_client.get("/wordsprint/profile")
    assert res.status_code == 200
    assert res.json()["role"] == "player"

def test_py_authz_002_player_denied_admin_config():
    test_client = TestClient(app)
    uname = unique_username("NormalPlayer")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    res = test_client.get("/wordsprint/admin/config")
    assert res.status_code in (401, 403)

def test_py_authz_003_player_denied_admin_reports():
    test_client = TestClient(app)
    uname = unique_username("NormalPlayer2")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    res = test_client.get("/wordsprint/admin/reports")
    assert res.status_code in (401, 403)

def test_py_authz_004_admin_accesses_admin_endpoints():
    test_client = TestClient(app)
    test_client.post("/wordsprint/login", data={"username": "admin", "password": "admin123"})
    
    res_cfg = test_client.get("/wordsprint/admin/config")
    assert res_cfg.status_code == 200
    
    res_rep = test_client.get("/wordsprint/admin/reports")
    assert res_rep.status_code == 200

def test_py_authz_005_unauthenticated_denied_protected_endpoints():
    test_client = TestClient(app)
    res_prof = test_client.get("/wordsprint/profile")
    assert res_prof.status_code == 401
    
    res_game = test_client.post("/wordsprint/game", data={"action": "start"})
    assert res_game.status_code == 401

# ==========================================
# 3. PYTHON GAME TESTS
# ==========================================

def test_py_game_001_start_game():
    test_client = TestClient(app)
    uname = unique_username("GamePlayer")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    res = test_client.post("/wordsprint/game", data={"action": "start"})
    assert res.status_code in (200, 201)
    assert "gameId" in res.json() or "game_id" in res.json()

def test_py_game_002_submit_guess():
    test_client = TestClient(app)
    uname = unique_username("GuessUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    start_res = test_client.post("/wordsprint/game", data={"action": "start"})
    g_id = start_res.json().get("gameId") or start_res.json().get("game_id")
    
    guess_res = test_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": "APPLE"})
    assert guess_res.status_code == 200
    assert guess_res.json()["success"] is True
    assert "result" in guess_res.json()

def test_py_game_003_invalid_guess_length():
    test_client = TestClient(app)
    uname = unique_username("BadLenUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    start_res = test_client.post("/wordsprint/game", data={"action": "start"})
    g_id = start_res.json().get("gameId") or start_res.json().get("game_id")
    
    guess_res = test_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": "FOUR"})
    assert guess_res.status_code == 400
    assert guess_res.json()["success"] is False

def test_py_game_004_game_won():
    test_client = TestClient(app)
    uname = unique_username("WinUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    start_res = test_client.post("/wordsprint/game", data={"action": "start"})
    g_id = start_res.json().get("gameId") or start_res.json().get("game_id")
    
    target_row = fetch_one(
        "SELECT w.word FROM words w JOIN games g ON w.word_id = g.word_id WHERE g.game_id = %s",
        (g_id,)
    )
    correct_word = target_row["word"]
    
    guess_res = test_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": correct_word})
    assert guess_res.status_code == 200
    assert guess_res.json()["isCorrect"] is True
    assert guess_res.json()["status"] == "WON"

def test_py_game_005_guess_after_game_completion():
    test_client = TestClient(app)
    uname = unique_username("CompletedUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    start_res = test_client.post("/wordsprint/game", data={"action": "start"})
    g_id = start_res.json().get("gameId") or start_res.json().get("game_id")
    
    target_row = fetch_one(
        "SELECT w.word FROM words w JOIN games g ON w.word_id = g.word_id WHERE g.game_id = %s",
        (g_id,)
    )
    correct_word = target_row["word"]
    
    test_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": correct_word})
    
    extra_guess = test_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": "APPLE"})
    assert extra_guess.status_code == 400
    assert extra_guess.json()["success"] is False

def test_py_game_006_game_history_and_stats():
    test_client = TestClient(app)
    uname = unique_username("StatsUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    test_client.post("/wordsprint/game", data={"action": "start"})
    
    stats_res = test_client.get("/wordsprint/profile")
    assert stats_res.status_code == 200
    assert "stats" in stats_res.json()
    assert "games" in stats_res.json()

# ==========================================
# 4. PYTHON DYNAMIC MAX_ATTEMPTS REGRESSION TESTS
# ==========================================

@pytest.mark.parametrize("configured_max", [5, 6, 10, 20])
def test_py_reg_max_attempts_dynamic(configured_max):
    """
    REGRESSION TEST: Verify max_attempts dynamic configuration (5, 6, 10, 20).
    Ensures guess_number between 1 and configured_max executes cleanly without HTTP 500 or DB constraint violations.
    """
    admin_client = TestClient(app)
    admin_client.post("/wordsprint/login", data={"username": "admin", "password": "admin123"})
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": str(configured_max), "maxDailyGames": "20", "gameEnabled": "true"})
    
    player_client = TestClient(app)
    uname = unique_username(f"RegMax{configured_max}")
    pwd = "Pass123!$%*@#&"
    player_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    player_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    start_res = player_client.post("/wordsprint/game", data={"action": "start"})
    g_id = start_res.json().get("gameId") or start_res.json().get("game_id")
    
    target_row = fetch_one(
        "SELECT w.word FROM words w JOIN games g ON w.word_id = g.word_id WHERE g.game_id = %s",
        (g_id,)
    )
    target_word = target_row["word"]
    wrong_word = "ZZZZZ" if target_word != "ZZZZZ" else "YYYYY"
    
    for attempt in range(1, configured_max):
        guess_res = player_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": wrong_word})
        assert guess_res.status_code == 200, f"Failed at attempt {attempt} for max {configured_max}: {guess_res.text}"
        assert guess_res.json()["status"] == "IN_PROGRESS"
    
    last_guess = player_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": wrong_word})
    assert last_guess.status_code == 200
    assert last_guess.json()["status"] == "LOST"
    
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "3", "gameEnabled": "true"})
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "3", "gameEnabled": "true"})
    
    over_limit = player_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": wrong_word})
    assert over_limit.status_code == 400

# ==========================================
# 5. PYTHON DAILY GAME LIMIT TESTS
# ==========================================

def test_py_daily_001_daily_game_limit():
    admin_client = TestClient(app)
    admin_client.post("/wordsprint/login", data={"username": "admin", "password": "admin123"})
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "3", "gameEnabled": "true"})
    
    player_client = TestClient(app)
    uname = unique_username("DailyLimitUser")
    pwd = "Pass123!$%*@#&"
    player_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    player_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    for i in range(3):
        g_res = player_client.post("/wordsprint/game", data={"action": "start"})
        assert g_res.status_code in (200, 201)
        g_id = g_res.json().get("gameId") or g_res.json().get("game_id")
        player_client.post("/wordsprint/game", data={"action": "end", "gameId": str(g_id), "status": "LOST"})
    
    fourth_res = player_client.post("/wordsprint/game", data={"action": "start"})
    assert fourth_res.status_code in (400, 403)
    assert "Daily limit reached" in fourth_res.json()["message"]
    
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "5", "gameEnabled": "true"})
    
    fifth_res = player_client.post("/wordsprint/game", data={"action": "start"})
    assert fifth_res.status_code in (200, 201)
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "3", "gameEnabled": "true"})

# ==========================================
# 6. PYTHON ADMIN TESTS
# ==========================================

def test_py_admin_001_update_configuration():
    admin_client = TestClient(app)
    admin_client.post("/wordsprint/login", data={"username": "admin", "password": "admin123"})
    
    update_res = admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "8", "maxDailyGames": "15", "gameEnabled": "true"})
    assert update_res.status_code == 200
    
    cfg = get_game_config()
    assert cfg["max_attempts"] == 8
    assert cfg["max_daily_games"] == 15
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "3", "gameEnabled": "true"})

def test_py_admin_002_disable_game():
    admin_client = TestClient(app)
    admin_client.post("/wordsprint/login", data={"username": "admin", "password": "admin123"})
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "3", "gameEnabled": "false"})
    
    player_client = TestClient(app)
    uname = unique_username("DisabledGameUser")
    pwd = "Pass123!$%*@#&"
    player_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    player_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    start_res = player_client.post("/wordsprint/game", data={"action": "start"})
    assert start_res.status_code in (400, 403)
    assert "disabled" in start_res.json()["message"].lower()
    
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "3", "gameEnabled": "true"})

# ==========================================
# 7. PYTHON SECURITY TESTS
# ==========================================

def test_py_sec_001_cross_user_game_access():
    client1 = TestClient(app)
    u1 = unique_username("UserOne")
    p1 = "Pass123!$%*@#&"
    client1.post("/wordsprint/register", data={"username": u1, "password": p1})
    client1.post("/wordsprint/login", data={"username": u1, "password": p1})
    g1_res = client1.post("/wordsprint/game", data={"action": "start"})
    g1_id = g1_res.json().get("gameId") or g1_res.json().get("game_id")
    
    client2 = TestClient(app)
    u2 = unique_username("UserTwo")
    p2 = "Pass123!$%*@#&"
    client2.post("/wordsprint/register", data={"username": u2, "password": p2})
    client2.post("/wordsprint/login", data={"username": u2, "password": p2})
    
    guess_res = client2.post("/wordsprint/guess", data={"gameId": str(g1_id), "guess": "APPLE"})
    assert guess_res.status_code in (403, 400)

def test_py_sec_002_sql_injection_resilience():
    client1 = TestClient(app)
    sql_payload = "' OR '1'='1"
    login_res = client1.post("/wordsprint/login", data={"username": sql_payload, "password": sql_payload})
    assert login_res.status_code in (400, 401)
    
    reg_res = client1.post("/wordsprint/register", data={"username": "InjectedUser", "password": "InvalidPasswordFormat"})
    assert reg_res.status_code == 400

# ==========================================
# 8. PYTHON DATABASE INTEGRITY TESTS
# ==========================================

def test_py_db_001_database_connectivity_and_schema():
    words = fetch_all("SELECT word_id, word FROM words LIMIT 5")
    assert len(words) > 0
    
    cfg = fetch_one("SELECT config_id, max_attempts, max_daily_games, game_enabled FROM game_config WHERE config_id = 1")
    assert cfg is not None
    assert cfg["max_attempts"] > 0


# ==========================================
# 9. ADDITIONAL COMPREHENSIVE COVERAGE TESTS
# ==========================================

def test_py_auth_010_validation_edge_cases():
    # Short username
    res1 = client.post("/wordsprint/register", data={"username": "abc", "password": "Pass123!$%*@#&"})
    assert res1.status_code == 400
    
    # Username without uppercase
    res2 = client.post("/wordsprint/register", data={"username": "lowercase", "password": "Pass123!$%*@#&"})
    assert res2.status_code == 400
    
    # Password without number
    res3 = client.post("/wordsprint/register", data={"username": "ValidUser", "password": "Password!@#$%"})
    assert res3.status_code == 400
    
    # Password without special char
    res4 = client.post("/wordsprint/register", data={"username": "ValidUser", "password": "Password12345"})
    assert res4.status_code == 400

def test_py_auth_011_update_profile_username_and_password():
    test_client = TestClient(app)
    uname = unique_username("UpdateUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    new_uname = unique_username("NewUname")
    new_pwd = "NewPass123!$%*@#&"
    
    # Missing old password when changing password
    res_err1 = test_client.post("/wordsprint/profile", json={"newPassword": new_pwd, "confirmPassword": new_pwd})
    assert res_err1.status_code == 400
    
    # Mismatched confirm password
    res_err2 = test_client.post("/wordsprint/profile", json={"oldPassword": pwd, "newPassword": new_pwd, "confirmPassword": "DifferentPassword!1"})
    assert res_err2.status_code == 400
    
    # Incorrect old password
    res_err3 = test_client.post("/wordsprint/profile", json={"oldPassword": "WrongOldPassword!1", "newPassword": new_pwd, "confirmPassword": new_pwd})
    assert res_err3.status_code == 400
    
    # Successful profile update (Username & Password)
    res_ok = test_client.post("/wordsprint/profile", json={"username": new_uname, "oldPassword": pwd, "newPassword": new_pwd, "confirmPassword": new_pwd})
    assert res_ok.status_code == 200
    assert res_ok.json()["success"] is True

def test_py_game_007_game_details_and_end_action():
    test_client = TestClient(app)
    uname = unique_username("DetailsUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    start_res = test_client.post("/wordsprint/game", data={"action": "start"})
    g_id = start_res.json().get("gameId") or start_res.json().get("game_id")
    
    test_client.post("/wordsprint/guess", data={"gameId": str(g_id), "guess": "APPLE"})
    
    # Get Game Details
    details_res = test_client.get(f"/wordsprint/game?action=details&gameId={g_id}")
    assert details_res.status_code == 200
    assert details_res.json()["gameId"] == g_id
    assert len(details_res.json()["guesses"]) == 1
    
    # End game explicitly
    end_res = test_client.post("/wordsprint/game", data={"action": "end", "gameId": str(g_id), "status": "LOST"})
    assert end_res.status_code == 200
    assert end_res.json()["success"] is True

def test_py_game_008_resumable_game_retrieval():
    test_client = TestClient(app)
    uname = unique_username("ResumeUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    start1 = test_client.post("/wordsprint/game", data={"action": "start"})
    g1_id = start1.json().get("gameId") or start1.json().get("game_id")
    get_res = test_client.get(f"/wordsprint/game?gameId={g1_id}")
    assert get_res.status_code == 200
    assert get_res.json()["gameId"] == g1_id
def test_py_game_009_game_config_action_and_legacy_endpoints():
    test_client = TestClient(app)
    uname = unique_username("CfgUser")
    pwd = "Pass123!$%*@#&"
    test_client.post("/wordsprint/register", data={"username": uname, "password": pwd})
    test_client.post("/wordsprint/login", data={"username": uname, "password": pwd})
    
    # GET game config via GET /wordsprint/game?action=config
    res_cfg = test_client.get("/wordsprint/game?action=config")
    assert res_cfg.status_code == 200
    assert "maxAttempts" in res_cfg.json()
    
    # POST game config via POST /wordsprint/game with action=config
    res_cfg_post = test_client.post("/wordsprint/game", data={"action": "config"})
    assert res_cfg_post.status_code == 200
    assert "maxAttempts" in res_cfg_post.json()
    
    admin_client = TestClient(app)
    admin_client.post("/wordsprint/login", data={"username": "admin", "password": "admin123"})
    admin_client.post("/wordsprint/admin/config", data={"maxAttempts": "5", "maxDailyGames": "3", "gameEnabled": "true"})

