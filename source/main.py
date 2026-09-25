import pyxel
from screens import TitleScreen, ListScreen, EditorScreen


class PatternMaker:

    SCREEN_WIDTH = 256
    SCREEN_HEIGHT = 256

    SCREEN_TITLE = 0
    SCREEN_LIST = 1
    SCREEN_EDITOR = 2
    SCREEN_SETTING = 3

    def __init__(self):
        pyxel.init(
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            title="Pattern Maker",
            fps=30,
        )
        pyxel.mouse(True)
        pyxel.load("assets/asset.pyxres")

        self.screens = {
            self.SCREEN_TITLE: TitleScreen(self),
            self.SCREEN_LIST: ListScreen(self),
            self.SCREEN_EDITOR: EditorScreen(self)
        }
        self.current_screen = self.SCREEN_TITLE

        pyxel.run(self.update, self.draw)

    def change_screen(self, screen):
        self.current_screen = screen

    def update(self):
        self.screens[self.current_screen].update()

    def draw(self):
        pyxel.cls(0)
        self.screens[self.current_screen].draw()



PatternMaker()