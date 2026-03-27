import threading
import time

import flet as ft

from frontend import theme as t

# Softer feedback colors — less harsh than full accent/success
_COLOR_CORRECT = "#1a4a1a"
_COLOR_WRONG = "#4a1a1a"


def game_view(page: ft.Page, state, client, navigate) -> ft.Container:
    if not state.current_round or not state.session_id:
        navigate("/home")
        return ft.Container()

    cards_locked = [False]

    # --- Live controls ---
    round_label = ft.Text(
        "",
        color=t.SUBTEXT,
        size=t.FONT_SMALL,
        weight=ft.FontWeight.W_600,
        style=ft.TextStyle(letter_spacing=2),
    )
    score_label = ft.Text(
        "",
        color=t.TEXT,
        size=t.FONT_SMALL,
        weight=ft.FontWeight.W_600,
        style=ft.TextStyle(letter_spacing=2),
    )
    quote_text = ft.Text(
        "",
        color=t.TEXT,
        size=18,
        italic=True,
        text_align=ft.TextAlign.CENTER,
    )
    feedback_icon = ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="white", size=20)
    feedback_label = ft.Text("", color="white", size=t.FONT_BODY, weight=ft.FontWeight.W_700)
    feedback_sublabel = ft.Text("", color="white", size=t.FONT_SMALL)
    feedback_hint = ft.Text(
        "click to continue  →",
        color="white",
        size=10,
        opacity=0.5,
    )

    feedback_banner = ft.Container(
        visible=False,
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=28, vertical=14),
        ink=True,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            tight=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        feedback_icon,
                        ft.Column(
                            spacing=2,
                            tight=True,
                            controls=[feedback_label, feedback_sublabel],
                        ),
                    ],
                ),
                feedback_hint,
            ],
        ),
    )

    feedback_row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[feedback_banner],
    )

    cards_row = ft.Row(spacing=16, controls=[])

    # --- Card builder ---
    def make_card(option: dict) -> ft.Container:
        pid = option["person_id"]
        return ft.Container(
            expand=True,
            bgcolor=t.SURFACE,
            border=ft.border.all(1, t.BORDER),
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ink=True,
            on_click=lambda e, person_id=pid: on_answer(person_id),
            content=ft.Column(
                spacing=0,
                controls=[
                    # DecorationImage fills the Container's own rendered dimensions
                    # (not the child's), so COVER always fills the full card width.
                    # Container with height set fills parent Column's bounded width.
                    ft.Container(
                        height=320,
                        bgcolor=t.INPUT_BG,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        image=ft.DecorationImage(
                            src=option["image_url"],
                            fit=ft.BoxFit.COVER,
                        ),
                    ),
                    ft.Container(
                        padding=ft.padding.all(16),
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    option["name"],
                                    color=t.TEXT,
                                    size=t.FONT_BODY,
                                    weight=ft.FontWeight.W_700,
                                ),
                                ft.Text(
                                    option["short_bio"],
                                    color=t.SUBTEXT,
                                    size=t.FONT_SMALL,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    # --- Load a round ---
    def load_round(round_data: dict) -> None:
        round_label.value = f"ROUND  {round_data['round_number']} / 5"
        score_label.value = f"SCORE  {state.score}"
        quote_text.value = f'"{round_data["quote_text"]}"'
        opts = round_data["options"]
        cards_row.controls = [make_card(opts[0]), make_card(opts[1])]
        feedback_banner.visible = False
        cards_locked[0] = False

    # --- Answer handler ---
    def on_answer(person_id: int) -> None:
        if cards_locked[0]:
            return
        cards_locked[0] = True

        try:
            result = client.submit_answer(state.session_id, person_id)
        except ValueError as ex:
            feedback_banner.bgcolor = _COLOR_WRONG
            feedback_icon.name = ft.Icons.ERROR_OUTLINE
            feedback_label.value = "Error"
            feedback_sublabel.value = str(ex)
            feedback_hint.value = "click to dismiss"
            feedback_banner.visible = True
            cards_locked[0] = False
            page.update()
            return

        state.score = result["current_score"]
        score_label.value = f"SCORE  {state.score}"
        correct_name = result["correct_person"]["name"]

        if result["is_correct"]:
            feedback_banner.bgcolor = _COLOR_CORRECT
            feedback_icon.name = ft.Icons.CHECK_CIRCLE_OUTLINE
            feedback_label.value = "CORRECT"
            feedback_sublabel.value = f"It was {correct_name}. Obviously."
        else:
            feedback_banner.bgcolor = _COLOR_WRONG
            feedback_icon.name = ft.Icons.CANCEL_OUTLINED
            feedback_label.value = "WRONG"
            feedback_sublabel.value = f"It was {correct_name}. Do better."

        feedback_hint.value = "click to continue  →"
        feedback_banner.visible = True

        advance_done = [False]

        def do_advance() -> None:
            if advance_done[0]:
                return
            advance_done[0] = True
            if result["game_over"]:
                navigate("/result")
            else:
                state.current_round = result["next_round"]
                load_round(result["next_round"])
                page.update()

        feedback_banner.on_click = lambda e: do_advance()
        page.update()

        def auto_advance() -> None:
            time.sleep(1.5)
            do_advance()

        threading.Thread(target=auto_advance, daemon=True).start()

    load_round(state.current_round)

    return ft.Container(
        expand=True,
        bgcolor=t.BG,
        content=ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=700,
                    padding=ft.padding.symmetric(vertical=28),
                    content=ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
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
                                    ft.Row(spacing=24, controls=[round_label, score_label]),
                                ],
                            ),
                            ft.Container(height=1, bgcolor=t.BORDER),

                            # Quote card — alignment forces full 700px width regardless of text length
                            ft.Container(
                                alignment=ft.Alignment(0, 0),
                                bgcolor=t.SURFACE,
                                border=ft.border.all(1, t.BORDER),
                                border_radius=8,
                                padding=ft.padding.symmetric(horizontal=36, vertical=28),
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=14,
                                    controls=[
                                        ft.Icon(ft.Icons.FORMAT_QUOTE, color=t.ACCENT, size=26),
                                        quote_text,
                                    ],
                                ),
                            ),

                            # Person cards — two equal-width columns
                            cards_row,

                            # Feedback banner — compact, centered
                            feedback_row,
                        ],
                    ),
                ),
            ],
        ),
    )
