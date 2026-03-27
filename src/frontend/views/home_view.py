import flet as ft

from frontend import theme as t


def home_view(page: ft.Page, state, client, navigate) -> ft.Container:
    error_msg = ft.Text("", color=t.DANGER, size=t.FONT_SMALL, text_align=ft.TextAlign.CENTER)

    def on_start(e) -> None:
        error_msg.value = ""
        try:
            data = client.start_game()
            state.session_id = data["session_id"]
            state.current_round = data["round"]
            state.score = 0
            navigate("/game")
        except ValueError as ex:
            error_msg.value = str(ex)
            page.update()

    def on_leaderboard(e) -> None:
        navigate("/leaderboard")

    def on_logout(e) -> None:
        state.logout()
        client.clear_token()
        navigate("/login")

    return ft.Container(
        expand=True,
        bgcolor=t.BG,
        content=ft.Stack(
            expand=True,
            controls=[
                # --- Main centered content ---
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        ft.Text(
                            "WHO SAID THAT?!",
                            size=t.FONT_TITLE,
                            weight=ft.FontWeight.W_900,
                            color=t.TEXT,
                            style=ft.TextStyle(letter_spacing=t.LETTER_SPACING_TITLE),
                        ),
                        ft.Container(height=8),
                        ft.Container(bgcolor=t.ACCENT, height=2, width=320),
                        ft.Container(height=14),
                        ft.Text(
                            f"Welcome back, {state.username}. Try not to embarrass yourself.",
                            size=t.FONT_SMALL,
                            color=t.SUBTEXT,
                            italic=True,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=52),

                        # START GAME — primary, centered
                        ft.Container(
                            width=320,
                            content=ft.Text(
                                "START GAME",
                                color=t.TEXT,
                                size=t.FONT_BODY,
                                weight=ft.FontWeight.W_700,
                                text_align=ft.TextAlign.CENTER,
                                style=ft.TextStyle(letter_spacing=t.LETTER_SPACING_BTN),
                            ),
                            bgcolor=t.ACCENT,
                            border_radius=2,
                            padding=ft.padding.symmetric(vertical=16),
                            on_click=on_start,
                            ink=True,
                        ),
                        ft.Container(height=12),

                        # LEADERBOARD — secondary
                        ft.Container(
                            width=320,
                            content=ft.Text(
                                "LEADERBOARD",
                                color=t.TEXT,
                                size=t.FONT_SMALL,
                                weight=ft.FontWeight.W_600,
                                text_align=ft.TextAlign.CENTER,
                                style=ft.TextStyle(letter_spacing=t.LETTER_SPACING_BTN),
                            ),
                            border=ft.border.all(1, t.BORDER),
                            border_radius=2,
                            padding=ft.padding.symmetric(vertical=12),
                            on_click=on_leaderboard,
                            ink=True,
                        ),
                        ft.Container(height=20),
                        ft.Container(content=error_msg, height=20),
                    ],
                ),

                # --- LOGOUT — top right ---
                ft.Container(
                    right=24,
                    top=20,
                    content=ft.Container(
                        content=ft.Text(
                            "LOGOUT",
                            color=t.SUBTEXT,
                            size=t.FONT_SMALL,
                            weight=ft.FontWeight.W_600,
                            style=ft.TextStyle(letter_spacing=1),
                        ),
                        border=ft.border.all(1, t.BORDER),
                        border_radius=2,
                        padding=ft.padding.symmetric(horizontal=14, vertical=8),
                        on_click=on_logout,
                        ink=True,
                    ),
                ),
            ],
        ),
    )
