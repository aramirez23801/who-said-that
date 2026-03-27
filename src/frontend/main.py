import flet as ft

from frontend.api_client import APIClient
from frontend.state import AppState
from frontend.theme import BG
from frontend.views.game_view import game_view
from frontend.views.home_view import home_view
from frontend.views.leaderboard_view import leaderboard_view
from frontend.views.login_view import login_view
from frontend.views.result_view import result_view


def main(page: ft.Page) -> None:
    page.title = "Who Said That?!"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.window.width = 960
    page.window.height = 720
    page.window.min_width = 800
    page.window.min_height = 600

    state = AppState()
    client = APIClient()

    def navigate(route: str) -> None:
        page.controls.clear()
        match route:
            case "/login":
                page.add(login_view(page, state, client, navigate))
            case "/home":
                page.add(home_view(page, state, client, navigate))
            case "/game":
                page.add(game_view(page, state, client, navigate))
            case "/result":
                page.add(result_view(page, state, client, navigate))
            case "/leaderboard":
                page.add(leaderboard_view(page, state, client, navigate))
            case _:
                navigate("/login")
        page.update()

    navigate("/login")


ft.run(main)
