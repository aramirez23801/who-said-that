import flet as ft

from frontend import theme as t

_SCORE_LINES = {
    0: "Impressive. Somehow even worse than random.",
    1: "1 out of 5. You're consistent, at least.",
    2: "2 out of 5. A solid foundation of ignorance.",
    3: "3 out of 5. Mediocrity, achieved.",
    4: "4 out of 5. So close. Must sting.",
    5: "5 out of 5. Either you cheated or you need a life.",
}


def result_view(page: ft.Page, state, client, navigate) -> ft.Container:
    if not state.session_id:
        navigate("/home")
        return ft.Container()

    try:
        data = client.get_result(state.session_id)
    except ValueError:
        data = None

    score = data.get("score", state.score) if data else state.score
    total = data.get("total_rounds", 5) if data else 5

    # --- Score card (centered, fixed width) ---
    score_card = ft.Container(
        width=300,
        bgcolor=t.SURFACE,
        border=ft.border.all(1, t.BORDER),
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=40, vertical=32),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Text(
                    "FINAL SCORE",
                    color=t.SUBTEXT,
                    size=t.FONT_SMALL,
                    weight=ft.FontWeight.W_600,
                    style=ft.TextStyle(letter_spacing=3),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    f"{score} / {total}",
                    color=t.TEXT,
                    size=52,
                    weight=ft.FontWeight.W_900,
                    style=ft.TextStyle(letter_spacing=4),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    _SCORE_LINES.get(score, "Results inconclusive."),
                    color=t.SUBTEXT,
                    size=t.FONT_SMALL,
                    italic=True,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    # --- Round summary rows ---
    def make_round_row(rd: dict, index: int) -> ft.Container:
        is_correct = rd.get("is_correct")
        correct_name = rd.get("correct_person_name", "?")
        user_answer_name = rd.get("user_answer_name") or "—"
        quote = rd.get("quote_text", "")
        quote_short = f'"{quote[:68]}…"' if len(quote) > 68 else f'"{quote}"'

        icon_name = ft.Icons.CHECK_CIRCLE_OUTLINE if is_correct else ft.Icons.CANCEL_OUTLINED
        icon_color = t.SUCCESS if is_correct else t.DANGER

        return ft.Container(
            bgcolor=t.SURFACE,
            border=ft.border.all(1, t.BORDER),
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            content=ft.Row(
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=8,
                        tight=True,
                        controls=[
                            ft.Icon(icon_name, color=icon_color, size=18),
                            ft.Text(
                                str(index + 1),
                                color=t.SUBTEXT,
                                size=t.FONT_SMALL,
                                weight=ft.FontWeight.W_600,
                            ),
                        ],
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            quote_short,
                            color=t.TEXT,
                            size=t.FONT_SMALL,
                            italic=True,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                    ft.Column(
                        spacing=2,
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text(
                                correct_name,
                                color=t.TEXT,
                                size=t.FONT_SMALL,
                                weight=ft.FontWeight.W_700,
                                text_align=ft.TextAlign.RIGHT,
                            ),
                            ft.Text(
                                f"You said: {user_answer_name}" if not is_correct else "You got it.",
                                color=t.SUBTEXT,
                                size=t.FONT_SMALL,
                                text_align=ft.TextAlign.RIGHT,
                            ),
                        ],
                    ),
                ],
            ),
        )

    rounds = data.get("rounds", []) if data else []
    round_rows = [make_round_row(rd, i) for i, rd in enumerate(rounds)]

    summary_section = (
        ft.Column(spacing=8, controls=round_rows)
        if round_rows
        else ft.Text(
            "Round details unavailable.",
            color=t.SUBTEXT,
            size=t.FONT_SMALL,
            italic=True,
        )
    )

    # --- Action buttons ---
    def on_play_again(e) -> None:
        state.clear_session()
        try:
            game_data = client.start_game()
            state.session_id = game_data["session_id"]
            state.current_round = game_data["round"]
            state.score = 0
            navigate("/game")
        except ValueError as ex:
            error_text.value = str(ex)
            page.update()

    def on_leaderboard(e) -> None:
        navigate("/leaderboard")

    def on_home(e) -> None:
        state.clear_session()
        navigate("/home")

    error_text = ft.Text("", color=t.DANGER, size=t.FONT_SMALL)

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
                                        "GAME OVER",
                                        color=t.SUBTEXT,
                                        size=t.FONT_SMALL,
                                        weight=ft.FontWeight.W_600,
                                        style=ft.TextStyle(letter_spacing=2),
                                    ),
                                ],
                            ),
                            ft.Container(height=1, bgcolor=t.BORDER),

                            # Scrollable section: score card + round breakdown
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    spacing=20,
                                    controls=[
                                        ft.Container(height=8),

                                        # Score card — centered, fixed width
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            controls=[score_card],
                                        ),

                                        ft.Container(height=4),

                                        ft.Text(
                                            "ROUND BREAKDOWN",
                                            color=t.SUBTEXT,
                                            size=t.FONT_SMALL,
                                            weight=ft.FontWeight.W_600,
                                            style=ft.TextStyle(letter_spacing=2),
                                        ),

                                        summary_section,

                                        ft.Container(height=8),
                                    ],
                                ),
                            ),

                            # Sticky buttons at bottom
                            ft.Row(
                                spacing=12,
                                controls=[
                                    _btn("PLAY AGAIN", on_play_again, primary=True),
                                    _btn("LEADERBOARD", on_leaderboard, primary=False),
                                    _btn("HOME", on_home, primary=False),
                                ],
                            ),
                            ft.Container(content=error_text, height=20),
                        ],
                    ),
                ),
            ],
        ),
    )
