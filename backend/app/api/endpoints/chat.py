from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.langgraph import langgraph_app

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    # Use the LangGraph app to get a response
    # We pass the message as the initial state
    initial_state = {"message": chat_message.message}
    result = langgraph_app.invoke(initial_state)
    return ChatResponse(response=result["response"])