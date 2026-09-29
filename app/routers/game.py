from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from typing import Optional
from app.game import (
    get_game_config,
    create_new_game,
    get_game_by_id,
    get_guesses_for_game,
    update_game_status,
    process_guess
)
from app.database import fetch_one

router = APIRouter(tags=["Game REST API"])

async def get_request_params(request: Request):
    """Extract params from query, form data, or JSON body."""
    params = dict(request.query_params)
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                params.update(body)
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        try:
            form = await request.form()
            for k, v in form.items():
                params[k] = v
        except Exception:
            pass

    return params

def get_current_user_id(request: Request) -> int | None:
    """Get authenticated user_id from session."""
    return request.session.get("user_id")

@router.get("/game")
@router.post("/game")
@router.get("/wordsprint/game")
@router.post("/wordsprint/game")
async def handle_game(request: Request):
    user_id = get_current_user_id(request)
    params = await get_request_params(request)
    action = params.get("action")

    if not action:
        game_id_param = params.get("gameId")
        if game_id_param and request.method == "GET":
            action = "details"
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Missing action"}
            )

    action = action.lower().strip()

    if action == "config":
        config = get_game_config()
        return {
            "success": True,
            "maxAttempts": config["max_attempts"],
            "maxDailyGames": config["max_daily_games"],
            "gameEnabled": config["game_enabled"]
        }

    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Please log in first to play WordSprint."}
        )

    if action == "start":
        game, msg = create_new_game(user_id)
        if not game:
            status_code = status.HTTP_403_FORBIDDEN if "Daily limit" in msg else status.HTTP_400_BAD_REQUEST
            return JSONResponse(
                status_code=status_code,
                content={"success": False, "message": msg}
            )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "gameId": game["game_id"],
                "userId": game["user_id"],
                "status": game["status"],
                "maxAttempts": game["max_attempts"]
            }
        )

    elif action == "details":
        game_id_param = params.get("gameId")
        if not game_id_param:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Missing gameId"}
            )
        try:
            game_id = int(game_id_param)
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Invalid gameId"}
            )

        game = get_game_by_id(game_id)
        if not game:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Game not found"}
            )

        if game["user_id"] != user_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"success": False, "message": "Access denied. You can only view your own game."}
            )

        guesses_raw = get_guesses_for_game(game_id)
        config = get_game_config()

        formatted_guesses = [
            {
                "guessNumber": g["guess_number"],
                "guessedWord": g["guessed_word"],
                "result": g["result"]
            }
            for g in guesses_raw
        ]

        return {
            "success": True,
            "gameId": game["game_id"],
            "userId": game["user_id"],
            "status": game["status"],
            "maxAttempts": config["max_attempts"],
            "guesses": formatted_guesses
        }

    elif action == "end":
        game_id_param = params.get("gameId")
        status_param = params.get("status")

        if not game_id_param or not status_param:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Missing gameId or status"}
            )

        if status_param not in ("WON", "LOST"):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Status must be WON or LOST"}
            )

        try:
            game_id = int(game_id_param)
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Invalid gameId"}
            )

        game = get_game_by_id(game_id)
        if not game:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Game not found"}
            )

        if game["user_id"] != user_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"success": False, "message": "Access denied. You can only end your own game."}
            )

        success = update_game_status(game_id, status_param)
        if success:
            return {"success": True, "message": "Game ended successfully"}
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Unable to update game status"}
            )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "message": "Invalid action"}
    )

@router.post("/api/game/start")
async def api_start_game(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Please log in first"}
        )
    game, msg = create_new_game(user_id)
    if not game:
        status_code = status.HTTP_403_FORBIDDEN if "Daily limit" in msg else status.HTTP_400_BAD_REQUEST
        return JSONResponse(status_code=status_code, content={"success": False, "message": msg})
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "gameId": game["game_id"],
            "userId": game["user_id"],
            "status": game["status"],
            "maxAttempts": game["max_attempts"]
        }
    )

@router.get("/api/game/current")
async def api_get_current_game(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Please log in first"}
        )
    active = fetch_one(
        "SELECT game_id FROM games WHERE user_id = %s AND status = 'IN_PROGRESS' ORDER BY started_at DESC LIMIT 1",
        (user_id,)
    )
    if not active:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "No active game found"}
        )
    game_id = active["game_id"]
    game = get_game_by_id(game_id)
    guesses_raw = get_guesses_for_game(game_id)
    config = get_game_config()

    return {
        "success": True,
        "gameId": game["game_id"],
        "userId": game["user_id"],
        "status": game["status"],
        "maxAttempts": config["max_attempts"],
        "guesses": [
            {
                "guessNumber": g["guess_number"],
                "guessedWord": g["guessed_word"],
                "result": g["result"]
            }
            for g in guesses_raw
        ]
    }

@router.get("/api/game/{game_id}")
async def api_get_game_by_id(game_id: int, request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Please log in first"}
        )
    game = get_game_by_id(game_id)
    if not game:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "Game not found"}
        )
    if game["user_id"] != user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": "Access denied. You can only view your own game."}
        )

    guesses_raw = get_guesses_for_game(game_id)
    config = get_game_config()

    return {
        "success": True,
        "gameId": game["game_id"],
        "userId": game["user_id"],
        "status": game["status"],
        "maxAttempts": config["max_attempts"],
        "guesses": [
            {
                "guessNumber": g["guess_number"],
                "guessedWord": g["guessed_word"],
                "result": g["result"]
            }
            for g in guesses_raw
        ]
    }

@router.post("/guess")
@router.post("/wordsprint/guess")
@router.post("/api/guess")
async def handle_guess(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Please log in first"}
        )

    params = await get_request_params(request)
    game_id_param = params.get("gameId")
    guessed_word = params.get("guess") or params.get("guessedWord")
    guess_num_param = params.get("guessNumber")

    if not game_id_param or not guessed_word:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "Missing gameId or guess parameter"}
        )

    try:
        game_id = int(game_id_param)
        guess_number = int(guess_num_param) if guess_num_param else None
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "Invalid gameId or guessNumber"}
        )

    result_data, status_code, err_msg = process_guess(game_id, user_id, guessed_word, guess_number)

    if not result_data:
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": err_msg}
        )

    return result_data
