# -*- coding: utf-8 -*-
"""开发用：单独显示某个页面，检查版式。用法：python mini_screens.py checklist"""

import os
import sys

os.environ.setdefault("KIVY_NO_ARGS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.core.window import Window

import app as A

MODE = sys.argv[1] if len(sys.argv) > 1 else "home"


class Mini(A.CareerApp):
    def build(self):
        root = super().build()
        Window.size = (400, 680)
        if MODE == "checklist":
            self.show(A.ChecklistScreen(self, A.PARTS[0], "R", 0, 18))
        elif MODE == "rating":
            self.show(
                A.RatingScreen(
                    self, "表 A · 能力自评",
                    "和同龄人比一比，给自己六项能力打分（1~7）",
                    A.ABILITY, lambda values: None,
                )
            )
        elif MODE == "holland":
            totals = {t: 10 + i * 5 for i, t in enumerate(A.ORDER)}
            self.show(A.HollandResultScreen(self, totals))
        return root


if __name__ == "__main__":
    Mini().run()
