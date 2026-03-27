import random

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.game import GameRound, GameSession
from backend.models.person import Person
from backend.models.quote import Quote
from backend.schemas.game import (
    GameResultResponse,
    PersonOption,
    RoundData,
    RoundSummary,
    StartGameResponse,
    SubmitAnswerResponse,
)

ROUNDS_PER_GAME = 5


def _person_to_option(person: Person) -> PersonOption:
    return PersonOption(
        person_id=person.id,
        name=person.name,
        image_url=person.image_url,
        short_bio=person.short_bio,
    )


async def _build_round_data(game_round: GameRound, db: AsyncSession) -> RoundData:
    quote = await db.get(Quote, game_round.quote_id)
    correct_person = await db.get(Person, game_round.correct_person_id)
    wrong_person = await db.get(Person, game_round.wrong_person_id)

    options = [_person_to_option(correct_person), _person_to_option(wrong_person)]
    random.shuffle(options)

    return RoundData(
        round_number=game_round.round_number,
        quote_text=quote.text,
        options=options,
    )


async def start_game(user_id: str, db: AsyncSession) -> StartGameResponse:
    # Fetch all quote IDs and person IDs
    quote_ids = (await db.execute(select(Quote.id))).scalars().all()
    person_ids = (await db.execute(select(Person.id))).scalars().all()

    if len(quote_ids) < ROUNDS_PER_GAME:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Not enough quotes in the database to start a game.",
        )

    selected_quote_ids = random.sample(quote_ids, ROUNDS_PER_GAME)

    # Create the session
    session = GameSession(user_id=user_id)
    db.add(session)
    await db.flush()  # get session.id before creating rounds

    # Pre-generate all 5 rounds
    for round_number, quote_id in enumerate(selected_quote_ids, start=1):
        quote = await db.get(Quote, quote_id)
        correct_person_id = quote.person_id
        decoy_pool = [pid for pid in person_ids if pid != correct_person_id]
        wrong_person_id = random.choice(decoy_pool)

        db.add(GameRound(
            session_id=session.id,
            round_number=round_number,
            quote_id=quote_id,
            correct_person_id=correct_person_id,
            wrong_person_id=wrong_person_id,
        ))

    await db.commit()

    # Return session_id + first round
    first_round = (await db.execute(
        select(GameRound)
        .where(GameRound.session_id == session.id, GameRound.round_number == 1)
    )).scalar_one()

    return StartGameResponse(
        session_id=session.id,
        round=await _build_round_data(first_round, db),
    )


async def submit_answer(
    session_id: str,
    person_id: int,
    user_id: str,
    db: AsyncSession,
) -> SubmitAnswerResponse:
    session = await db.get(GameSession, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found.")
    if session.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game already completed.")

    # Find the current unanswered round
    current_round = (await db.execute(
        select(GameRound)
        .where(GameRound.session_id == session_id, GameRound.user_answer_id.is_(None))
        .order_by(GameRound.round_number)
        .limit(1)
    )).scalar_one_or_none()

    if not current_round:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending rounds.")

    # Validate the submitted person is one of the two options for this round
    if person_id not in (current_round.correct_person_id, current_round.wrong_person_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid answer: not one of the options.")

    # Record the answer
    is_correct = person_id == current_round.correct_person_id
    current_round.user_answer_id = person_id
    current_round.is_correct = is_correct

    if is_correct:
        session.score += 1

    game_over = current_round.round_number == session.total_rounds
    if game_over:
        session.completed = True

    await db.commit()

    correct_person = await db.get(Person, current_round.correct_person_id)

    # Build next round if the game isn't over
    next_round = None
    if not game_over:
        next_game_round = (await db.execute(
            select(GameRound).where(
                GameRound.session_id == session_id,
                GameRound.round_number == current_round.round_number + 1,
            )
        )).scalar_one()
        next_round = await _build_round_data(next_game_round, db)

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_person=_person_to_option(correct_person),
        current_score=session.score,
        round_number=current_round.round_number,
        game_over=game_over,
        next_round=next_round,
    )


async def get_result(session_id: str, user_id: str, db: AsyncSession) -> GameResultResponse:
    session = await db.get(GameSession, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found.")
    if not session.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game is not completed yet.")

    rounds = (await db.execute(
        select(GameRound)
        .where(GameRound.session_id == session_id)
        .order_by(GameRound.round_number)
    )).scalars().all()

    summaries = []
    for r in rounds:
        quote = await db.get(Quote, r.quote_id)
        correct_person = await db.get(Person, r.correct_person_id)
        user_answer_person = await db.get(Person, r.user_answer_id) if r.user_answer_id else None

        summaries.append(RoundSummary(
            round_number=r.round_number,
            quote_text=quote.text,
            correct_person_name=correct_person.name,
            user_answer_name=user_answer_person.name if user_answer_person else None,
            is_correct=r.is_correct,
        ))

    return GameResultResponse(
        session_id=session.id,
        score=session.score,
        total_rounds=session.total_rounds,
        rounds=summaries,
    )
