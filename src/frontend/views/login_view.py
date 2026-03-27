import flet as ft

from frontend import theme as t


def login_view(page: ft.Page, state, client, navigate) -> ft.Container:
    error_msg = ft.Text("", color=t.DANGER, size=t.FONT_SMALL)

    username_field = ft.TextField(
        hint_text="username",
        border_color=t.BORDER,
        focused_border_color=t.ACCENT,
        color=t.TEXT,
        hint_style=ft.TextStyle(color=t.SUBTEXT),
        bgcolor=t.INPUT_BG,
        border_radius=2,
        height=48,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        cursor_color=t.ACCENT,
    )

    password_field = ft.TextField(
        hint_text="password",
        password=True,
        can_reveal_password=True,
        border_color=t.BORDER,
        focused_border_color=t.ACCENT,
        color=t.TEXT,
        hint_style=ft.TextStyle(color=t.SUBTEXT),
        bgcolor=t.INPUT_BG,
        border_radius=2,
        height=48,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        cursor_color=t.ACCENT,
    )

    def set_error(msg: str) -> None:
        error_msg.value = msg
        page.update()

    def handle_auth(action: str) -> None:
        set_error("")
        username = username_field.value.strip() if username_field.value else ""
        password = password_field.value or ""

        if not username or not password:
            set_error("Both fields are required.")
            return

        try:
            data = client.register(username, password) if action == "register" else client.login(username, password)
            state.token = data["access_token"]
            state.username = username
            client.set_token(state.token)
            navigate("/home")
        except ValueError as e:
            set_error(str(e))

    def on_login(e) -> None:
        handle_auth("login")

    def on_register(e) -> None:
        handle_auth("register")

    def on_submit(e: ft.KeyboardEvent) -> None:
        if e.key == "Enter":
            handle_auth("login")

    page.on_keyboard_event = on_submit

    return ft.Container(
        expand=True,
        bgcolor=t.BG,
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                # Title
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
                    "Identify the culprit. Before they do.",
                    size=t.FONT_SMALL,
                    color=t.SUBTEXT,
                    italic=True,
                    style=ft.TextStyle(letter_spacing=1),
                ),
                ft.Container(height=52),

                # Form card
                ft.Container(
                    width=360,
                    bgcolor=t.SURFACE,
                    border_radius=4,
                    border=ft.border.all(1, t.BORDER),
                    padding=ft.padding.all(32),
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            ft.Text(
                                "SIGN IN",
                                size=t.FONT_SMALL,
                                color=t.SUBTEXT,
                                weight=ft.FontWeight.W_600,
                                style=ft.TextStyle(letter_spacing=3),
                            ),
                            ft.Container(height=20),
                            username_field,
                            ft.Container(height=10),
                            password_field,
                            ft.Container(height=24),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    _btn("LOGIN", on_login, primary=True),
                                    _btn("REGISTER", on_register, primary=False),
                                ],
                            ),
                            ft.Container(height=16),
                            ft.Container(
                                content=error_msg,
                                height=20,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )


def _btn(label: str, on_click, primary: bool) -> ft.Container:
    return ft.Container(
        expand=True,
        content=ft.Text(
            label,
            color=t.TEXT,
            size=t.FONT_SMALL,
            weight=ft.FontWeight.W_700,
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(letter_spacing=t.LETTER_SPACING_BTN),
        ),
        bgcolor=t.ACCENT if primary else "transparent",
        border=ft.border.all(1, t.ACCENT if primary else t.BORDER),
        border_radius=2,
        padding=ft.padding.symmetric(vertical=13),
        on_click=on_click,
        ink=True,
    )
