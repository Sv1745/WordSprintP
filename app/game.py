from datetime import datetime
from app.database import fetch_one, fetch_all, execute_query, execute_insert

DEFAULT_WORDS = [
    "APPLE", "BRAIN", "CHAIR", "DREAM", "EARTH",
    "FLAME", "GRAPE", "HEART", "IMAGE", "JUICE",
    "KNIFE", "LIGHT", "MUSIC", "NIGHT", "OCEAN",
    "PLANT", "QUEEN", "RIGHT", "SMILE", "TRAIN"
]

def seed_words_if_empty():
    """Ensure database has initial word list if empty."""
    count_row = fetch_one("SELECT COUNT(*) as count FROM words")
    if not count_row or count_row["count"] < 20:
        for w in DEFAULT_WORDS:
            execute_query(
                "INSERT INTO words (word) VALUES (%s) ON CONFLICT (word) DO NOTHING",
                (w,)
            )

def get_game_config() -> dict:
    """Retrieve system game configuration."""
    config = fetch_one("SELECT max_attempts, max_daily_games, game_enabled FROM game_config WHERE config_id = 1")
    if not config:
        return {"max_attempts": 5, "max_daily_games": 3, "game_enabled": True}
    return {
        "max_attempts": config["max_attempts"],
        "max_daily_games": config["max_daily_games"],
        "game_enabled": bool(config["game_enabled"])
    }

def get_random_word():
    """Fetch a random 5-letter word from database."""
    seed_words_if_empty()
    return fetch_one("SELECT word_id, word FROM words ORDER BY RANDOM() LIMIT 1")

def get_daily_games_count(user_id: int) -> int:
    """Get the number of games played by user today."""
    row = fetch_one(
        "SELECT COUNT(*) as count FROM games WHERE user_id = %s AND started_at >= CURRENT_DATE",
        (user_id,)
    )
    return row["count"] if row else 0

def create_new_game(user_id: int):
    """Start a new game for user after checking config and limits."""
    config = get_game_config()
    if not config["game_enabled"]:
        return None, "WordSprint is currently disabled by Admin."

    daily_count = get_daily_games_count(user_id)
    if daily_count >= config["max_daily_games"]:
        return None, f"Daily limit reached! You can only play a maximum of {config['max_daily_games']} games per day."

    word = get_random_word()
    if not word:
        return None, "Unable to select a word for the game."

    query = """
        INSERT INTO games (user_id, word_id, started_at, status)
        VALUES (%s, %s, %s, %s)
        RETURNING game_id, user_id, word_id, started_at, status
    """
    game = execute_insert(query, (user_id, word["word_id"], datetime.now(), "IN_PROGRESS"))
    if not game:
        return None, "Unable to start game. Please try again later."

    game["max_attempts"] = config["max_attempts"]
    return game, "Game started successfully"

def get_game_by_id(game_id: int):
    """Retrieve game by game_id."""
    return fetch_one(
        "SELECT game_id, user_id, word_id, started_at, completed_at, status FROM games WHERE game_id = %s",
        (game_id,)
    )

def get_guesses_for_game(game_id: int):
    """Retrieve all guesses for a game ordered by guess_number."""
    return fetch_all(
        "SELECT guess_id, game_id, guess_number, guessed_word, result, created_at FROM guesses WHERE game_id = %s ORDER BY guess_number ASC",
        (game_id,)
    )

def update_game_status(game_id: int, status: str) -> bool:
    """Mark a game as WON or LOST and set completed_at timestamp."""
    if status not in ("WON", "LOST"):
        return False
    affected = execute_query(
        "UPDATE games SET completed_at = %s, status = %s WHERE game_id = %s",
        (datetime.now(), status, game_id)
    )
    return affected > 0

def evaluate_guess_feedback(user_guess: str, target_word: str) -> str:
    """
    Compute 2-pass feedback string:
    'G' = Green (Correct letter & position)
    'Y' = Yellow (Correct letter, wrong position)
    'B' = Grey (Absent letter)
    """
    user_guess = user_guess.upper()
    target_word = target_word.upper()

    result = ["B"] * 5
    target_matched = [False] * 5
    guess_matched = [False] * 5

    # Pass 1: Exact matches
    for i in range(5):
        if user_guess[i] == target_word[i]:
            result[i] = "G"
            target_matched[i] = True
            guess_matched[i] = True

    # Pass 2: Partial matches
    for i in range(5):
        if not guess_matched[i]:
            c = user_guess[i]
            for j in range(5):
                if not target_matched[j] and target_word[j] == c:
                    result[i] = "Y"
                    target_matched[j] = True
                    break

    return "".join(result)

def process_guess(game_id: int, user_id: int, guessed_word: str, requested_guess_number: int = None):
    """
    Validate and process a guess submission.
    Returns (response_dict, http_status_code, error_message).
    """
    game = get_game_by_id(game_id)
    if not game:
        return None, 404, "Game not found"

    if game["user_id"] != user_id:
        return None, 403, "Access denied. You can only play your own game."

    if game["status"] != "IN_PROGRESS":
        return None, 400, f"Game has already ended with status {game['status']}."

    target_word_obj = fetch_one("SELECT word_id, word FROM words WHERE word_id = %s", (game["word_id"],))
    if not target_word_obj:
        return None, 500, "Target word not found"

    target_word = target_word_obj["word"].strip().upper()
    user_guess = guessed_word.strip().upper()

    if len(user_guess) != 5:
        return None, 400, "Guess must be a 5-letter word"

    config = get_game_config()
    max_attempts = config["max_attempts"]

    previous_guesses = get_guesses_for_game(game_id)
    if len(previous_guesses) >= max_attempts:
        update_game_status(game_id, "LOST")
        return None, 400, f"Maximum guess limit ({max_attempts}) reached for this game."

    guess_number = len(previous_guesses) + 1

    result = evaluate_guess_feedback(user_guess, target_word)
    is_correct = (user_guess == target_word)

    # Save guess
    try:
        execute_query(
            "INSERT INTO guesses (game_id, guess_number, guessed_word, result, created_at) VALUES (%s, %s, %s, %s, %s)",
            (game_id, guess_number, user_guess, result, datetime.now())
        )
    except Exception as e:
        return None, 400, f"Failed to save guess: {str(e)}"

    status_str = "IN_PROGRESS"
    if is_correct:
        status_str = "WON"
        update_game_status(game_id, "WON")
    elif guess_number >= max_attempts:
        status_str = "LOST"
        update_game_status(game_id, "LOST")

    res = {
        "success": True,
        "isCorrect": is_correct,
        "result": result,
        "status": status_str,
        "maxAttempts": max_attempts
    }
    if is_correct or status_str == "LOST":
        res["targetWord"] = target_word

    return res, 200, ""
