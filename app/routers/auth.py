from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import re
from app.auth import (
    authenticate_user,
    register_user,
    find_user_by_id,
    find_user_by_username,
    validate_credentials,
    hash_password,
    verify_password
)
from app.database import fetch_all, execute_query

router = APIRouter(tags=["Authentication"])

class RegisterSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = "player"

class LoginSchema(BaseModel):
    username: Optional[str] = None
    uname: Optional[str] = None
    password: Optional[str] = None

async def parse_request_credentials(request: Request):
    """Extract credentials from JSON body or Form data."""
    content_type = request.headers.get("content-type", "")
    username = None
    password = None
    role = "player"
    old_password = None
    new_password = None
    confirm_password = None

    if "application/json" in content_type:
        try:
            data = await request.json()
            username = data.get("username") or data.get("uname")
            password = data.get("password")
            role = data.get("role", "player")
            old_password = data.get("oldPassword")
            new_password = data.get("newPassword") or data.get("password")
            confirm_password = data.get("confirmPassword")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            username = form.get("username") or form.get("uname")
            password = form.get("password")
            role = form.get("role", "player")
            old_password = form.get("oldPassword")
            new_password = form.get("newPassword") or form.get("password")
            confirm_password = form.get("confirmPassword")
        except Exception:
            pass

    return {
        "username": username,
        "password": password,
        "role": role,
        "oldPassword": old_password,
        "newPassword": new_password,
        "confirmPassword": confirm_password
    }

@router.post("/register")
@router.post("/wordsprint/register")
async def register(request: Request):
    creds = await parse_request_credentials(request)
    username = creds.get("username")
    password = creds.get("password")
    role = creds.get("role") or "player"

    if not username or not password or role is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "Username, password and role are required"}
        )

    val_err = validate_credentials(username, password)
    if val_err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": val_err}
        )

    success, message = register_user(username, password, role)
    if success:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "message": message}
        )
    elif message == "Username already exists":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"success": False, "message": message}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": message}
        )

@router.post("/login")
@router.post("/wordsprint/login")
async def login(request: Request):
    creds = await parse_request_credentials(request)
    username = creds.get("username")
    password = creds.get("password")

    if not username or not password:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "Provide the username and password!"}
        )

    user = authenticate_user(username, password)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Invalid username or password!"}
        )

    request.session["user_id"] = user["user_id"]
    request.session["uname"] = user["uname"]
    request.session["role"] = user["role"]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Login successful"}
    )

@router.post("/logout")
@router.post("/wordsprint/logout")
async def logout(request: Request):
    request.session.clear()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Logout successful"}
    )

@router.get("/profile")
@router.get("/wordsprint/profile")
async def get_profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Please log in first"}
        )

    user = find_user_by_id(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "User not found"}
        )

    games_query = """
        SELECT game_id, status, started_at, completed_at
        FROM games
        WHERE user_id = %s
        ORDER BY started_at DESC
    """
    games_raw = fetch_all(games_query, (user_id,))
    
    total_games = len(games_raw)
    wins = sum(1 for g in games_raw if g.get("status") == "WON")
    losses = sum(1 for g in games_raw if g.get("status") == "LOST")
    in_progress = sum(1 for g in games_raw if g.get("status") == "IN_PROGRESS")

    games_formatted = []
    for g in games_raw:
        item = {
            "gameId": g["game_id"],
            "status": g["status"],
            "startedAt": str(g["started_at"]) if g.get("started_at") else ""
        }
        if g.get("completed_at"):
            item["completedAt"] = str(g["completed_at"])
        games_formatted.append(item)

    return {
        "success": True,
        "userId": user["user_id"],
        "username": user["uname"],
        "role": user["role"],
        "createdAt": str(user["created_at"]) if user.get("created_at") else "",
        "stats": {
            "totalGames": total_games,
            "wins": wins,
            "losses": losses,
            "inProgress": in_progress
        },
        "games": games_formatted
    }

@router.post("/profile")
@router.post("/wordsprint/profile")
async def update_profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Please log in first"}
        )

    creds = await parse_request_credentials(request)
    new_username = creds.get("username")
    old_password = creds.get("oldPassword")
    new_password = creds.get("newPassword")
    confirm_password = creds.get("confirmPassword")

    pwd_hash = None
    is_password_change = (
        (old_password and old_password.strip()) or
        (new_password and new_password.strip()) or
        (confirm_password and confirm_password.strip())
    )

    if is_password_change:
        if not old_password or not old_password.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Old password is required to change password."}
            )
        if not new_password or not new_password.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "New password is required."}
            )
        if not confirm_password or not confirm_password.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Please confirm your new password."}
            )
        if new_password.strip() != confirm_password.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "New password and confirm password do not match!"}
            )

        current_user = find_user_by_id(user_id)
        if not current_user or not verify_password(old_password.strip(), current_user["pwd_hash"]):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Current (old) password is incorrect!"}
            )

        np = new_password.strip()
        if len(np) < 5 or not re.search(r"[A-Za-z]", np) or not re.search(r"\d", np) or not re.search(r"[$%*@#&!]", np):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "New password must be at least 5 characters and contain letters, numbers, and special chars ($, %, *, @, #, !, &)"}
            )

        pwd_hash = hash_password(np)

    if new_username and new_username.strip():
        uname = new_username.strip()
        if len(uname) < 5 or not re.search(r"[A-Z]", uname) or not re.search(r"[a-z]", uname):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Username must be at least 5 characters and contain uppercase and lowercase letters"}
            )
        existing = find_user_by_username(uname)
        if existing and existing["user_id"] != user_id:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"success": False, "message": "Username already taken by another user"}
            )

    update_fields = []
    params = []

    if new_username and new_username.strip():
        update_fields.append("uname = %s")
        params.append(new_username.strip())

    if pwd_hash:
        update_fields.append("pwd_hash = %s")
        params.append(pwd_hash)

    if not update_fields:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "No changes made or update failed"}
        )

    params.append(user_id)
    set_clause = ", ".join(update_fields)
    query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
    affected = execute_query(query, tuple(params))

    if affected > 0:
        if new_username and new_username.strip():
            request.session["uname"] = new_username.strip()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "Profile updated successfully"}
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "message": "No changes made or update failed"}
    )
