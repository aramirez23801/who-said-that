from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.schemas.game import GameResultResponse, StartGameResponse, SubmitAnswerRequest, SubmitAnswerResponse
from backend.services.auth_service import get_current_user
from backend.services.game_service import get_result, start_game, submit_answer

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post("/start", response_model=StartGameResponse)
async def game_start(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await start_game(user_id=current_user.id, db=db)


@router.post("/{session_id}/answer", response_model=SubmitAnswerResponse)
async def game_answer(
    session_id: str,
    body: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await submit_answer(
        session_id=session_id,
        person_id=body.person_id,
        user_id=current_user.id,
        db=db,
    )


@router.get("/{session_id}/result", response_model=GameResultResponse)
async def game_result(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_result(session_id=session_id, user_id=current_user.id, db=db)
