import pyxel

PTN_SIZE = 16
PTN_KATAKUSA = (0, 32)
PTN_UROKO = (16, 32)
PTN_ICHIMATSU = (32, 32)
PTN_KAGOME = (48, 32)
PTN_KAMADO = (0, 48)
PTN_KOUSHI = (16, 48)
PTN_KUSAKI = (32, 48)

PATTERNS = [
    PTN_KATAKUSA,
    PTN_UROKO,
    PTN_ICHIMATSU,
    PTN_KAGOME,
    PTN_KAMADO,
    PTN_KOUSHI,
    PTN_KUSAKI
]

class TitleScreen:
    def __init__(self, app):
        self.app = app

    def update(self):
        app = self.app
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            app.change_screen(app.SCREEN_LIST)
    
    def draw(self):
        pyxel.cls(0)

        
        for i in range((pyxel.width // PTN_SIZE) + 1):
            for j in range((pyxel.height // PTN_SIZE) + 1):
                pyxel.blt(
                    i * PTN_SIZE,
                    j * PTN_SIZE,
                    0,
                    PATTERNS[(pyxel.frame_count // 90) % 7][0],
                    PATTERNS[(pyxel.frame_count // 90) % 7][1],
                    PTN_SIZE,
                    PTN_SIZE
                )
        # --------------------
        # タイトル
        # --------------------
        w, h, = 200, 120
        pyxel.rect(
            (pyxel.width // 2) - (w // 2),
            30,
            w,
            h,
            3
        )
        # --------------------
        # 文字
        # --------------------
        msg = "PATTERN MAKER"
        pyxel.text(
            (pyxel.width // 2) - (len(msg)*pyxel.FONT_WIDTH // 2),
            90,
            msg,
            7
        )
        pyxel.text(0, 0, "TITLE", 7)