import pyxel
import json

from js import window

from .editor import EditorScreen
""" sample data
data_list = [
    {
        "id": 12345,
        "name": "hogehoge",
        "canvas": []
    },
    {
        "id": 67890,
        "name": "fugafuga",
        "canvas": [
            [0, 1, 2],
            [3, 4, 5]
        ]
    }
]
"""

class ListScreen:
    def __init__(self, app):
        self.app = app
        self.canvases = None

    def save_game(self, score):
        window.localStorage.setItem("score", str(score))

    def load_game(self):
        value = window.localStorage.getItem("score")
        return int(value) if value is not None else 0

    def update(self):
        app = self.app
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            app.screens[app.SCREEN_EDITOR] = EditorScreen(app)
            app.change_screen(app.SCREEN_EDITOR)
    
    def draw(self):
        pyxel.cls(0)
        pyxel.text(0, 0, "List", 7)