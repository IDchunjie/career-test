# -*- coding: utf-8 -*-
"""开发用：按固定节奏自动翻页，配合桌面截屏逐个检查页面。"""

import os
import sys

os.environ.setdefault("KIVY_NO_ARGS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.clock import Clock
from kivy.core.window import Window

import app as A


class Drive(A.CareerApp):
    def build(self):
        root = super().build()
        Window.size = (400, 680)
        Clock.schedule_once(lambda dt: self.start_holland(), 7)
        Clock.schedule_once(lambda dt: self.fill_holland(), 13)
        Clock.schedule_once(lambda dt: self.finish_holland(), 19)
        Clock.schedule_once(lambda dt: self.start_mbti(), 25)
        Clock.schedule_once(lambda dt: self.finish_mbti(), 31)
        Clock.schedule_once(lambda dt: self.stop(), 38)
        return root

    def fill_holland(self):
        for part in A.PARTS:
            for t in A.ORDER:
                self.submit_checklist(part["key"], t, (A.ORDER.index(t) + 3) % 10)

    def finish_holland(self):
        self.finish_ability({t: 5 for t in A.ORDER})
        self.finish_skill({t: 4 for t in A.ORDER})

    def finish_mbti(self):
        for question, a_text, a_letter, b_text, b_letter in A.MBTI_ITEMS:
            self.answer_mbti(a_letter)


if __name__ == "__main__":
    Drive().run()
