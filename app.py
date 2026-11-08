# -*- coding: utf-8 -*-
"""
职业测评 APP（Kivy + KivyMD）
视觉风格：薄荷白背景 + 白色大圆角卡片 + 墨绿主色 + 细描边
参考：B 站 SBTI 玩具的浅色极简风格
"""

import json
import os
import time
import traceback

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

# ---------------------------------------------------------------
# 基础设置
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "data.json"), encoding="utf-8") as f:
    DATA = json.load(f)

ORDER = DATA["order"]
TYPES = DATA["types"]
PARTS = DATA["parts"]
ABILITY = DATA["ability"]
SKILL = DATA["skill"]
MBTI_ITEMS = DATA["mbti_items"]
MBTI_TYPES = DATA["mbti_types"]
DIMENSIONS = DATA["dimensions"]
DIM_NAMES = DATA["dim_names"]

# SBTI 数据（题目 / 15 维度 / 25 种人格 / 解释）
with open(os.path.join(BASE_DIR, "sbti_data.json"), encoding="utf-8") as f:
    SBTI = json.load(f)

SBTI_DIMS = SBTI["dims"]
SBTI_DIM_META = SBTI["dimMeta"]
SBTI_QUESTIONS = SBTI["questions"]
SBTI_SPECIAL = SBTI["special"]
SBTI_TYPES = SBTI["types"]
SBTI_EXPL = SBTI["explanations"]
SBTI_LEVEL = {"L": 1, "M": 2, "H": 3}

FONT_CANDIDATES = [
    os.path.join(BASE_DIR, "assets", "NotoSansCJKsc-Regular.otf"),
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
]
for _f in FONT_CANDIDATES:
    if os.path.exists(_f):
        LabelBase.register(name="Roboto", fn_regular=_f, fn_bold=_f)
        break

# 色板（取自 SBTI 页面 computed style）
BG = (0.965, 0.984, 0.973, 1)             # #F6FBF8 背景
CARD = (1, 1, 1, 1)                       # 卡片
BORDER = (0.859, 0.910, 0.867, 1)         # #DBE8DD 卡片描边
TEXT = (0.118, 0.165, 0.133, 1)           # #1E2A22 主文字
HINT = (0.416, 0.471, 0.435, 1)           # #6A786F 次要文字
PRIMARY = (0.302, 0.416, 0.325, 1)        # #4D6A53 墨绿
SOFT = (0.906, 0.945, 0.918, 1)           # #E7F1EA 浅绿底
OPTION_BG = (0.973, 0.988, 0.976, 1)      # #F8FCF9 选项底
OPTION_BORDER = (0.737, 0.816, 0.757, 1)  # #BCD0C1 选项描边
TRACK = (0.929, 0.953, 0.933, 1)          # #EDF3EE 进度轨道
WHITE = (1, 1, 1, 1)


def txt(text, size=15, color=TEXT, bold=False, halign="left"):
    """自适应高度的中文标签。"""
    return MDLabel(
        text=text,
        font_size=f"{size}sp",
        theme_font_size="Custom",
        theme_text_color="Custom",
        text_color=color,
        bold=bold,
        halign=halign,
        valign="middle",
        adaptive_height=True,
        size_hint_y=None,
    )


def spacer(h=8):
    return Label(size_hint_y=None, height=dp(h))


class Panel(BoxLayout):
    """白色大圆角卡片：细描边 + 柔和阴影。"""

    RADIUS = 22

    def __init__(self, pad=(16, 16, 16, 16), spacing=10, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, None),
            padding=[dp(pad[0]), dp(pad[1]), dp(pad[2]), dp(pad[3])],
            spacing=dp(spacing),
            **kwargs,
        )

        with self.canvas.before:
            Color(0.18, 0.29, 0.22, 0.06)
            self._shadow = RoundedRectangle(radius=[dp(self.RADIUS)])
            Color(*CARD)
            self._fill = RoundedRectangle(radius=[dp(self.RADIUS)])
            Color(*BORDER)
            self._line = Line(width=1)

        self.bind(pos=self._sync, size=self._sync)
        self.bind(minimum_height=self.setter("height"))

    def _sync(self, *args):
        r = [dp(self.RADIUS)]
        self._shadow.pos = (self.x, self.y - dp(5))
        self._shadow.size = self.size
        self._shadow.radius = r
        self._fill.pos = self.pos
        self._fill.size = self.size
        self._fill.radius = r
        self._line.rounded_rectangle = (
            self.x, self.y, self.width, self.height, dp(self.RADIUS)
        )


class Pill(ButtonBehavior, BoxLayout):
    """圆角按钮：filled 墨绿 / outline 白底描边 / text 纯文字。"""

    def __init__(self, label, on_press=None, kind="filled", height=dp(48),
                 font_size=16, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, None),
            height=height,
            padding=[dp(8), 0, dp(8), 0],
            **kwargs,
        )
        self.kind = kind
        self._on_press = on_press

        if kind == "filled":
            fill_color, line_color, text_color = PRIMARY, PRIMARY, WHITE
        elif kind == "outline":
            fill_color, line_color, text_color = WHITE, OPTION_BORDER, PRIMARY
        else:
            fill_color, line_color, text_color = (1, 1, 1, 0), (1, 1, 1, 0), PRIMARY

        with self.canvas.before:
            Color(*fill_color)
            self._bg = RoundedRectangle(radius=[dp(14)])
            if kind != "text":
                Color(*line_color)
                self._border = Line(width=1)
            else:
                self._border = None

        self.bind(pos=self._sync, size=self._sync)
        self.add_widget(
            MDLabel(
                text=label,
                font_size=f"{font_size}sp",
                theme_font_size="Custom",
                theme_text_color="Custom",
                text_color=text_color,
                bold=True,
                halign="center",
                valign="middle",
            )
        )

    def _sync(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [dp(14)]
        if self._border is not None:
            self._border.rounded_rectangle = (
                self.x, self.y, self.width, self.height, dp(14)
            )

    def on_release(self):
        if self._on_press:
            self._on_press()


class OptionRow(ButtonBehavior, BoxLayout):
    """选项行：圆形选择点 + 文字，整行可点。"""

    PAD_V = 14
    MIN_H = 52

    def __init__(self, text, on_select=None, selected=False, letter=None,
                 **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(self.MIN_H),
            padding=[dp(44), dp(10), dp(16), dp(10)],
            spacing=dp(10),
            **kwargs,
        )
        self._on_select = on_select
        self.selected = selected
        self.letter = letter

        with self.canvas.before:
            Color(*(SOFT if selected else OPTION_BG))
            self._bg = RoundedRectangle(radius=[dp(14)])
            Color(*(PRIMARY if selected else OPTION_BORDER))
            self._border = Line(width=1)
            Color(*(PRIMARY if selected else OPTION_BORDER))
            self._ring = Line(width=1.4)
            Color(*(PRIMARY if selected else (1, 1, 1, 0)))
            self._dot = Ellipse()

        self.bind(pos=self._sync, size=self._sync)

        label_text = f"{letter}. {text}" if letter else text
        self._label = txt(label_text, 15, color=TEXT)
        self._label.bind(height=self._relayout)
        self.add_widget(self._label)

        self._relayout()
        # 布局稳定后再画一次，避免最后一行圆圈停在中间态坐标
        Clock.schedule_once(lambda dt: self._sync(), 0)

    def _relayout(self, *args):
        self.height = max(dp(self.MIN_H), self._label.height + dp(20))
        Clock.schedule_once(lambda dt: self._sync(), 0)

    def _sync(self, *args):
        r = [dp(14)]
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = r
        self._border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, dp(14)
        )

        cx = self.x + dp(24)
        cy = self.center_y
        rad = dp(8)
        self._ring.circle = (cx, cy, rad)
        self._dot.pos = (cx - rad / 2, cy - rad / 2)
        self._dot.size = (rad, rad)

    def set_selected(self, value):
        self.selected = value
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*(SOFT if value else OPTION_BG))
            self._bg = RoundedRectangle(radius=[dp(14)], pos=self.pos, size=self.size)
            Color(*(PRIMARY if value else OPTION_BORDER))
            self._border = Line(width=1)
            Color(*(PRIMARY if value else OPTION_BORDER))
            self._ring = Line(width=1.4)
            Color(*(PRIMARY if value else (1, 1, 1, 0)))
            self._dot = Ellipse()
        self._sync()

    def on_release(self):
        if self._on_select:
            self._on_select()


class ThinProgress(BoxLayout):
    """细进度条。"""

    def __init__(self, value=0.0, height=dp(6), **kwargs):
        super().__init__(size_hint=(1, None), height=height, **kwargs)
        self.value = max(0.0, min(1.0, value))
        with self.canvas.before:
            Color(*TRACK)
            self._track = RoundedRectangle(radius=[dp(3)])
            Color(*PRIMARY)
            self._fill = RoundedRectangle(radius=[dp(3)])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self._track.pos = self.pos
        self._track.size = self.size
        self._track.radius = [dp(3)]
        w = max(0, self.width * self.value)
        self._fill.pos = self.pos
        self._fill.size = (w, self.height)
        self._fill.radius = [dp(3)]


class DualBar(BoxLayout):
    """双色比例条：左侧按比例填充主色，用于 MBTI 维度比例。"""

    def __init__(self, ratio=0.5, height=dp(6), **kwargs):
        super().__init__(size_hint=(1, None), height=height, **kwargs)
        self.ratio = max(0.0, min(1.0, ratio))
        with self.canvas.before:
            Color(*SOFT)
            self._track = RoundedRectangle(radius=[dp(3)])
            Color(*PRIMARY)
            self._fill = RoundedRectangle(radius=[dp(3)])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self._track.pos = self.pos
        self._track.size = self.size
        self._track.radius = [dp(3)]
        self._fill.pos = self.pos
        self._fill.size = (self.width * self.ratio, self.height)
        self._fill.radius = [dp(3)]


class Chip(ButtonBehavior, BoxLayout):
    """1~7 评分小胶囊。"""

    def __init__(self, number, on_select=None, selected=False, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(40),
            padding=[0, 0, 0, 0],
            **kwargs,
        )
        self.number = number
        self._on_select = on_select
        self.selected = selected

        with self.canvas.before:
            Color(*(PRIMARY if selected else OPTION_BG))
            self._bg = RoundedRectangle(radius=[dp(12)])
            Color(*(PRIMARY if selected else OPTION_BORDER))
            self._border = Line(width=1)

        self.bind(pos=self._sync, size=self._sync)
        self._label = MDLabel(
            text=str(number),
            font_size="14sp",
            theme_font_size="Custom",
            theme_text_color="Custom",
            text_color=(WHITE if selected else TEXT),
            bold=selected,
            halign="center",
            valign="middle",
        )
        self.add_widget(self._label)

    def _sync(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [dp(12)]
        self._border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, dp(12)
        )

    def set_selected(self, value):
        self.selected = value
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*(PRIMARY if value else OPTION_BG))
            self._bg = RoundedRectangle(radius=[dp(12)], pos=self.pos, size=self.size)
            Color(*(PRIMARY if value else OPTION_BORDER))
            self._border = Line(width=1)
        self._label.text_color = WHITE if value else TEXT
        self._label.bold = value
        self._sync()

    def on_release(self):
        if self._on_select:
            self._on_select(self.number)


# ---------------------------------------------------------------
# 历史记录
# ---------------------------------------------------------------
class HistoryScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)], spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        header = Panel(pad=(18, 18, 18, 18), spacing=8)
        header.add_widget(txt("历史记录", 22, bold=True))
        header.add_widget(txt("最近 50 条，保存在本机", 12, color=HINT))
        content.add_widget(header)

        hist = app.load_history()
        if not hist:
            empty = Panel(pad=(18, 16, 18, 16), spacing=6)
            empty.add_widget(txt("还没有记录", 15, bold=True))
            empty.add_widget(txt("先去做一个测试吧", 13, color=HINT))
            content.add_widget(empty)
        else:
            for rec in hist:
                card = Panel(pad=(16, 14, 16, 14), spacing=6)
                row = BoxLayout(
                    orientation="horizontal", size_hint=(1, None),
                    height=dp(22),
                )
                row.add_widget(txt(rec.get("title", ""), 14, bold=True))
                row.add_widget(
                    txt(rec.get("time", ""), 11, color=HINT, halign="right")
                )
                card.add_widget(row)
                card.add_widget(txt(rec.get("summary", ""), 12, color=HINT))
                content.add_widget(card)

        btn_row = BoxLayout(
            orientation="horizontal", size_hint=(1, None),
            height=dp(48), spacing=dp(10),
        )
        btn_row.add_widget(Pill("清空记录", app.clear_history, kind="outline"))
        btn_row.add_widget(Pill("回首页", app.go_home))
        content.add_widget(btn_row)

        scroll.add_widget(content)
        self.add_widget(scroll)


# ---------------------------------------------------------------
# 首页
# ---------------------------------------------------------------
class HomeScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(24), dp(18), dp(18)],
        )

        hero = Panel(pad=(22, 26, 22, 22), spacing=14)
        hero.add_widget(txt("职业测评", 32, bold=True, halign="center"))
        hero.add_widget(
            txt("霍兰德 · MBTI · SBTI 三个测试", 13, color=HINT, halign="center")
        )
        hero.add_widget(spacer(6))
        hero.add_widget(Pill("霍兰德职业倾向测验", app.start_holland))
        hero.add_widget(Pill("MBTI 职业性格测试", app.start_mbti, kind="outline"))
        hero.add_widget(Pill("SBTI 人格测试", app.start_sbti, kind="outline"))
        hero.add_widget(
            Pill("历史记录", app.show_history, kind="text",
                 height=dp(38), font_size=13)
        )
        hero.add_widget(
            txt("在手机上完成约需 10 分钟", 12, color=HINT, halign="center")
        )

        root.add_widget(hero)
        root.add_widget(Label())

        root.add_widget(
            txt("结果仅供参考，不做专业或职业选择的唯一依据",
                11, color=HINT, halign="center")
        )
        self.add_widget(root)


# ---------------------------------------------------------------
# 霍兰德：勾选一组
# ---------------------------------------------------------------
class ChecklistScreen(MDScreen):
    def __init__(self, app, part, type_key, step, total, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.part = part
        self.type_key = type_key
        self.step = step
        self.total = total
        self.checked = set()
        self.rows = {}

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)], spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        panel = Panel(pad=(18, 18, 18, 18), spacing=12)
        panel.add_widget(ThinProgress(step / total))
        panel.add_widget(
            txt(f"第 {step + 1} / {total} 组", 12, color=HINT, halign="right")
        )
        panel.add_widget(txt(part["name"], 12, color=HINT))
        panel.add_widget(txt(f"{type_key} {TYPES[type_key]['name']}", 22, bold=True))
        panel.add_widget(
            txt("选上你符合的项，可以多选，也可以一个都不选", 12, color=HINT)
        )

        for i, item in enumerate(part["items"][type_key], 1):
            row = OptionRow(
                f"{i}. {item}",
                on_select=lambda idx=i: self._toggle(idx),
            )
            self.rows[i] = row
            panel.add_widget(row)

        panel.add_widget(spacer(4))
        panel.add_widget(
            Pill("下一组" if step + 1 < total else "进入下一步", self._next)
        )

        content.add_widget(panel)
        scroll.add_widget(content)
        self.add_widget(scroll)

    def _toggle(self, idx):
        row = self.rows[idx]
        if idx in self.checked:
            self.checked.discard(idx)
            row.set_selected(False)
        else:
            self.checked.add(idx)
            row.set_selected(True)

    def _next(self):
        self.app.submit_checklist(self.part["key"], self.type_key, len(self.checked))


# ---------------------------------------------------------------
# 霍兰德：能力 / 技能自评（1~7 分）
# ---------------------------------------------------------------
class RatingScreen(MDScreen):
    def __init__(self, app, title, desc, data, on_done, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.on_done = on_done
        self.values = {t: 4 for t in ORDER}
        self.chips = {}

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)], spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        panel = Panel(pad=(18, 18, 18, 18), spacing=12)
        panel.add_widget(txt(title, 22, bold=True))
        panel.add_widget(txt(desc, 12, color=HINT))

        for t in ORDER:
            panel.add_widget(txt(f"{t} {data[t]}", 15, bold=True))
            row = BoxLayout(
                orientation="horizontal", size_hint=(1, None),
                height=dp(40), spacing=dp(4),
            )
            self.chips[t] = []
            for n in range(1, 8):
                chip = Chip(
                    n,
                    on_select=lambda num, key=t: self._pick(key, num),
                    selected=(n == 4),
                )
                self.chips[t].append(chip)
                row.add_widget(chip)
            panel.add_widget(row)

        panel.add_widget(spacer(4))
        panel.add_widget(Pill("下一步", lambda: self.on_done(dict(self.values))))

        content.add_widget(panel)
        scroll.add_widget(content)
        self.add_widget(scroll)

    def _pick(self, key, number):
        self.values[key] = number
        for chip in self.chips[key]:
            chip.set_selected(chip.number == number)


# ---------------------------------------------------------------
# 霍兰德：结果
# ---------------------------------------------------------------
class HollandResultScreen(MDScreen):
    def __init__(self, app, totals, detail=None, **kwargs):
        super().__init__(**kwargs)
        self.detail = detail or {}

        ranking = sorted(ORDER, key=lambda t: (-totals[t], ORDER.index(t)))
        code = "-".join(ranking[:3])

        app.add_history(
            "holland", "霍兰德职业倾向测验",
            f"代码 {code} · " + " ".join(f"{t}{totals[t]}" for t in ORDER),
        )
        self._share_text = (
            f"我的霍兰德职业倾向测验结果：{code}\n"
            + "，".join(f"{t} {TYPES[t]['name']} {totals[t]} 分" for t in ORDER)
        )

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)], spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        hero = Panel(pad=(20, 24, 20, 22), spacing=8)
        hero.add_widget(txt("你的霍兰德代码", 13, color=HINT, halign="center"))
        hero.add_widget(txt(code, 42, bold=True, color=PRIMARY, halign="center"))
        hero.add_widget(
            txt("三个字母依次代表最突出的三种兴趣类型", 12, color=HINT, halign="center")
        )
        content.add_widget(hero)

        scores = Panel(pad=(18, 16, 18, 16), spacing=8)
        scores.add_widget(txt("六维得分", 15, bold=True))
        for t in ORDER:
            row = BoxLayout(
                orientation="horizontal", size_hint=(1, None), height=dp(24),
            )
            row.add_widget(txt(f"{t} {TYPES[t]['name']}", 13))
            row.add_widget(
                txt(f"{totals[t]} 分", 12, color=HINT, halign="right")
            )
            scores.add_widget(row)
            scores.add_widget(ThinProgress(totals[t] / 44))
        content.add_widget(scores)

        # 多维度明细：每型在五个部分的得分
        if self.detail:
            detail_panel = Panel(pad=(18, 16, 18, 16), spacing=10)
            detail_panel.add_widget(txt("各维度明细", 15, bold=True))
            for t in ORDER:
                row = BoxLayout(
                    orientation="horizontal", size_hint=(1, None), height=dp(24)
                )
                row.add_widget(txt(f"{t} {TYPES[t]['name']}", 13, bold=True))
                level = "强" if totals[t] >= 30 else ("中" if totals[t] >= 20 else "弱")
                row.add_widget(
                    txt(level, 13, bold=True, color=PRIMARY, halign="right")
                )
                detail_panel.add_widget(row)

                parts = []
                for key in ("兴趣", "擅长", "喜欢", "能力", "技能"):
                    parts.append(f"{key} {self.detail.get(key, {}).get(t, 0)}")
                detail_panel.add_widget(
                    txt(" · ".join(parts), 12, color=HINT)
                )
            content.add_widget(detail_panel)

        for i, t in enumerate(ranking[:3], 1):
            info = TYPES[t]
            card = Panel(pad=(18, 16, 18, 16), spacing=8)
            card.add_widget(txt(f"{i}. {t} {info['name']}", 17, bold=True))
            card.add_widget(txt(f"特点：{info['traits']}", 13, color=HINT))
            card.add_widget(txt(f"专业：{info['majors']}", 13, color=HINT))
            card.add_widget(txt(f"职业：{info['careers']}", 13, color=HINT))
            content.add_widget(card)

        note = Panel(pad=(18, 16, 18, 16), spacing=6)
        note.add_widget(txt("说明", 14, bold=True))
        note.add_widget(
            txt("三个字母的组合可以到教材职业索引里查具体职业；"
                "分数只代表兴趣倾向，不代表能力高低。", 12, color=HINT)
        )
        content.add_widget(note)

        btn_row = BoxLayout(
            orientation="horizontal", size_hint=(1, None),
            height=dp(48), spacing=dp(10),
        )
        btn_row.add_widget(Pill("再测一次", app.start_holland, kind="outline"))
        btn_row.add_widget(Pill("回首页", app.go_home))
        content.add_widget(btn_row)
        content.add_widget(
            Pill("复制结果", lambda: Clipboard.copy(self._share_text),
                 kind="text", height=dp(38), font_size=13)
        )

        scroll.add_widget(content)
        self.add_widget(scroll)


# ---------------------------------------------------------------
# MBTI：答题
# ---------------------------------------------------------------
class MbtiQuestionScreen(MDScreen):
    def __init__(self, app, index, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.index = index
        total = len(MBTI_ITEMS)
        question, a_text, a_letter, b_text, b_letter = MBTI_ITEMS[index]

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)], spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        panel = Panel(pad=(18, 18, 18, 18), spacing=12)
        panel.add_widget(ThinProgress(index / total))
        panel.add_widget(
            txt(f"{index + 1} / {total}", 12, color=HINT, halign="right")
        )
        panel.add_widget(txt("请选择更符合你的一项", 12, color=HINT))
        panel.add_widget(txt(question, 20, bold=True))
        panel.add_widget(spacer(2))

        panel.add_widget(
            OptionRow(
                a_text,
                on_select=lambda: self.app.answer_mbti(a_letter),
                letter="A",
            )
        )
        panel.add_widget(
            OptionRow(
                b_text,
                on_select=lambda: self.app.answer_mbti(b_letter),
                letter="B",
            )
        )

        panel.add_widget(spacer(6))
        panel.add_widget(
            Pill("返回首页", self.app.go_home, kind="text", height=dp(42),
                 font_size=14)
        )

        content.add_widget(panel)
        scroll.add_widget(content)
        self.add_widget(scroll)


# ---------------------------------------------------------------
# MBTI：结果
# ---------------------------------------------------------------
class MbtiResultScreen(MDScreen):
    def __init__(self, app, counts, **kwargs):
        super().__init__(**kwargs)

        letters = []
        for left, right in DIMENSIONS:
            letters.append(left if counts[left] >= counts[right] else right)
        mbti = "".join(letters)
        traits, careers = MBTI_TYPES[mbti]

        app.add_history(
            "mbti", "MBTI 职业性格测试",
            f"{mbti} · " + " ".join(f"{k}{counts[k]}" for k in "EISNTFJP"),
        )
        self._share_text = f"我的 MBTI 类型是 {mbti}"

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)], spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        hero = Panel(pad=(20, 24, 20, 22), spacing=8)
        hero.add_widget(txt("你的性格类型", 13, color=HINT, halign="center"))
        hero.add_widget(txt(mbti, 44, bold=True, color=PRIMARY, halign="center"))
        hero.add_widget(
            txt("四个字母分别代表四个维度的偏好", 12, color=HINT, halign="center")
        )
        content.add_widget(hero)

        dims = Panel(pad=(18, 16, 18, 16), spacing=10)
        dims.add_widget(txt("维度倾向", 15, bold=True))
        for left, right in DIMENSIONS:
            row = BoxLayout(
                orientation="horizontal", size_hint=(1, None), height=dp(26)
            )
            row.add_widget(
                txt(f"{left} {DIM_NAMES[left]}", 13,
                    bold=counts[left] >= counts[right])
            )
            row.add_widget(
                txt(f"{counts[left]} : {counts[right]}", 12, color=HINT,
                    halign="center")
            )
            row.add_widget(
                txt(f"{DIM_NAMES[right]} {right}", 13, halign="right",
                    bold=counts[right] > counts[left])
            )
            dims.add_widget(row)
        content.add_widget(dims)

        ratio_panel = Panel(pad=(18, 16, 18, 16), spacing=10)
        ratio_panel.add_widget(txt("维度比例", 15, bold=True))
        for left, right in DIMENSIONS:
            total = counts[left] + counts[right]
            pct = round(100 * counts[left] / total) if total else 50
            row = BoxLayout(
                orientation="horizontal", size_hint=(1, None), height=dp(24)
            )
            row.add_widget(
                txt(f"{left} {DIM_NAMES[left]}", 13,
                    bold=counts[left] >= counts[right])
            )
            row.add_widget(
                txt(f"{pct}% / {100 - pct}%", 12, color=HINT, halign="center")
            )
            row.add_widget(
                txt(f"{DIM_NAMES[right]} {right}", 13, halign="right",
                    bold=counts[right] > counts[left])
            )
            ratio_panel.add_widget(row)
            ratio_panel.add_widget(DualBar(pct / 100))
        content.add_widget(ratio_panel)

        traits_card = Panel(pad=(18, 16, 18, 16), spacing=8)
        traits_card.add_widget(txt("典型特征", 15, bold=True))
        traits_card.add_widget(txt(traits, 13, color=HINT))
        content.add_widget(traits_card)

        careers_card = Panel(pad=(18, 16, 18, 16), spacing=8)
        careers_card.add_widget(txt("适合职业", 15, bold=True))
        careers_card.add_widget(txt(careers, 13, color=HINT))
        content.add_widget(careers_card)

        note = Panel(pad=(18, 16, 18, 16), spacing=6)
        note.add_widget(txt("说明", 14, bold=True))
        note.add_widget(
            txt("MBTI 测的是偏好，不是能力；换个心情再测，结果可能变化。",
                12, color=HINT)
        )
        content.add_widget(note)

        btn_row = BoxLayout(
            orientation="horizontal", size_hint=(1, None),
            height=dp(48), spacing=dp(10),
        )
        btn_row.add_widget(Pill("再测一次", app.start_mbti, kind="outline"))
        btn_row.add_widget(Pill("回首页", app.go_home))
        content.add_widget(btn_row)
        content.add_widget(
            Pill("复制结果", lambda: Clipboard.copy(self._share_text),
                 kind="text", height=dp(38), font_size=13)
        )

        scroll.add_widget(content)
        self.add_widget(scroll)


# ---------------------------------------------------------------
# SBTI：人格测试（内容与算法来自 B 站 SBTI 页面）
# ---------------------------------------------------------------
class Badge(BoxLayout):
    """浅绿底的小标签。"""

    def __init__(self, label, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, None),
            padding=[dp(14), dp(10), dp(14), dp(10)],
            **kwargs,
        )
        with self.canvas.before:
            Color(*SOFT)
            self._bg = RoundedRectangle(radius=[dp(14)])
        self.bind(pos=self._sync, size=self._sync)
        self.add_widget(txt(label, 13, color=PRIMARY, bold=True))
        self.bind(minimum_height=self.setter("height"))

    def _sync(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [dp(14)]


class SbtiQuestionBlock(BoxLayout):
    """SBTI 单题：元信息 + 题干 + 选项。"""

    def __init__(self, question, on_answer, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, None),
            spacing=dp(8),
            **kwargs,
        )
        self.qid = question["id"]
        self.options = question["options"]
        self.on_answer = on_answer
        self.value = None
        self.rows = []

        self.add_widget(txt("维度已隐藏", 11, color=HINT))
        self.add_widget(txt(question["text"], 17, bold=True))
        for opt in self.options:
            row = OptionRow(
                opt["label"],
                on_select=lambda v=opt["value"]: self._pick(v),
            )
            self.rows.append(row)
            self.add_widget(row)

        self.bind(minimum_height=self.setter("height"))

    def _pick(self, value):
        self.value = value
        for row, opt in zip(self.rows, self.options):
            row.set_selected(opt["value"] == value)
        self.on_answer(self.qid, value)


class SbtiIntroScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(24), dp(18), dp(18)],
        )
        hero = Panel(pad=(22, 26, 22, 22), spacing=14)
        hero.add_widget(txt("MBTI 已经过时，\nSBTI 来了。", 26, bold=True,
                            halign="center"))
        hero.add_widget(
            txt("31 道题，测出你不太正经的那一面", 13, color=HINT, halign="center")
        )
        hero.add_widget(spacer(6))
        hero.add_widget(Pill("开始测试", app.start_sbti_test))
        hero.add_widget(
            txt("题目与结果均来自 B 站 SBTI 玩具，仅供娱乐", 11, color=HINT,
                halign="center")
        )

        root.add_widget(hero)
        root.add_widget(Label())
        root.add_widget(
            txt("SBTI 结果不具备任何科学效力，别当真", 11, color=HINT,
                halign="center")
        )
        self.add_widget(root)


class SbtiQuestionScreen(MDScreen):
    """SBTI 一题一屏。"""

    def __init__(self, app, index, total, question, answers, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)], spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        panel = Panel(pad=(18, 18, 18, 18), spacing=12)
        panel.add_widget(ThinProgress(index / max(1, total)))
        panel.add_widget(
            txt(f"第 {index + 1} / {total} 题", 12, color=HINT, halign="right")
        )
        panel.add_widget(txt("维度已隐藏", 11, color=HINT))
        panel.add_widget(txt(question["text"], 19, bold=True))
        panel.add_widget(spacer(2))

        current = answers.get(question["id"])
        for opt in question["options"]:
            panel.add_widget(
                OptionRow(
                    opt["label"],
                    on_select=lambda v=opt["value"]: self.app.answer_sbti(
                        question["id"], v),
                    selected=(current == opt["value"]),
                )
            )

        if index > 0:
            panel.add_widget(
                Pill("上一题", self.app.sbti_back, kind="text",
                     height=dp(40), font_size=14)
            )

        content.add_widget(panel)
        scroll.add_widget(content)
        self.add_widget(scroll)


class SbtiResultScreen(MDScreen):
    def __init__(self, app, result, **kwargs):
        super().__init__(**kwargs)
        t = result["type"]

        app.add_history(
            "sbti", "SBTI 人格测试",
            f"{t['cn']}（{t['code']}）· {result['badge']}",
        )
        self._share_text = (
            f"我的 SBTI 人格是 {t['cn']}（{t['code']}）\n"
            f"{result['badge']}\n{t['intro']}"
        )

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)], spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        hero = Panel(pad=(20, 24, 20, 22), spacing=8)
        hero.add_widget(txt(result["kicker"], 12, color=HINT, halign="center"))
        hero.add_widget(txt(t["cn"], 36, bold=True, halign="center"))
        hero.add_widget(txt(t["code"], 15, bold=True, color=PRIMARY,
                            halign="center"))
        hero.add_widget(txt(t["intro"], 13, color=HINT, halign="center"))
        content.add_widget(hero)

        meta = Panel(pad=(18, 16, 18, 16), spacing=10)
        meta.add_widget(Badge(result["badge"]))
        meta.add_widget(txt(result["sub"], 12, color=HINT))
        content.add_widget(meta)

        desc = Panel(pad=(18, 16, 18, 16), spacing=8)
        desc.add_widget(txt("该人格的简单解读", 15, bold=True))
        desc.add_widget(txt(t["desc"], 13, color=HINT))
        content.add_widget(desc)

        dims = Panel(pad=(18, 16, 18, 16), spacing=10)
        dims.add_widget(txt("十五维度评分", 15, bold=True))
        for d in SBTI_DIMS:
            level = result["levels"][d]
            name = SBTI_DIM_META[d]["name"]
            row = BoxLayout(
                orientation="horizontal", size_hint=(1, None), height=dp(24)
            )
            row.add_widget(txt(name, 13, bold=True))
            row.add_widget(txt(level, 13, bold=True, color=PRIMARY,
                               halign="right"))
            dims.add_widget(row)
            dims.add_widget(
                txt(result["explanations"][d], 12, color=HINT)
            )
        content.add_widget(dims)

        btn_row = BoxLayout(
            orientation="horizontal", size_hint=(1, None),
            height=dp(48), spacing=dp(10),
        )
        btn_row.add_widget(Pill("再测一次", app.start_sbti_test, kind="outline"))
        btn_row.add_widget(Pill("回首页", app.go_home))
        content.add_widget(btn_row)
        content.add_widget(
            Pill("复制结果", lambda: Clipboard.copy(self._share_text),
                 kind="text", height=dp(38), font_size=13)
        )

        scroll.add_widget(content)
        self.add_widget(scroll)


def sbti_compute(answers):
    """按原页面算法计算：15 维等级 → 模式 → 距离最小的人格。"""
    totals = {d: 0 for d in SBTI_DIMS}
    for q in SBTI_QUESTIONS:
        totals[q["dim"]] += int(answers.get(q["id"], 0))

    levels = {}
    for d in SBTI_DIMS:
        s = totals[d]
        levels[d] = "L" if s <= 3 else ("M" if s == 4 else "H")

    vec = [SBTI_LEVEL[levels[d]] for d in SBTI_DIMS]

    best = None
    for t in SBTI_TYPES:
        pattern = [SBTI_LEVEL[c] for c in t["pattern"].replace("-", "")]
        dist = sum(abs(a - b) for a, b in zip(vec, pattern))
        exact = sum(1 for a, b in zip(vec, pattern) if a == b)
        sim = max(0, round(100 * (1 - dist / 30)))
        key = (dist, -exact, -sim)
        if best is None or key < best[0]:
            best = (key, t, dist, exact, sim)

    _, t, dist, exact, sim = best
    kicker = "你的主类型"
    badge = f"匹配度 {sim}% · 精准命中 {exact}/15 维"
    sub = "维度命中度较高，当前结果可视为你的第一人格画像。"
    final = t

    if answers.get("drink_gate_q2") == 2:
        final = SBTI["drunk"]
        kicker = "隐藏人格已激活"
        badge = "匹配度 100% · 酒精异常因子已接管"
        sub = "乙醇亲和性过强，系统已直接跳过常规人格审判。"
    elif sim < 60:
        final = SBTI["fallback"]
        kicker = "系统强制兜底"
        badge = f"标准人格库最高匹配仅 {sim}%"
        sub = "标准人格库对你的脑回路集体罢工了，于是系统把你强制分配给了 HHHH。"

    explanations = {d: SBTI_EXPL[d][levels[d]] for d in SBTI_DIMS}

    return {
        "type": final,
        "levels": levels,
        "explanations": explanations,
        "kicker": kicker,
        "badge": badge,
        "sub": sub,
        "similarity": sim,
    }


# ---------------------------------------------------------------
# 主程序
# ---------------------------------------------------------------
class CareerApp(MDApp):
    def build(self):
        self.title = "职业测评"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"

        if platform not in ("android", "ios"):
            Window.size = (400, 680)
        Window.clearcolor = BG

        self.sm = MDScreenManager()
        self.sm.transition = NoTransition()
        self._nav = 0

        self.holland = None
        self.holland_steps = []
        self.holland_index = 0
        self.mbti_counts = None
        self.mbti_index = 0
        self.sbti_answers = {}
        self.sbti_extra = False
        self.sbti_index = 0

        Window.bind(on_keyboard=self._on_keyboard)

        self._swap(HomeScreen(self))
        return self.sm

    def show(self, screen):
        Clock.schedule_once(lambda dt: self._swap(screen), 0)

    def _swap(self, screen):
        try:
            if self.sm.screens:
                for old in list(self.sm.screens):
                    self.sm.remove_widget(old)
            self._nav += 1
            screen.name = f"screen{self._nav}"
            self.sm.add_widget(screen)
        except Exception:
            self._show_error(traceback.format_exc())

    def _show_error(self, text):
        try:
            screen = MDScreen()
            box = BoxLayout(
                orientation="vertical",
                padding=[dp(14), dp(14), dp(14), dp(14)], spacing=dp(8),
            )
            box.add_widget(txt("出错了，请把这一页截图发给开发者", 16, bold=True))
            scroll = ScrollView(do_scroll_x=False)
            content = MDLabel(
                text=text,
                font_size="11sp",
                theme_font_size="Custom",
                theme_text_color="Custom",
                text_color=TEXT,
                halign="left",
                valign="top",
                size_hint_y=None,
                adaptive_height=True,
                text_size=(300, None),
            )
            scroll.add_widget(content)
            box.add_widget(scroll)
            screen.add_widget(box)

            if self.sm.screens:
                for old in list(self.sm.screens):
                    self.sm.remove_widget(old)
            self._nav += 1
            screen.name = f"screen{self._nav}"
            self.sm.add_widget(screen)
        except Exception:
            pass

    def _on_keyboard(self, window, key, *args):
        if key == 27:
            current = self.sm.current_screen if self.sm.screens else None
            if isinstance(current, HomeScreen):
                return False
            self.go_home()
            return True
        return False

    def go_home(self):
        self.show(HomeScreen(self))

    # ---------- 历史记录 ----------
    def _history_path(self):
        return os.path.join(self.user_data_dir, "history.json")

    def load_history(self):
        try:
            with open(self._history_path(), encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def add_history(self, kind, title, summary):
        try:
            rec = {
                "kind": kind,
                "title": title,
                "time": time.strftime("%Y-%m-%d %H:%M"),
                "summary": summary,
            }
            hist = self.load_history()
            hist.insert(0, rec)
            hist = hist[:50]
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self._history_path(), "w", encoding="utf-8") as f:
                json.dump(hist, f, ensure_ascii=False, indent=1)
        except Exception:
            pass

    def clear_history(self):
        try:
            os.remove(self._history_path())
        except Exception:
            pass
        self.show(HistoryScreen(self))

    def show_history(self):
        self.show(HistoryScreen(self))

    # ---------- 霍兰德 ----------
    def start_holland(self):
        self.holland = {p["key"]: {} for p in PARTS}
        self.holland["能力"] = {}
        self.holland["技能"] = {}
        self.holland_steps = [(part, t) for part in PARTS for t in ORDER]
        self.holland_index = 0
        self.show_checklist()

    def show_checklist(self):
        part, t = self.holland_steps[self.holland_index]
        self.show(
            ChecklistScreen(self, part, t, self.holland_index,
                            len(self.holland_steps))
        )

    def submit_checklist(self, part_key, t, count):
        self.holland[part_key][t] = count
        self.holland_index += 1
        if self.holland_index < len(self.holland_steps):
            self.show_checklist()
        else:
            self.show_ratings()

    def show_ratings(self):
        self.show(
            RatingScreen(
                self, "表 A · 能力自评",
                "和同龄人比一比，给自己六项能力打分（1~7，越大越强）",
                ABILITY, self.finish_ability,
            )
        )

    def finish_ability(self, values):
        self.holland["能力"] = values
        self.show(
            RatingScreen(
                self, "表 B · 技能自评",
                "再给自己的六项技能打分（1~7）",
                SKILL, self.finish_skill,
            )
        )

    def finish_skill(self, values):
        self.holland["技能"] = values
        totals = {
            t: sum(self.holland[p][t]
                   for p in ("兴趣", "擅长", "喜欢", "能力", "技能"))
            for t in ORDER
        }
        self.show(HollandResultScreen(self, totals, self.holland))

    # ---------- SBTI ----------
    def start_sbti(self):
        self.show(SbtiIntroScreen(self))

    def sbti_question_list(self):
        qs = list(SBTI_QUESTIONS) + [SBTI_SPECIAL["drink_gate_q1"]]
        if self.sbti_extra:
            qs.append(SBTI_SPECIAL["drink_gate_q2"])
        return qs

    def start_sbti_test(self):
        self.sbti_answers = {}
        self.sbti_extra = False
        self.sbti_index = 0
        self.show_sbti_question()

    def show_sbti_question(self):
        qs = self.sbti_question_list()
        idx = min(self.sbti_index, len(qs) - 1)
        self.show(
            SbtiQuestionScreen(self, idx, len(qs), qs[idx], self.sbti_answers)
        )

    def answer_sbti(self, qid, value):
        self.sbti_answers[qid] = value
        if qid == "drink_gate_q1" and value == 3:
            self.sbti_extra = True

        qs = self.sbti_question_list()
        nxt = self.sbti_index + 1
        if nxt < len(qs):
            self.sbti_index = nxt
            self.show(
                SbtiQuestionScreen(self, nxt, len(qs), qs[nxt],
                                   self.sbti_answers)
            )
        else:
            self.show(SbtiResultScreen(self, sbti_compute(self.sbti_answers)))

    def sbti_back(self):
        if self.sbti_index <= 0:
            return
        self.sbti_index -= 1
        qs = self.sbti_question_list()
        self.show(
            SbtiQuestionScreen(self, self.sbti_index, len(qs),
                               qs[self.sbti_index], self.sbti_answers)
        )

    # ---------- MBTI ----------
    def start_mbti(self):
        self.mbti_counts = {k: 0 for k in "EISNTFJP"}
        self.mbti_index = 0
        self.show(MbtiQuestionScreen(self, 0))

    def answer_mbti(self, letter):
        self.mbti_counts[letter] += 1
        self.mbti_index += 1
        if self.mbti_index < len(MBTI_ITEMS):
            self.show(MbtiQuestionScreen(self, self.mbti_index))
        else:
            self.show(MbtiResultScreen(self, self.mbti_counts))


if __name__ == "__main__":
    CareerApp().run()
