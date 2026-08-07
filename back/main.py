import time
from tools.registry import (
    get_tool_schemas,
    get_tool_function
)
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from prompts import SYSTEM_PROMPT
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import secrets
from contextlib import asynccontextmanager
from db import init_table, save_message, get_chat_history
from auth import (
    GOOGLE_CLIENT_ID, 
    GOOGLE_REDIRECT_URI, 
    exchange_code_for_google_user, 
    create_access_token, 
    verify_jwt_token
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_table()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_TOOL_ROUNDS = 8

@app.get("/api/auth/login")
def login_with_google():
    state = secrets.token_urlsafe(32)

    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&scope=openid%20email%20profile"
        f"&state={state}"
    )

    response = RedirectResponse(url=google_auth_url)

    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=600,
        samesite="lax",
        secure=False,
    )

    return response



@app.get("/api/auth/google/callback")
async def google_callback(request: Request, code: str, state: str):
    stored_state = request.cookies.get("oauth_state")
    print(f"Stored Cookie State: {stored_state}")
    print(f"Returned URL State: {state}")

    if not stored_state:
        print("ERROR: Cookie was missing entirely from the request.")
        raise HTTPException(status_code=400, detail="Missing oauth_state cookie.")
        
    if stored_state != state:
        print("ERROR: CSRF state mismatch!")
        raise HTTPException(status_code=400, detail="CSRF validation failed.")

    try:
        user_info = await exchange_code_for_google_user(code)
    except Exception as e:
        print(f"ERROR: Google code exchange failed: {e}")
        raise HTTPException(status_code=400, detail=f"Google token exchange failed: {str(e)}")

    user_id = f"google_{user_info['id']}"
    email = user_info.get("email")

    app_jwt = create_access_token(data={"user_id": user_id, "email": email})

    response = RedirectResponse(f"http://localhost:5173/#token={app_jwt}")
    response.delete_cookie("oauth_state")
    print(request.cookies)
    return response



class QueryRequest(BaseModel):
    message: str

@app.get("/api/history")
async def fetch_history(user: dict = Depends(verify_jwt_token)):
    user_id = user["user_id"]
    items = get_chat_history(user_id)
    return {"history": items, "user_email": user.get("email")}



@app.post("/api/chat")
async def chat(
    request: QueryRequest,
    user: dict = Depends(verify_jwt_token)
):

    user_id = user["user_id"]


    save_message(
        user_id,
        "user",
        request.message
    )


    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


    history = get_chat_history(user_id)

    user_history = [
        msg for msg in history
        if msg["role"] == "user"
    ]

    messages.extend(
        user_history[-1:]
    )


    async_ollama = ollama.AsyncClient()


    ai_reply = (
        "I could not complete your request."
    )


    agent_state = {
        "tools_used": [],
        "tool_results": []
    }


    tool_failures = 0


    try:

        for round_num in range(MAX_TOOL_ROUNDS):

            print(
                f"\n===== Agent Round {round_num+1} ====="
            )

            start = time.time()

            print("Calling Ollama...")


            response = await async_ollama.chat(
                model="qwen2.5:7b",

                messages=messages,

                tools=get_tool_schemas(),

            )

            print(
                "Ollama finished:",
                time.time() - start,
                "seconds"
            )


            messages.append(
                response.message
            )

            if not response.message.tool_calls:

                ai_reply = (
                    response.message.content
                )

                break



            for tool_call in response.message.tool_calls:


                tool_name = (
                    tool_call.function.name
                )


                arguments = (
                    tool_call.function.arguments
                )


                print(
                    "Tool:",
                    tool_name
                )

                print(
                    "Args:",
                    arguments
                )


                tool_function = get_tool_function(
                    tool_name
                )


                if tool_function is None:

                    result = (
                        f"Unknown tool: {tool_name}"
                    )

                    tool_failures += 1


                else:

                    try:

                        result = await tool_function(
                            **arguments
                        )

                        result = str(result)

                        if len(result) > 3000:
                            result = result[:3000] + "...truncated"


                        agent_state[
                            "tools_used"
                        ].append(
                            tool_name
                        )


                        agent_state[
                            "tool_results"
                        ].append(
                            {
                                "tool": tool_name,
                                "result": result
                            }
                        )


                    except Exception as e:

                        result = (
                            f"Tool failed: {e}"
                        )

                        tool_failures += 1



                messages.append(
                    {
                        "role": "tool",
                        "name": tool_name,
                        "content": str(result)
                    }
                )



            if tool_failures >= 3:

                ai_reply = (
                    "I could not access "
                    "the required information."
                )

                break



        else:

            ai_reply = (
                "I reached my maximum "
                "planning steps."
            )



        save_message(
            user_id,
            "assistant",
            ai_reply
        )


        print(
            "TOOLS USED:",
            agent_state["tools_used"]
        )


        return {
            "reply": ai_reply
        }



    except Exception as e:

        print(
            "CHAT ERROR:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )