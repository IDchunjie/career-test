# -*- coding: utf-8 -*-
"""开发用：单独显示 MBTI 结果页，方便检查版式。"""

import os
import sys

os.environ.setdefault("KIVY_NO_ARGS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.core.window import Window

import app as A


class Mini(A.CareerApp):
    def build(self):
        root = super().build()
        Window.size = (400, 680)
        counts = {"E": 4, "I": 3, "S": 3, "N": 4, "T": 3, "F": 4, "J": 3, "P": 4}
        self.show(A.MbtiResultScreen(self, counts))
        return root


if __name__ == "__main__":
    Mini().run()
