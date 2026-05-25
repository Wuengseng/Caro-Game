from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np

from board import Board
from ai_easy import AIEasy
from ai_medium import AIMedium
from ai_hard import AIHard

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MoveRequest(BaseModel):
    grid: List[List[int]]
    difficulty: str
    ai_player: int
    player: int

@app.post("/move")
def get_move(req: MoveRequest):
    board = Board(len(req.grid))
    board.grid = np.array(req.grid)
    
    if req.difficulty == "easy":
        ai = AIEasy(req.ai_player, req.player)
    elif req.difficulty == "medium":
        ai = AIMedium(req.ai_player, req.player, depth=3) # Limit depth for web responsiveness
    else:
        ai = AIHard(req.ai_player, req.player)
        
    ai_move = ai.get_best_move(board)
    if ai_move:
        return {"r": int(ai_move[0]), "c": int(ai_move[1])}
    return {"r": -1, "c": -1}
