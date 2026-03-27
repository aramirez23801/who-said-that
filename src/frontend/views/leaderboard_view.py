import flet as ft

from frontend import theme as t

# Score tier colors
_BG_HIGH = "#0a2010"       # 5/5 — dark green row
_BG_LOW = "#200a0a"        # 0-2/5 — dark red row
_SCORE_HIGH = "#5acd7a"    # 5/5 score text
_SCORE_LOW = "#cd5a5a"     # 0-2/5 score text


def leaderboard_view(page: ft.Page, state, client, navigate) -> ft.Container:
    # --- Fetch data ---
    try:
        data = client.get_leaderboard()
        entries = data.get("entries", [])
        fetch_error = ""
    except ValueError as ex:
        entries = []
        fetch_error = str(ex)

    # --- Table rows ---
    def make_row(entry: dict, rank: int) -> ft.Container:
        is_me = entry.get("username") == state.username
        score = entry.get("score", 0)
        username = entry.get("username", "?")

        # Background based on score tier
        if score == 5:
            row_bg = _BG_HIGH
        elif score <= 2:
            row_bg = _BG_LOW
        else:
            row_bg = "transparent"

        # Score text color based on tier
        if score == 5:
            score_color = _SCORE_HIGH
        elif score <= 2:
            score_color = _SCORE_LOW
        else:
            score_color = t.TEXT

        # Rank color: top 3 get accent
        rank_color = t.ACCENT if rank <= 3 else t.SUBTEXT

        # Current user: bold white name + "(you)" tag
        name_weight = ft.FontWeight.W_700 if is_me else ft.FontWeight.W_400
        name_color = t.TEXT if is_me else t.SUBTEXT
        display_name = username + (" (you)" if is_me else "")

        return ft.Container(
            bgcolor=row_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, t.BORDER)),
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=16,
                        controls=[
                            ft.Container(
                                width=36,
                                content=ft.Text(
                                    f"#{rank}",
                                    color=rank_color,
                                    size=t.FONT_SMALL,
                                    weight=ft.FontWeight.W_700,
                                    style=ft.TextStyle(letter_spacing=1),
                                ),
                            ),
                            ft.Text(
                                display_name,
                                color=name_color,
                                size=t.FONT_BODY,
                                weight=name_weight,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"{score} / 5",
                        color=score_color,
                        size=t.FONT_BODY,
                        weight=ft.FontWeight.W_700,
                    ),
                ],
            ),
        )

    # --- Table header ---
    table_header = ft.Container(
        bgcolor=t.SURFACE,
        border=ft.border.only(bottom=ft.BorderSide(1, t.BORDER)),
        border_radius=ft.border_radius.only(top_left=6, top_right=6),
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "PLAYER",
                    color=t.SUBTEXT,
                    size=t.FONT_SMALL,
                    weight=ft.FontWeight.W_600,
                    style=ft.TextStyle(letter_spacing=2),
                ),
                ft.Text(
                    "SCORE",
                    color=t.SUBTEXT,
                    size=t.FONT_SMALL,
                    weight=ft.FontWeight.W_600,
                    style=ft.TextStyle(letter_spacing=2),
                ),
            ],
        ),
    )

    if fetch_error:
        table_body = ft.Container(
            bgcolor=t.SURFACE,
            border_radius=ft.border_radius.only(bottom_left=6, bottom_right=6),
            padding=ft.padding.all(24),
            content=ft.Text(fetch_error, color=t.DANGER, size=t.FONT_SMALL, italic=True),
        )
    elif not entries:
        table_body = ft.Container(
            bgcolor=t.SURFACE,
            border_radius=ft.border_radius.only(bottom_left=6, bottom_right=6),
            padding=ft.padding.symmetric(horizontal=20, vertical=32),
            content=ft.Text(
                "No games completed yet. Be the first to embarrass yourself.",
                color=t.SUBTEXT,
                size=t.FONT_SMALL,
                italic=True,
                text_align=ft.TextAlign.CENTER,
            ),
        )
    else:
        rows = [make_row(e, i + 1) for i, e in enumerate(entries)]
        table_body = ft.Column(
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            controls=rows,
        )

    # --- Nav handlers ---
    def on_play(e) -> None:
        state.clear_session()
        try:
            game_data = client.start_game()
            state.session_id = game_data["session_id"]
            state.current_round = game_data["round"]
            state.score = 0
            navigate("/game")
        except ValueError as ex:
            nav_error.value = str(ex)
            page.update()

    def on_home(e) -> None:
        navigate("/home")

    nav_error = ft.Text("", color=t.DANGER, size=t.FONT_SMALL)

    def _btn(label: str, handler, primary: bool) -> ft.Container:
        return ft.Container(
            expand=True,
            content=ft.Text(
                label,
                color=t.TEXT,
                size=t.FONT_SMALL,
                weight=ft.FontWeight.W_700,
                text_align=ft.TextAlign.CENTER,
                style=ft.TextStyle(letter_spacing=2),
            ),
            bgcolor=t.ACCENT if primary else "transparent",
            border=ft.border.all(1, t.ACCENT if primary else t.BORDER),
            border_radius=4,
            padding=ft.padding.symmetric(vertical=13),
            on_click=handler,
            ink=True,
        )

    return ft.Container(
        expand=True,
        bgcolor=t.BG,
        content=ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                # width=700, NO expand=True — Row stretch provides full height
                ft.Container(
                    width=700,
                    padding=ft.padding.only(top=24, bottom=20),
                    content=ft.Column(
                        expand=True,
                        spacing=16,
                        controls=[
                            # Header bar
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        "WHO SAID THAT?!",
                                        color=t.ACCENT,
                                        size=t.FONT_SMALL,
                                        weight=ft.FontWeight.W_900,
                                        style=ft.TextStyle(letter_spacing=3),
                                    ),
                                    ft.Text(
                                        "HALL OF SHAME",
                                        color=t.SUBTEXT,
                                        size=t.FONT_SMALL,
                                        weight=ft.FontWeight.W_600,
                                        style=ft.TextStyle(letter_spacing=2),
                                    ),
                                ],
                            ),
                            ft.Container(height=1, bgcolor=t.BORDER),

                            ft.Text(
                                "LEADERBOARD",
                                color=t.TEXT,
                                size=t.FONT_HEADING,
                                weight=ft.FontWeight.W_900,
                                style=ft.TextStyle(letter_spacing=3),
                            ),
                            ft.Text(
                                "Every completed game, ranked. Yours included.",
                                color=t.SUBTEXT,
                                size=t.FONT_SMALL,
                                italic=True,
                            ),

                            # Table (scrollable, expands to fill remaining space)
                            ft.Container(
                                expand=True,
                                border=ft.border.all(1, t.BORDER),
                                border_radius=6,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                bgcolor=t.SURFACE,
                                content=ft.Column(
                                    expand=True,
                                    spacing=0,
                                    controls=[
                                        table_header,
                                        ft.Container(
                                            expand=True,
                                            content=table_body,
                                        ),
                                    ],
                                ),
                            ),

                            # Sticky buttons
                            ft.Row(
                                spacing=12,
                                controls=[
                                    _btn("PLAY AGAIN", on_play, primary=True),
                                    _btn("HOME", on_home, primary=False),
                                ],
                            ),
                            ft.Container(content=nav_error, height=20),
                        ],
                    ),
                ),
            ],
        ),
    )
