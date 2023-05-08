import ipyvuetify as v
from . import View

class SettingButton(View):
    def __init__(self) -> None:
        super().__init__()

        self.ui = v.Btn(children=[
            v.Icon(left=True, children=["mdi-wrench"]),
            "Settings"
        ])


class StartButton(View):
    def __init__(self) -> None:
        super().__init__()

        self.ui = v.Btn(children=[
            v.Icon(left=True, children=["mdi-play"]),
            "Begin"
        ], color='success')


class Buttons(View):
    def __init__(self) -> None:
        super().__init__()

        self.start_button = StartButton()
        self.setting_button = SettingButton()
        self.ui = v.Row(justify='start', children=[
                v.Col(children=[self.start_button.ui]),
                v.Col(children=[self.setting_button.ui])
            ])


class ProxyView(View):
    def __init__(self) -> None:
        super().__init__()

        self.ui = v.DataTable(
            headers=[
                {'text': 'Host', 'value': 'host'},
                {'text': 'Path', 'value': 'path'},
                {'text': 'Method', 'value': 'method'},
                {'text': 'Status', 'value': 'status'},
                {'text': 'Size', 'value': 'size'},
                {'text': 'Time', 'value': 'time'}
            ],
            items=[],
            items_per_page=-1
        )


class Mitm(View):
    def __init__(self) -> None:
        super().__init__()

        self.buttons = Buttons()
        self.proxy_view = ProxyView()

        self.ui = v.Container(children=[
            v.Row(children=[self.buttons.ui]),
            v.Row(children=[self.proxy_view.ui])
        ])