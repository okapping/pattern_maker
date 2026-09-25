import pyxel


class ListScreen:
    def __init__(self, app):
        self.app = app

    def update(self):
        app = self.app
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            app.change_screen(app.SCREEN_EDITOR)
    
    def draw(self):
        pyxel.cls(0)
        pyxel.text(0, 0, "List", 7)