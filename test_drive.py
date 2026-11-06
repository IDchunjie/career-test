# -*- coding: utf-8 -*-
"""
寮€鍙戠敤锛氳嚜鍔ㄨ蛋涓€閬嶆墍鏈夐〉闈㈠苟鎴浘锛屾鏌ユ湁娌℃湁鐢婚敊銆佹姤閿欍€?涓嶅弬涓庢渶缁?APP锛屽彧鏄垜鑷繁鐢ㄧ殑宸℃鑴氭湰銆?"""

import os
import sys

os.environ.setdefault("KIVY_NO_ARGS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.clock import Clock
from kivy.core.window import Window

import app as A

OUT = r"E:\career_app\shots"
os.makedirs(OUT, exist_ok=True)


class Drive(A.CareerApp):
    def build(self):
        root = super().build()
        Window.size = (400, 680)
        self.actions = [
            ("home", lambda: self.go_home()),
            ("checklist", lambda: self.start_holland()),
            ("rating", self._fill_holland),
            ("holland_result", self._finish_holland),
            ("mbti_question", lambda: self.start_mbti()),
            ("mbti_result", self._finish_mbti),
        ]
        Clock.schedule_once(lambda dt: self._step(0), 1.0)
        return root

    def _fill_holland(self):
        for part in A.PARTS:
            for t in A.ORDER:
                self.submit_checklist(part["key"], t, (A.ORDER.index(t) + 3) % 10)

    def _finish_holland(self):
        self.finish_ability({t: 5 for t in A.ORDER})
        self.finish_skill({t: 4 for t in A.ORDER})

    def _finish_mbti(self):
        for question, a_text, a_letter, b_text, b_letter in A.MBTI_ITEMS:
            self.answer_mbti(a_letter)

    def _step(self, i):
        if i >= len(self.actions):
            self.stop()
            return
        name, action = self.actions[i]
        action()
        Clock.schedule_once(lambda dt: self._shot(name, "a"), 3.0)
        Clock.schedule_once(lambda dt: self._shot(name, "b"), 4.0)
        Clock.schedule_once(lambda dt: self._step(i + 1), 5.0)

    def _shot(self, name, suffix):
        Window.screenshot(name=os.path.join(OUT, f"{name}_{suffix}.png"))


if __name__ == "__main__":
    Drive().run()

