import httpx

BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0


class APIClient:
    def __init__(self):
        self._token: str | None = None

    def set_token(self, token: str) -> None:
        self._token = token

    def clear_token(self) -> None:
        self._token = None

    @property
    def _auth_headers(self) -> dict:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    def _handle(self, response: httpx.Response) -> dict:
        if response.is_error:
            try:
                body = response.json()
                detail = body.get("detail", "Unknown error")
                if isinstance(detail, list):
                    msg = detail[0].get("msg", "Validation error")
                    msg = msg.replace("Value error, ", "")
                else:
                    msg = str(detail)
            except Exception:
                msg = f"Server error ({response.status_code})"
            raise ValueError(msg)
        return response.json()

    @staticmethod
    def _wrap(fn):
        """Converts httpx transport errors into ValueError so views only catch one type."""
        try:
            return fn()
        except ValueError:
            raise
        except httpx.ConnectError:
            raise ValueError("Cannot reach server. Is the backend running?")
        except httpx.TimeoutException:
            raise ValueError("Request timed out. Try again.")
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")

    # --- Auth ---

    def register(self, username: str, password: str) -> dict:
        return self._wrap(lambda: self._handle(httpx.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": username, "password": password},
            timeout=TIMEOUT,
        )))

    def login(self, username: str, password: str) -> dict:
        return self._wrap(lambda: self._handle(httpx.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=TIMEOUT,
        )))

    # --- Game ---

    def start_game(self) -> dict:
        return self._wrap(lambda: self._handle(httpx.post(
            f"{BASE_URL}/api/game/start",
            headers=self._auth_headers,
            timeout=TIMEOUT,
        )))

    def submit_answer(self, session_id: str, person_id: int) -> dict:
        return self._wrap(lambda: self._handle(httpx.post(
            f"{BASE_URL}/api/game/{session_id}/answer",
            headers=self._auth_headers,
            json={"person_id": person_id},
            timeout=TIMEOUT,
        )))

    def get_result(self, session_id: str) -> dict:
        return self._wrap(lambda: self._handle(httpx.get(
            f"{BASE_URL}/api/game/{session_id}/result",
            headers=self._auth_headers,
            timeout=TIMEOUT,
        )))

    # --- Leaderboard ---

    def get_leaderboard(self, limit: int = 20) -> dict:
        return self._wrap(lambda: self._handle(httpx.get(
            f"{BASE_URL}/api/leaderboard",
            params={"limit": limit},
            timeout=TIMEOUT,
        )))
