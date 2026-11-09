# 人格图片素材库 · MBTI 16 型 + SBTI 27 型

本文件夹收集了两套人格测试的配图，可直接用于 `E:\career_app` 里的职业测评 App（结果页配图）。

```
E:\career_app\图片\
├─ MBTI-INTJ.png … MBTI-ESFP.png    16 张，MBTI 16 型人格头像
├─ SBTI-CTRL.png … SBTI-DRUNK.png   27 张，SBTI 人格插画
├─ MBTI-总览.png                     16 型九宫格预览图（带中文名）
├─ SBTI-总览.png                     27 型九宫格预览图（带中文名）
├─ index.json                        代码 → 文件名 / 中文名 的机器可读索引
└─ README.md                         本说明
```

---

## 一、MBTI（16 型）

| 代码 | 中文名 | 家族 | 文件 |
|---|---|---|---|
| INTJ | 建筑师 | 分析家 NT | `MBTI-INTJ.png` |
| INTP | 逻辑学家 | 分析家 NT | `MBTI-INTP.png` |
| ENTJ | 指挥官 | 分析家 NT | `MBTI-ENTJ.png` |
| ENTP | 辩论家 | 分析家 NT | `MBTI-ENTP.png` |
| INFJ | 提倡者 | 外交家 NF | `MBTI-INFJ.png` |
| INFP | 调停者 | 外交家 NF | `MBTI-INFP.png` |
| ENFJ | 主人公 | 外交家 NF | `MBTI-ENFJ.png` |
| ENFP | 竞选者 | 外交家 NF | `MBTI-ENFP.png` |
| ISTJ | 物流师 | 守护者 SJ | `MBTI-ISTJ.png` |
| ISFJ | 守卫者 | 守护者 SJ | `MBTI-ISFJ.png` |
| ESTJ | 总经理 | 守护者 SJ | `MBTI-ESTJ.png` |
| ESFJ | 执政官 | 守护者 SJ | `MBTI-ESFJ.png` |
| ISTP | 鉴赏家 | 探险家 SP | `MBTI-ISTP.png` |
| ISFP | 探险家 | 探险家 SP | `MBTI-ISFP.png` |
| ESTP | 企业家 | 探险家 SP | `MBTI-ESTP.png` |
| ESFP | 表演者 | 探险家 SP | `MBTI-ESFP.png` |

## 二、SBTI（25 型 + 2 个彩蛋）

| 代码 | 中文名 | 文件 | 备注 |
|---|---|---|---|
| CTRL | 拿捏者 | `SBTI-CTRL.png` | |
| ATM-er | 送钱者 | `SBTI-ATM-er.png` | |
| Dior-s | 雕丝 | `SBTI-Dior-s.jpg` | 原图为 jpg |
| BOSS | 领导者 | `SBTI-BOSS.png` | |
| THAN-K | 感恩者 | `SBTI-THAN-K.png` | |
| OH-NO | 哦不人 | `SBTI-OH-NO.png` | |
| GOGO | 行人 | `SBTI-GOGO.png` | |
| SEXY | 尤物 | `SBTI-SEXY.png` | |
| LOVE-R | 多情者 | `SBTI-LOVE-R.png` | |
| MUM | 妈妈 | `SBTI-MUM.png` | |
| FAKE | 伪人 | `SBTI-FAKE.png` | |
| OG8K | 无所谓人 | `SBTI-OG8K.png` | |
| MALO | 吗喽 | `SBTI-MALO.png` | |
| JOKE-R | 小丑 | `SBTI-JOKE-R.jpg` | 原图为 jpg |
| WOC! | 握草人 | `SBTI-WOC.png` | 文件名去掉 `!` |
| THIN-K | 思考者 | `SBTI-THIN-K.png` | |
| SHIT | 愤世者 | `SBTI-SHIT.png` | |
| ZZZZ | 装死者 | `SBTI-ZZZZ.png` | |
| POOR | 贫困者 | `SBTI-POOR.png` | |
| MONK | 僧人 | `SBTI-MONK.png` | |
| IMSB | 傻者 | `SBTI-IMSB.png` | |
| SOLO | 孤儿 | `SBTI-SOLO.png` | |
| FU?K | 草者 | `SBTI-FU-K.png` | `?` 不能做文件名，改为 `-` |
| DEAD | 死者 | `SBTI-DEAD.png` | |
| IMFW | 废物 | `SBTI-IMFW.png` | |
| HHHH | 傻乐者 | `SBTI-HHHH.png` | 彩蛋：标准人格匹配率不足时的兜底人格 |
| DRUNK | 酒鬼 | `SBTI-DRUNK.png` | 彩蛋：饮酒支线触发 |

## 三、图片从哪来的

**MBTI**：16Personalities 官网的 16 张官方类型头像（低多边形风格矢量插画）。
页面：<https://www.16personalities.com/personality-types>
资源规则：`https://www.16personalities.com/static/images/personality-types/avatars/<小写代码-英文昵称>.png`
例：`intp-logician.png`、`infp-mediator.png`。下载后按 `MBTI-<代码>.png` 重命名。

**SBTI**：B 站「SBTI 人格测试」页面的结果配图。
入口页：<https://www.bilibili.com/toy/SBTI/index.html> → iframe 指向
`https://www.bilibilitoy.com/toy/SBTI/8339161393152-v1/index.html`，其脚本 `assets/index-BtN43TCH.js`
里有一个「人格代码 → 图片 URL」的映射表，图片实际存在 B 站 CDN：
`https://p0.hdslb.com/bfs/activity-plat/static/20260409/49ddaeaba3a23f61a6d2695de40d45f0/<代码>.png`
（另有 4 张放在 `20260410 / 20260413 / 20260414` 目录下，文件名是随机串）。

## 四、规格说明

- MBTI：400×400 PNG，白底（无透明通道），单张 8–12 KB。
- SBTI：约 670×740 到 1030×1010，PNG / JPEG，白底；多数图片内部已经印有「你的人格类型是：中文名 代码」字样，少数是放大特写版（Dior-s、HHHH、SHIT、ZZZZ、DRUNK）。
- 两套图都是**白底不透明**，放进深色卡片时需要自己加一个白色圆角底板，或用 `Image` 的 background_color。

## 五、在 App 里怎么用

```python
import json, os
IMG_DIR = r"E:\career_app\图片"
index = json.load(open(os.path.join(IMG_DIR, "index.json"), encoding="utf-8"))

# MBTI 结果页
mbti = "INFP"
source = os.path.join(IMG_DIR, index["mbti"][mbti]["file"])   # → E:\career_app\图片\MBTI-INFP.png

# SBTI 结果页
code = "CTRL"
source = os.path.join(IMG_DIR, index["sbti"][code]["file"])   # → E:\career_app\图片\SBTI-CTRL.png
```

`index.json` 结构：

```json
{
  "mbti": { "INFP": { "file": "MBTI-INFP.png", "cn": "调停者", "group": "NF", "group_cn": "外交家" } },
  "sbti": { "CTRL": { "file": "SBTI-CTRL.png", "cn": "拿捏者" },
            "HHHH": { "file": "SBTI-HHHH.png", "cn": "傻乐者", "note": "兜底/彩蛋人格…" } }
}
```

## 六、版权提醒

图片版权属于原出处（MBTI 头像 © 16Personalities；SBTI 插画 © 哔哩哔哩及原作者）。
这里仅作**本地学习、个人项目**使用；如果 App 要对外发布 / 商用，请替换为自制或已获授权的素材，
或至少在「关于」页注明出处。
