import os
from datetime import datetime
import pyxel
# from PIL import Image
# from js import window, Blob, URL, document
from js import Blob, URL, Uint8Array, document

import utils
# =========================================================
# Pyxel標準16色
# =========================================================

PYXEL_PALETTE = [
    0x000000,  # 0
    0x2B335F,  # 1
    0x7E2072,  # 2
    0x19959C,  # 3
    0x8B4852,  # 4
    0x395C98,  # 5
    0xA9C1FF,  # 6
    0xEEEEEE,  # 7
    0xD4186C,  # 8
    0xD38411,  # 9
    0xE9C35B,  # 10
    0x70C6A9,  # 11
    0x7696DE,  # 12
    0xA3A3A3,  # 13
    0xFF9798,  # 14
    0xEDCF80,  # 15
]


class EditorScreen:
    # =====================================================
    # 基本設定
    # =====================================================

    SCREEN_WIDTH = 256
    SCREEN_HEIGHT = 256

    # パターンそのもののサイズ
    PATTERN_SIZE_LIST = [8, 16, 32, 48]

    # 中央の入力枠の表示サイズ
    # パターンサイズとは別に変更できる
    FRAME_SIZE_LIST = [64, 96, 128, 160]

    # 中央入力枠の上端
    EDITOR_Y = 37

    # パレット
    PALETTE_CELL_SIZE = 14
    PALETTE_X = 16
    PALETTE_Y = 211

    # ツール
    TOOL_PEN = 0
    TOOL_FILL = 1
    TOOL_LINE = 2
    TOOL_CELL_SIZE = 14
    TOOL_X = 16
    TOOL_Y = 16

    def __init__(self, app):
        self.app = app
        # self.id = id
        # pyxel.init(
        #     self.SCREEN_WIDTH,
        #     self.SCREEN_HEIGHT,
        #     title="Pattern Maker",
        #     fps=30,
        # )

        pyxel.mouse(True)
        pyxel.load("assets/asset.pyxres")
        # キャンバス
        self.canvas = []
        # 一時的に表示する仮想的なキャンバス
        self.preview_canvas = []
        # 現在のパターンサイズ
        self.pattern_size = 16

        # 現在の入力枠サイズ
        self.frame_size = 128

        # 選択中の色
        self.selected_color = 8

        # プレビューモード
        self.preview_mode = False

        # 前回描画した論理座標
        self.previous_point = None
        # 開始倫理座標
        self.starting_point = None

        # 選択中のツール
        self.selected_tool = self.TOOL_PEN
        # self.selected_tool = self.TOOL_FILL

        # 初期キャンバス
        # 0番色、つまり黒で埋める
        self.create_canvas()
        self.create_preview_canvas()

        # pyxel.run(self.update, self.draw)

    # =====================================================
    # キャンバス
    # =====================================================

    def create_canvas(self):
        """
        キャンバスを黒で初期化する。
        """

        self.canvas = [
            [0 for _ in range(self.pattern_size)]
            for _ in range(self.pattern_size)
        ]

    def create_preview_canvas(self):
        """
        キャンバスをNoneで初期化する。
        プレビューはNoneが有効
        """

        self.preview_canvas = [
            [None for _ in range(self.pattern_size)]
            for _ in range(self.pattern_size)
        ]

    def clear_canvas(self):
        """
        キャンバスをすべて黒に戻す。
        """

        for y in range(self.pattern_size):
            for x in range(self.pattern_size):
                self.canvas[y][x] = 0

    def clear_preview_canvas(self):
        """
        プレビュー用キャンバスをすべてNoneに戻す。
        """

        for y in range(self.pattern_size):
            for x in range(self.pattern_size):
                self.preview_canvas[y][x] = None

    def change_pattern_size(self, new_size):
        """
        パターンサイズを変更する。

        サイズ変更時は、誤った座標変換を防ぐため
        キャンバスを黒で初期化する。
        """

        if new_size not in self.PATTERN_SIZE_LIST:
            return

        if new_size == self.pattern_size:
            return

        self.pattern_size = new_size
        self.previous_point = None
        self.create_canvas()
        self.create_preview_canvas()

    def change_frame_size(self, new_size):
        """
        中央の入力枠の表示サイズだけを変更する。
        パターンの論理サイズは変更しない。
        FRAME_SIZE_LIST = [64, 96, 128, 160]
        """

        # if new_size not in self.FRAME_SIZE_LIST:
        #     return
        if not (52 <= new_size < 200):
            return

        self.frame_size = new_size
        self.previous_point = None

    # =====================================================
    # 座標変換
    # =====================================================

    def editor_x(self):
        """
        中央入力枠の左端を返す。
        """

        return (
            self.SCREEN_WIDTH - self.frame_size
        ) // 2

    def editor_y(self):
        """
        中央入力枠の上端を返す。
        """

        return (
            self.SCREEN_HEIGHT - self.frame_size
        ) // 2

    def screen_to_canvas(self, screen_x, screen_y):
        """
        画面座標をキャンバスの論理座標へ変換する。
        """

        editor_x = self.editor_x()

        if not (
            editor_x <= screen_x < editor_x + self.frame_size
            and self.editor_y() <= screen_y < self.editor_y() + self.frame_size
        ):
            return None

        x = (
            (screen_x - editor_x)
            * self.pattern_size
            // self.frame_size
        )

        y = (
            (screen_y - self.editor_y())
            * self.pattern_size
            // self.frame_size
        )

        if 0 <= x < self.pattern_size and 0 <= y < self.pattern_size:
            return x, y

        return None

    # =====================================================
    # 更新処理
    # =====================================================

    def update(self):
        # ---------------------------------------------
        # プレビューモード
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_P):
            self.preview_mode = not self.preview_mode
            self.previous_point = None
            return

        if self.preview_mode:
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                self.preview_mode = False

            self.previous_point = None
            return

        # ---------------------------------------------
        # パターンサイズ変更
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_1):
            self.change_pattern_size(8)

        if pyxel.btnp(pyxel.KEY_2):
            self.change_pattern_size(16)

        if pyxel.btnp(pyxel.KEY_3):
            self.change_pattern_size(32)

        if pyxel.btnp(pyxel.KEY_4):
            self.change_pattern_size(48)

        # ---------------------------------------------
        # 入力枠サイズ変更
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_Q):
            self.change_frame_size(64)

        if pyxel.btnp(pyxel.KEY_W):
            self.change_frame_size(96)

        if pyxel.btnp(pyxel.KEY_E):
            self.change_frame_size(128)

        if pyxel.btnp(pyxel.KEY_R):
            self.change_frame_size(160)

        if pyxel.btnp(pyxel.KEY_UP, hold=15, repeat=1):
            self.change_frame_size(self.frame_size + 4)
        if pyxel.btnp(pyxel.KEY_DOWN, hold=15, repeat=1):
            self.change_frame_size(self.frame_size - 4)
        # ---------------------------------------------
        # 色変更
        # ---------------------------------------------

        if (
            not pyxel.btn(pyxel.KEY_ALT)
            and pyxel.btnp(pyxel.KEY_LEFT)
        ):
            self.selected_color = (
                self.selected_color - 1
            ) % 16

        if (
            not pyxel.btn(pyxel.KEY_ALT)
            and pyxel.btnp(pyxel.KEY_RIGHT)
        ):
            self.selected_color = (
                self.selected_color + 1
            ) % 16

        # ---------------------------------------------
        # ツール変更
        # ---------------------------------------------

        if (
            pyxel.btn(pyxel.KEY_ALT)
            and pyxel.btnp(pyxel.KEY_LEFT)
        ):
            self.selected_tool = (
                self.selected_tool - 1
            ) % 2

        if (
            pyxel.btn(pyxel.KEY_ALT)
            and pyxel.btnp(pyxel.KEY_RIGHT)
        ):
            self.selected_tool = (
                self.selected_tool + 1
            ) % 2

        # ---------------------------------------------
        # パレットクリック
        # ---------------------------------------------

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            palette_color = self.get_palette_color(
                pyxel.mouse_x,
                pyxel.mouse_y,
            )

            if palette_color is not None:
                self.selected_color = palette_color
                self.previous_point = None
                return

        # ---------------------------------------------
        # ツールクリック
        # ---------------------------------------------

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            tool = self.get_select_tool(
                pyxel.mouse_x,
                pyxel.mouse_y,
            )

            if tool is not None:
                self.selected_tool = tool
                self.previous_point = None
                return

        # ---------------------------------------------
        # 左クリックで描画
        # ---------------------------------------------

        current_point = self.screen_to_canvas(
            pyxel.mouse_x,
            pyxel.mouse_y,
        )

        if current_point is not None:
            # ----------
            # ペンツール
            # ----------
            if self.selected_tool == self.TOOL_PEN:
                if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                    if self.previous_point is None:
                        self.paint_point(
                            current_point[0],
                            current_point[1],
                            self.selected_color,
                        )
                    else:
                        self.paint_line(
                            self.previous_point,
                            current_point,
                            self.selected_color,
                        )

                    self.previous_point = current_point
                else:
                    self.previous_point = None
                
            # ----------
            # 塗りつぶしツール
            # ----------
            elif self.selected_tool == self.TOOL_FILL:
                if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                    start_x, start_y = current_point[0], current_point[1]

                    # クリックしたセルの元の色
                    target_color = self.canvas[start_y][start_x]

                    # すでに選択色なら何もしない
                    if target_color != self.selected_color:
                        fill_cells = [(start_x, start_y)]
                        visited = set()

                        directions = [
                            (0, -1),  # 上
                            (-1, 0),  # 左
                            (1, 0),   # 右
                            (0, 1),   # 下
                        ]

                        while fill_cells:
                            x, y = fill_cells.pop(0)

                            # 同じセルを二重処理しない
                            if (x, y) in visited:
                                continue

                            # 枠外ならスキップ
                            if not (
                                0 <= x < self.pattern_size
                                and 0 <= y < self.pattern_size
                            ):
                                continue

                            # 元の色ではないセルには到達しない
                            if self.canvas[y][x] != target_color:
                                continue

                            visited.add((x, y))

                            # セルを塗る
                            self.paint_point(
                                x,
                                y,
                                self.selected_color,
                            )

                            # 上下左右を追加
                            for dx, dy in directions:
                                next_x = x + dx
                                next_y = y + dy

                                if (next_x, next_y) not in visited:
                                    fill_cells.append((next_x, next_y))

            # ----------
            # 線ツール
            # ----------
            elif self.selected_tool == self.TOOL_LINE:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.starting_point = current_point
                if self.starting_point is not None:
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                        self.paint_line(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                        )
                        self.starting_point = None
                        self.clear_preview_canvas()
                    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                        self.paint_line(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                            preview=True
                        )

        # if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            # current_point = self.screen_to_canvas(
            #     pyxel.mouse_x,
            #     pyxel.mouse_y,
            # )

            # if current_point is not None:


        # ---------------------------------------------
        # 右クリックまたはXキーで黒に戻す
        # ---------------------------------------------

        elif (
            pyxel.btn(pyxel.MOUSE_BUTTON_RIGHT)
            or pyxel.btn(pyxel.KEY_X)
        ):
            current_point = self.screen_to_canvas(
                pyxel.mouse_x,
                pyxel.mouse_y,
            )

            if current_point is not None:
                if self.previous_point is None:
                    self.paint_point(
                        current_point[0],
                        current_point[1],
                        0,
                    )
                else:
                    self.paint_line(
                        self.previous_point,
                        current_point,
                        0,
                    )

                self.previous_point = current_point

        else:
            self.previous_point = None

        # ---------------------------------------------
        # 全消去
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_C):
            self.clear_canvas()
            self.clear_preview_canvas()

        # ---------------------------------------------
        # ファイル出力
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_S):
            self.export_png()
            self.export_text()

    # =====================================================
    # 描画データ変更
    # =====================================================

    def paint_point(self, x, y, color, preview=False):
        """
        指定した1ドットだけを変更する。

        重要:
        キャンバス端に描いても反対側には描画しない。
        """

        if not (
            0 <= x < self.pattern_size
            and 0 <= y < self.pattern_size
        ):
            return

        if not preview:
            self.canvas[y][x] = color
        else:
            self.preview_canvas[y][x] = color

    def paint_line(self, start, end, color, preview=False):
        """
        直線を引く
        前回位置と現在位置の間を補間して描画する。
        マウスを速く動かしたときに、途中のドットが
        抜けるのを防ぐのにも有効
        """
        # プレビューの場合はキャンバスを初期化
        if preview:
            self.clear_preview_canvas()

        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        distance = max(abs(dx), abs(dy))

        if distance == 0:
            self.paint_point(x1, y1, color, preview)
            return

        for i in range(distance + 1):
            x = round(
                x1 + dx * i / distance
            )

            y = round(
                y1 + dy * i / distance
            )

            self.paint_point(x, y, color, preview)

    # =====================================================
    # 描画
    # =====================================================

    def draw(self):
        pyxel.cls(0)

        if self.preview_mode:
            self.draw_preview()
        else:
            self.draw_pattern()
            self.draw_preview_pattern()
            self.draw_palette()
            self.draw_tools()
            # self.draw_header()
            self.draw_footer()
        # pyxel.text(0, 0, f"{self.preview_canvas}", 7)

    def draw_text_shadow(self, x, y, text, color=7):
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

    def draw_header(self):
        self.draw_text_shadow(
            8,
            7,
            "PYXEL PATTERN EDITOR",
            7,
        )

        self.draw_text_shadow(
            8,
            18,
            f"PATTERN: {self.pattern_size} x {self.pattern_size}",
            10,
        )

        self.draw_text_shadow(
            145,
            18,
            f"FRAME: {self.frame_size}",
            7,
        )

    def draw_pattern(self):
        """
        中央の入力枠と、その周囲の繰り返しパターンを描画する。
        """

        editor_x = self.editor_x()
        editor_y = self.editor_y()

        # 周囲を5×5で描画
        for tile_y in range(-2, 3):
            for tile_x in range(-2, 3):
                left = editor_x + (
                    tile_x * self.frame_size
                )

                top = editor_y + (
                    tile_y * self.frame_size
                )

                self.draw_tile(left, top)

        # 中央の入力枠を強調
        pyxel.rectb(
            editor_x - 1,
            editor_y - 1,
            self.frame_size + 2,
            self.frame_size + 2,
            7,
        )

    def draw_preview_pattern(self):
        """
        パターンの入力中のプレビュー部分を描画する。
        """

        editor_x = self.editor_x()
        editor_y = self.editor_y()

        self.draw_tile(editor_x, editor_y, preview=True)
        # 周囲を5×5で描画
        # for tile_y in range(-2, 3):
        #     for tile_x in range(-2, 3):
        #         left = editor_x + (
        #             tile_x * self.frame_size
        #         )

        #         top = self.editor_y() + (
        #             tile_y * self.frame_size
        #         )

        #         self.draw_tile(left, top)

        # 中央の入力枠を強調
        # pyxel.rectb(
        #     editor_x - 1,
        #     self.editor_y() - 1,
        #     self.frame_size + 2,
        #     self.frame_size + 2,
        #     7,
        # )

    def draw_tile(self, tile_x, tile_y, preview=False):
        """
        1枚分のパターンを描画する。
        """

        if not preview:
            canvas = self.canvas
        else:
            canvas = self.preview_canvas
        for y in range(self.pattern_size):
            for x in range(self.pattern_size):
                if canvas[y][x] is None:
                    continue
                color = canvas[y][x]

                left = tile_x + (
                    x * self.frame_size
                    // self.pattern_size
                )

                top = tile_y + (
                    y * self.frame_size
                    // self.pattern_size
                )

                right = tile_x + (
                    (x + 1) * self.frame_size
                    // self.pattern_size
                ) - 1

                bottom = tile_y + (
                    (y + 1) * self.frame_size
                    // self.pattern_size
                ) - 1

                width = right - left + 1
                height = bottom - top + 1

                if width > 0 and height > 0:
                    pyxel.rect(
                        left,
                        top,
                        width,
                        height,
                        color,
                    )

        # タイルの枠
        pyxel.rectb(
            tile_x,
            tile_y,
            self.frame_size,
            self.frame_size,
            13,
        )

    def draw_palette(self):
        """
        16色パレットを表示する。
        """

        for color in range(16):
            x = (
                self.PALETTE_X
                + color * self.PALETTE_CELL_SIZE
            )

            pyxel.rect(
                x,
                self.PALETTE_Y,
                self.PALETTE_CELL_SIZE - 2,
                self.PALETTE_CELL_SIZE - 2,
                color,
            )

            # 選択中の色
            if color == self.selected_color:
                pyxel.rectb(
                    x - 1,
                    self.PALETTE_Y - 1,
                    self.PALETTE_CELL_SIZE,
                    self.PALETTE_CELL_SIZE,
                    7 if pyxel.frame_count // 20 % 2 == 0 else 10,
                )

        # パレットサイズ表示
        self.draw_text_shadow(
            8,
            202,
            "PALETTE: 16 COLORS",
            7,
        )

    def draw_tools(self):
        """
        ツールを表示する。
        """

        for tool in range(3):
            x = (
                self.TOOL_X
                + tool * self.TOOL_CELL_SIZE
            )
            pyxel.pal(5, 0)
            pyxel.blt(
                x+1,
                self.TOOL_Y+1,
                0,
                tool * 16,
                0,
                self.TOOL_CELL_SIZE-2,
                self.TOOL_CELL_SIZE-2,
                10
            )
            pyxel.pal()
            if tool == self.selected_tool:
                pyxel.pal(5, 7)
            pyxel.blt(
                x,
                self.TOOL_Y,
                0,
                tool * 16,
                0,
                self.TOOL_CELL_SIZE-2,
                self.TOOL_CELL_SIZE-2,
                10
            )
            pyxel.pal()

        self.draw_text_shadow(
            self.TOOL_X,
            self.TOOL_Y-7,
            "TOOLS",
            7,
        )

    def draw_footer(self):
        self.draw_text_shadow(
            8,
            229,
            "1-4: PATTERN SIZE",
            7,
        )

        self.draw_text_shadow(
            8,
            239,
            "Q-R: FRAME SIZE",
            7,
        )

        self.draw_text_shadow(
            8,
            249,
            "P: PREVIEW  S: SAVE",
            7,
        )

    # =====================================================
    # プレビューモード
    # =====================================================

    def draw_preview(self):
        """
        パターンを等倍で画面全体に繰り返し表示する。
        キャンバスの1ドットを、画面上の1ピクセルとして描画する。
        """

        # 等倍表示
        scale = 1
        tile_size = self.pattern_size

        # 画面全体を覆うため、左右・上下に余分に描画する
        tile_count_x = (
            self.SCREEN_WIDTH // tile_size
        ) + 2

        tile_count_y = (
            self.SCREEN_HEIGHT // tile_size
        ) + 2

        for tile_y in range(-1, tile_count_y):
            for tile_x in range(-1, tile_count_x):
                tile_left = tile_x * tile_size
                tile_top = tile_y * tile_size

                for y in range(self.pattern_size):
                    for x in range(self.pattern_size):
                        color = self.canvas[y][x]

                        pyxel.pset(
                            tile_left + x,
                            tile_top + y,
                            color,
                        )

        # 操作説明を表示する場合
        self.draw_text_shadow(
            8,
            8,
            f"PREVIEW: {self.pattern_size} x {self.pattern_size}",
            7,
        )

        self.draw_text_shadow(
            8,
            19,
            "P / ESC: BACK",
            7,
        )

    # =====================================================
    # パレット
    # =====================================================

    def get_palette_color(self, mouse_x, mouse_y):
        """
        クリックされたパレット色を返す。
        パレット外ならNoneを返す。
        """

        palette_width = (
            self.PALETTE_CELL_SIZE * 16
        )

        if not (
            self.PALETTE_X <= mouse_x
            < self.PALETTE_X + palette_width
            and self.PALETTE_Y <= mouse_y
            < self.PALETTE_Y + self.PALETTE_CELL_SIZE
        ):
            return None

        color = (
            mouse_x - self.PALETTE_X
        ) // self.PALETTE_CELL_SIZE

        if 0 <= color < 16:
            return color

        return None

    # =====================================================
    # ツール
    # =====================================================

    def get_select_tool(self, mouse_x, mouse_y):
        """
        クリックされたツールを返す。
        ツール外ならNoneを返す。
        """

        tool_width = (
            self.TOOL_CELL_SIZE * 3
        )

        if not (
            self.TOOL_X <= mouse_x
            < self.TOOL_X + tool_width
            and self.TOOL_Y <= mouse_y
            < self.TOOL_Y + self.TOOL_CELL_SIZE
        ):
            return None

        tool = (
            mouse_x - self.TOOL_X
        ) // self.TOOL_CELL_SIZE

        if 0 <= tool < 3:
            return tool

        return None

    # =====================================================
    # PNG出力
    # =====================================================

    def export_png(self):
        """
        パターンをPNGで出力する。
        背景は透明ではなく、すべてRGB形式で出力する。
        """

        output_size = self.pattern_size

        p_image = pyxel.Image(output_size, output_size)

        for y in range(self.pattern_size):
            for x in range(self.pattern_size):
                color_index = self.canvas[y][x]
                rgb = PYXEL_PALETTE[color_index]

                red = (rgb >> 16) & 0xFF
                green = (rgb >> 8) & 0xFF
                blue = rgb & 0xFF

                p_image.set(x, y, [str(color_index)])

        # filename = (
        #     f"pattern_{self.pattern_size}x"
        #     f"{self.pattern_size}_3x3.png"
        # )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pattern_{timestamp}.png"
        self.download_image(p_image, filename)
        print(f"PNG saved: {filename}")

    # =====================================================
    # テキスト出力
    # =====================================================

    def export_text(self):
        """
        PyxelのImage.set()で利用できる形式で出力する。
        """

        filename = (
            f"pattern_{self.pattern_size}x"
            f"{self.pattern_size}.txt"
        )

        output = "pyxel.image(0).set(0, 0, [\n"

        for y in range(self.pattern_size):
            row = ""

            for x in range(self.pattern_size):
                color = self.canvas[y][x]
                row += format(color, "x")

            comma = "," if y < self.pattern_size - 1 else ""
            output += f'    "{row}"{comma}\n'

        output += "])\n"

        # ファイルに書き込む
        with open(filename, "w", encoding="utf-8") as file:
            file.write(output)

        # 書き込んだ内容を画面に表示
        print(output)

        # print(f"Text saved: {filename}")

    def download_image(self, image, filename):
        path = "/tmp/download.png"

        image.save(path, 1)

        with open(path, "rb") as file:
            data = file.read()

        blob = Blob.new(
            [Uint8Array.new(data)],
            {"type": "image/png"},
        )

        url = URL.createObjectURL(blob)

        link = document.createElement("a")
        link.href = url
        link.download = filename

        document.body.appendChild(link)
        link.click()
        link.remove()

        URL.revokeObjectURL(url)
        os.remove(path)


# if __name__ == "__main__":
#     PatternEditor()
