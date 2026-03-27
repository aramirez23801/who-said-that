from pydantic import BaseModel


class PersonOption(BaseModel):
    person_id: int
    name: str
    image_url: str
    short_bio: str


class RoundData(BaseModel):
    round_number: int
    quote_text: str
    options: list[PersonOption]  # always 2, position randomized


class StartGameResponse(BaseModel):
    session_id: str
    round: RoundData


class SubmitAnswerRequest(BaseModel):
    person_id: int


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_person: PersonOption
    current_score: int
    round_number: int
    game_over: bool
    next_round: RoundData | None = None


class RoundSummary(BaseModel):
    round_number: int
    quote_text: str
    correct_person_name: str
    user_answer_name: str | None
    is_correct: bool | None


class GameResultResponse(BaseModel):
    session_id: str
    score: int
    total_rounds: int
    rounds: list[RoundSummary]
