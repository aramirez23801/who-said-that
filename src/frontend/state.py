class AppState:
    def __init__(self):
        self.token: str | None = None
        self.username: str | None = None
        self.session_id: str | None = None
        self.current_round: dict | None = None
        self.score: int = 0

    def clear_session(self):
        self.session_id = None
        self.current_round = None
        self.score = 0

    def logout(self):
        self.token = None
        self.username = None
        self.clear_session()
