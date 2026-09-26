import pyxel


def draw_text_shadow(x, y, text, color=7):
    """
    文字の右下に黒い影を付ける。
    """

    pyxel.text(
        x + 1,
        y + 1,
        text,
        0,
    )

    pyxel.text(
        x,
        y,
        text,
        color,
    )
