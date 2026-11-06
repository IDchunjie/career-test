# -*- coding: utf-8 -*-
"""
职业测评 APP
霍兰德职业倾向测验（教材原版 180 题）+ MBTI 职业性格测试（28 题）

运行：
    py -3.13 app.py
"""

import json
import os

from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import FadeTransition
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.slider import MDSlider

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

# 中文界面必须换成带中文字形的字体，否则全是方块。
# 优先用项目自带的 Noto Sans SC（打包进 APK 时用），电脑上再退回系统字体。
FONT_CANDIDATES = [
    os.path.join(BASE_DIR, "assets", "NotoSansCJKsc-Regular.otf"),
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
]

for font in FONT_CANDIDATES:
    if os.path.exists(font):
        LabelBase.register(
            name="Roboto",
            fn_regular=font,
            fn_bold=font,
        )
        break

TEXT = (0.12, 0.14, 0.17, 1)
HINT = (0.42, 0.45, 0.50, 1)
TEAL = (0.0, 0.59, 0.53, 1)
BG = (0.965, 0.973, 0.980, 1)


def txt(text, size=15, color=TEXT, bold=False, halign="left"):
    """自动换行、自动撑高的中文标签（用 KivyMD 自带的自适应高度）。"""
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


def card(**kwargs):
    """统一样式的卡片容器（高度跟着内容走）。"""
    kwargs.setdefault("orientation", "vertical")
    kwargs.setdefault("padding", [dp(16), dp(12), dp(16), dp(12)])
    kwargs.setdefault("spacing", dp(4))
    kwargs.setdefault("size_hint", (1, None))
    kwargs.setdefault("radius", [dp(14)])
    kwargs.setdefault("style", "elevated")
    c = MDCard(**kwargs)
    c.bind(minimum_height=c.setter("height"))
    return c


class TapCard(MDCard):
    """整张卡片都能点的卡片。"""

    def __init__(self, on_tap=None, **kwargs):
        super().__init__(**kwargs)
        self._on_tap = on_tap

    def on_touch_down(self, touch):
        if self._on_tap and self.collide_point(*touch.pos):
            self._on_tap()
            return True
        return super().on_touch_down(touch)


class Bar(ProgressBar):
    """细一点的进度条。"""

    def __init__(self, value=0.0, **kwargs):
        super().__init__(
            max=100, value=value, size_hint=(1, None), height=dp(8), **kwargs
        )


class AppButton(BoxLayout):
    """自绘按钮：KivyMD 2.0 的 MDButton 会按内容自适应，干脆自己画一个。"""

    def __init__(self, text, on_tap, filled=True, height=None, text_size=15):
        super().__init__(
            orientation="vertical",
            size_hint=(1, None),
            height=height if height is not None else dp(46),
            padding=[dp(8), 0, dp(8), 0],
        )
        self._on_tap = on_tap

        with self.canvas.before:
            Color(*(TEAL if filled else (1, 1, 1, 1)))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            if not filled:
                Color(*TEAL)
                self._line = Line(
                    rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                    width=1.2,
                )

        self.bind(pos=self._sync, size=self._sync)
        self.add_widget(
            MDLabel(
                text=text,
                font_size=f"{text_size}sp",
                theme_font_size="Custom",
                bold=True,
                halign="center",
                valign="middle",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1) if filled else TEAL,
            )
        )

    def _sync(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        if hasattr(self, "_line"):
            self._line.rounded_rectangle = (
                self.x, self.y, self.width, self.height, dp(12)
            )

    def on_touch_down(self, touch):
        if self._on_tap and self.collide_point(*touch.pos):
            self._on_tap()
            return True
        return super().on_touch_down(touch)


def action_button(text, callback, style="filled", height=None):
    """全宽按钮。"""
    return AppButton(
        text, callback, filled=(style == "filled"), height=height
    )


class CheckRow(MDBoxLayout):
    """一行「复选框 + 文字」，点哪都能勾选。"""

    def __init__(self, text, on_change=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(44),
            spacing=dp(4),
            **kwargs,
        )
        self.on_change = on_change

        self.checkbox = MDCheckbox(
            active=False, size_hint=(None, None), size=(dp(40), dp(40)),
            pos_hint={"center_y": 0.5},
        )
        self.checkbox.bind(active=self._changed)

        self.label = txt(text, 14)
        self.label.pos_hint = {"center_y": 0.5}
        self.label.bind(height=self._relayout)

        self.add_widget(self.checkbox)
        self.add_widget(self.label)

    def _changed(self, checkbox, value):
        if self.on_change:
            self.on_change(value)

    def _relayout(self, *args):
        self.height = max(dp(44), self.label.height + dp(10))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # 点文字也能切换复选框
            if not self.checkbox.collide_point(*touch.pos):
                self.checkbox.active = not self.checkbox.active
                return True
        return super().on_touch_down(touch)


# ---------------------------------------------------------------
# 首页
# ---------------------------------------------------------------
class HomeScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        root = MDBoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(26), dp(18), dp(18)],
            spacing=dp(10),
        )

        root.add_widget(txt("职业测评", 30, bold=True, halign="center"))
        root.add_widget(
            txt("霍兰德职业倾向测验 + MBTI 性格测试", 13, color=HINT, halign="center")
        )
        root.add_widget(Label(size_hint_y=None, height=dp(14)))

        root.add_widget(
            self.entry(
                "霍兰德职业倾向测验",
                "180 题 · 找到你的兴趣类型",
                lambda: self.app.start_holland(),
            )
        )
        root.add_widget(
            self.entry(
                "MBTI 职业性格测试",
                "28 题 · 看看你是哪一型",
                lambda: self.app.start_mbti(),
            )
        )

        root.add_widget(Label())  # 占位，把内容顶到上面

        root.add_widget(
            txt("结果仅供参考，不做专业或职业选择的唯一依据",
                11, color=HINT, halign="center")
        )
        self.add_widget(root)

    def entry(self, title, subtitle, callback):
        c = TapCard(
            on_tap=callback,
            orientation="vertical",
            padding=[dp(16), dp(12), dp(16), dp(10)],
            spacing=dp(2),
            size_hint=(1, None),
            height=dp(78),
            radius=[dp(14)],
            style="elevated",
        )
        c.add_widget(txt(title, 17, bold=True))
        c.add_widget(txt(subtitle, 12, color=HINT))
        return c


# ---------------------------------------------------------------
# 霍兰德：勾选一组题
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

        root = MDBoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(14), dp(16), dp(14)],
            spacing=dp(8),
        )

        # 顶部：进度
        root.add_widget(txt(f"第 {step + 1} / {total} 组", 11, color=HINT, halign="right"))
        root.add_widget(Bar(step / total * 100))

        # 标题
        info = TYPES[type_key]
        root.add_widget(txt(part["name"], 12, color=HINT))
        root.add_widget(txt(f"{type_key} {info['name']}", 20, bold=True))
        root.add_widget(txt("选上你符合的项，可以多选，也可以一个都不选", 12, color=HINT))

        # 题目列表
        scroll = ScrollView(do_scroll_x=False)
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        box.bind(minimum_height=box.setter("height"))

        for i, item in enumerate(part["items"][type_key], 1):
            row = CheckRow(
                f"{i}. {item}",
                on_change=lambda active, idx=i: self._toggle(idx, active),
            )
            row.ids_no = i
            box.add_widget(row)
        scroll.add_widget(box)
        root.add_widget(scroll)

        # 底部按钮
        root.add_widget(
            action_button(
                "下一组" if step + 1 < total else "进入下一步", self._next
            )
        )
        self.add_widget(root)

    def _toggle(self, idx, active):
        if active:
            self.checked.add(idx)
        else:
            self.checked.discard(idx)

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

        root = MDBoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(14), dp(16), dp(14)],
            spacing=dp(8),
        )
        root.add_widget(txt(title, 22, bold=True))
        root.add_widget(txt(desc, 12, color=HINT))

        scroll = ScrollView(do_scroll_x=False)
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        box.bind(minimum_height=box.setter("height"))

        for t in ORDER:
            box.add_widget(self.row(t, data[t]))
        scroll.add_widget(box)
        root.add_widget(scroll)

        root.add_widget(
            action_button("下一步", lambda: self.on_done(dict(self.values)))
        )

        self.add_widget(root)

    def row(self, type_key, label):
        holder = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(64),
            spacing=dp(0),
        )
        top = MDBoxLayout(
            orientation="horizontal", size_hint=(1, None), height=dp(24)
        )
        top.add_widget(txt(f"{type_key} {label}", 13))
        value_label = txt("4", 13, color=TEAL, bold=True, halign="right")
        top.add_widget(value_label)
        holder.add_widget(top)

        slider = MDSlider(
            min=1, max=7, step=1, value=4, size_hint=(1, None),
            height=dp(36),
        )

        def changed(widget, value):
            value_label.text = str(int(value))
            self.values[type_key] = int(value)

        slider.bind(value=changed)
        holder.add_widget(slider)
        return holder


# ---------------------------------------------------------------
# 霍兰德：结果
# ---------------------------------------------------------------
class HollandResultScreen(MDScreen):
    def __init__(self, app, totals, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        ranking = sorted(ORDER, key=lambda t: (-totals[t], ORDER.index(t)))
        code = "-".join(ranking[:3])

        scroll = ScrollView(do_scroll_x=False)
        root = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)],
            spacing=dp(8),
        )
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(txt("霍兰德职业倾向测验", 12, color=HINT, halign="center"))
        root.add_widget(txt("你的霍兰德代码", 15, color=HINT, halign="center"))
        root.add_widget(txt(code, 38, bold=True, color=TEAL, halign="center"))
        root.add_widget(txt("三个字母依次代表最突出的三种兴趣类型", 11, color=HINT, halign="center"))

        # 六项得分
        score_card = card(padding=[dp(16), dp(12), dp(16), dp(12)])
        for t in ORDER:
            row = MDBoxLayout(
                orientation="horizontal", size_hint=(1, None), height=dp(34),
                spacing=dp(8),
            )
            row.add_widget(txt(f"{t} {TYPES[t]['name']}", 12))
            row.add_widget(
                txt(f"{totals[t]} 分", 12, color=TEAL, bold=True, halign="right")
            )
            score_card.add_widget(row)
            score_card.add_widget(Bar(totals[t] / 44 * 100))
        root.add_widget(score_card)

        # 前三名的解释
        for i, t in enumerate(ranking[:3], 1):
            info = TYPES[t]
            c = card()
            c.add_widget(txt(f"{i}. {t} {info['name']}", 16, bold=True))
            c.add_widget(txt(f"特点：{info['traits']}", 12, color=HINT))
            c.add_widget(txt(f"专业：{info['majors']}", 12, color=HINT))
            c.add_widget(txt(f"职业：{info['careers']}", 12, color=HINT))
            root.add_widget(c)

        root.add_widget(txt("提示：三个字母的组合可以到教材职业索引里查具体职业；"
                            "分数只代表兴趣倾向，不代表能力高低。", 11, color=HINT))

        btn_row = MDBoxLayout(spacing=dp(10), size_hint=(1, None), height=dp(46))
        again = action_button("再测一次", self.app.start_holland, style="outlined")
        home = action_button("回首页", self.app.go_home)
        btn_row.add_widget(again)
        btn_row.add_widget(home)
        root.add_widget(btn_row)

        scroll.add_widget(root)
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

        root = MDBoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(16), dp(18), dp(16)],
            spacing=dp(10),
        )
        root.add_widget(txt(f"第 {index + 1} / {total} 题", 11, color=HINT, halign="right"))
        root.add_widget(Bar(index / total * 100))

        root.add_widget(Label(size_hint_y=None, height=dp(10)))
        root.add_widget(txt(question, 20, bold=True))
        root.add_widget(Label(size_hint_y=None, height=dp(6)))

        root.add_widget(self.option("A", a_text, lambda: self.app.answer_mbti(a_letter)))
        root.add_widget(self.option("B", b_text, lambda: self.app.answer_mbti(b_letter)))
        root.add_widget(Label())

        back = action_button("返回首页", self.app.go_home, style="text", height=dp(40))
        root.add_widget(back)

        self.add_widget(root)

    def option(self, letter, text, callback):
        c = TapCard(
            on_tap=callback,
            orientation="horizontal",
            padding=[dp(12), dp(8), dp(14), dp(8)],
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(64),
            radius=[dp(14)],
            style="elevated",
        )

        badge = Label(
            text=letter,
            font_size="20sp",
            bold=True,
            color=TEAL,
            halign="center",
            valign="middle",
            size_hint=(None, 1),
            width=dp(28),
        )
        badge.bind(size=lambda w, v: setattr(w, "text_size", v))

        body = Label(
            text=text,
            font_size="14sp",
            color=TEXT,
            halign="left",
            valign="middle",
            size_hint_y=1,
        )
        body.bind(size=lambda w, v: setattr(w, "text_size", (v[0], None)))

        c.add_widget(badge)
        c.add_widget(body)
        return c


# ---------------------------------------------------------------
# MBTI：结果
# ---------------------------------------------------------------
class MbtiResultScreen(MDScreen):
    def __init__(self, app, counts, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        letters = []
        for left, right in DIMENSIONS:
            letters.append(left if counts[left] >= counts[right] else right)
        mbti = "".join(letters)
        traits, careers = MBTI_TYPES[mbti]

        scroll = ScrollView(do_scroll_x=False)
        root = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(20)],
            spacing=dp(8),
        )
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(txt("MBTI 职业性格测试", 12, color=HINT, halign="center"))
        root.add_widget(txt("你的性格类型", 15, color=HINT, halign="center"))
        root.add_widget(txt(mbti, 40, bold=True, color=TEAL, halign="center"))

        dim_card = card()
        for left, right in DIMENSIONS:
            row = MDBoxLayout(
                orientation="horizontal", size_hint=(1, None), height=dp(30)
            )
            row.add_widget(
                txt(f"{left} {DIM_NAMES[left]}", 12,
                    bold=counts[left] >= counts[right])
            )
            row.add_widget(
                txt(f"{counts[left]} : {counts[right]}", 12, color=HINT,
                    halign="center")
            )
            row.add_widget(
                txt(f"{DIM_NAMES[right]} {right}", 12,
                    halign="right", bold=counts[right] > counts[left])
            )
            dim_card.add_widget(row)
        root.add_widget(dim_card)

        info = card()
        info.add_widget(txt("典型特征", 15, bold=True))
        info.add_widget(txt(traits, 12, color=HINT))
        info.add_widget(txt("适合职业", 15, bold=True))
        info.add_widget(txt(careers, 12, color=HINT))
        root.add_widget(info)

        root.add_widget(txt("提示：MBTI 测的是偏好，不是能力；换个心情再测，结果可能变化。",
                            11, color=HINT))

        btn_row = MDBoxLayout(spacing=dp(10), size_hint=(1, None), height=dp(46))
        again = action_button("再测一次", self.app.start_mbti, style="outlined")
        home = action_button("回首页", self.app.go_home)
        btn_row.add_widget(again)
        btn_row.add_widget(home)
        root.add_widget(btn_row)

        scroll.add_widget(root)
        self.add_widget(scroll)


# ---------------------------------------------------------------
# 主程序：状态与流程
# ---------------------------------------------------------------
class CareerApp(MDApp):
    def build(self):
        self.title = "职业测评"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"

        Window.size = (400, 680)
        Window.clearcolor = BG

        self.sm = MDScreenManager()
        self.sm.transition = FadeTransition(duration=0.15)
        self._nav = 0

        self.holland = None
        self.holland_steps = []
        self.holland_index = 0
        self.mbti_counts = None
        self.mbti_index = 0

        self.go_home()
        return self.sm

    # ---------- 导航 ----------
    def show(self, screen):
        """只保留当前这一屏，避免屏幕越堆越多。"""
        if self.sm.screens:
            for old in list(self.sm.screens):
                self.sm.remove_widget(old)
        self._nav += 1
        screen.name = f"screen{self._nav}"
        self.sm.add_widget(screen)

    def go_home(self):
        self.show(HomeScreen(self))

    # ---------- 霍兰德 ----------
    def start_holland(self):
        self.holland = {p["key"]: {} for p in PARTS}
        self.holland["能力"] = {}
        self.holland["技能"] = {}
        self.holland_steps = [
            (part, t) for part in PARTS for t in ORDER
        ]
        self.holland_index = 0
        self.show_checklist()

    def show_checklist(self):
        part, t = self.holland_steps[self.holland_index]
        self.show(
            ChecklistScreen(
                self, part, t, self.holland_index, len(self.holland_steps)
            )
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
                self,
                "表 A · 能力自评",
                "和同龄人比一比，给自己六项能力打分（1~7，越大越强）",
                ABILITY,
                self.finish_ability,
            )
        )

    def finish_ability(self, values):
        self.holland["能力"] = values
        self.show(
            RatingScreen(
                self,
                "表 B · 技能自评",
                "再给自己的六项技能打分（1~7）",
                SKILL,
                self.finish_skill,
            )
        )

    def finish_skill(self, values):
        self.holland["技能"] = values
        totals = {
            t: sum(self.holland[p][t] for p in ("兴趣", "擅长", "喜欢", "能力", "技能"))
            for t in ORDER
        }
        self.show(HollandResultScreen(self, totals))

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
