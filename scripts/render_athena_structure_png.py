"""Render the current Athena demo structure map as a PNG."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "docs" / "athena_structure_v0.113.0.png"


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/NotoSansSC-VF.ttf",
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    *,
    max_width: int,
    fill: str = "#26332d",
    line_height: int = 27,
) -> int:
    x, y = xy
    lines: list[str] = []
    for raw_line in text.splitlines():
        current = ""
        for char in raw_line:
            candidate = current + char
            if draw.textlength(candidate, font=font) <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = char
        if current:
            lines.append(current)
    for index, line in enumerate(lines):
        draw.text((x, y + index * line_height), line, font=font, fill=fill)
    return y + len(lines) * line_height


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    title: str,
    body: str,
    fill: str,
    outline: str = "#c9d7ce",
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=2)
    draw.text((x1 + 24, y1 + 18), title, font=F_BOX_TITLE, fill="#0a4f2d")
    draw_wrapped(draw, (x1 + 24, y1 + 58), body, F_BOX, max_width=x2 - x1 - 48)


def side(box: tuple[int, int, int, int], direction: str) -> tuple[int, int]:
    x1, y1, x2, y2 = box
    points = {
        "top": ((x1 + x2) // 2, y1),
        "bottom": ((x1 + x2) // 2, y2),
        "left": (x1, (y1 + y2) // 2),
        "right": (x2, (y1 + y2) // 2),
    }
    return points[direction]


def bezier_points(
    p1: tuple[int, int],
    p2: tuple[int, int],
    *,
    bend: int = 0,
    steps: int = 80,
) -> list[tuple[float, float]]:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if abs(dx) >= abs(dy):
        c1 = (p1[0] + dx * 0.46, p1[1] + bend)
        c2 = (p2[0] - dx * 0.46, p2[1] + bend)
    else:
        c1 = (p1[0] + bend, p1[1] + dy * 0.46)
        c2 = (p2[0] + bend, p2[1] - dy * 0.46)

    points = []
    for index in range(steps + 1):
        t = index / steps
        x = (
            (1 - t) ** 3 * p1[0]
            + 3 * (1 - t) ** 2 * t * c1[0]
            + 3 * (1 - t) * t**2 * c2[0]
            + t**3 * p2[0]
        )
        y = (
            (1 - t) ** 3 * p1[1]
            + 3 * (1 - t) ** 2 * t * c1[1]
            + 3 * (1 - t) * t**2 * c2[1]
            + t**3 * p2[1]
        )
        points.append((x, y))
    return points


def draw_polyline(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    *,
    color: str,
    width: int,
    dashed: bool,
) -> None:
    if not dashed:
        draw.line([(int(x), int(y)) for x, y in points], fill=color, width=width, joint="curve")
        return

    dash_length = 18
    gap_length = 11
    remaining = dash_length
    drawing = True
    previous = points[0]
    for current in points[1:]:
        segment_dx = current[0] - previous[0]
        segment_dy = current[1] - previous[1]
        segment_length = math.hypot(segment_dx, segment_dy)
        if segment_length == 0:
            continue
        cursor = 0.0
        while cursor < segment_length:
            step = min(remaining, segment_length - cursor)
            start_ratio = cursor / segment_length
            end_ratio = (cursor + step) / segment_length
            start = (previous[0] + segment_dx * start_ratio, previous[1] + segment_dy * start_ratio)
            end = (previous[0] + segment_dx * end_ratio, previous[1] + segment_dy * end_ratio)
            if drawing:
                draw.line([(int(start[0]), int(start[1])), (int(end[0]), int(end[1]))], fill=color, width=width)
            cursor += step
            remaining -= step
            if remaining <= 0:
                drawing = not drawing
                remaining = dash_length if drawing else gap_length
        previous = current


def arrow(
    draw: ImageDraw.ImageDraw,
    p1: tuple[int, int],
    p2: tuple[int, int],
    *,
    color: str = "#52725e",
    width: int = 3,
    bend: int = 0,
    dashed: bool = False,
) -> None:
    points = bezier_points(p1, p2, bend=bend)
    draw_polyline(draw, points, color=color, width=width, dashed=dashed)
    p_before = points[-3]
    angle = math.atan2(p2[1] - p_before[1], p2[0] - p_before[0])
    size = 12
    left = (p2[0] - math.cos(angle - 0.58) * size, p2[1] - math.sin(angle - 0.58) * size)
    right = (p2[0] - math.cos(angle + 0.58) * size, p2[1] - math.sin(angle + 0.58) * size)
    draw.polygon([p2, left, right], fill=color)


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str) -> None:
    x, y = xy
    width = int(draw.textlength(text, font=F_SMALL))
    draw.rounded_rectangle((x - 8, y - 4, x + width + 8, y + 24), radius=8, fill="#f6f8f5", outline="#dfe6df")
    draw.text((x, y), text, font=F_SMALL, fill="#4c6255")


WIDTH = 1800
HEIGHT = 1280
IMAGE = Image.new("RGB", (WIDTH, HEIGHT), "#f6f8f5")
DRAW = ImageDraw.Draw(IMAGE)
F_TITLE = load_font(38, bold=True)
F_SUB = load_font(20)
F_BOX_TITLE = load_font(24, bold=True)
F_BOX = load_font(18)
F_SMALL = load_font(15)


def main() -> None:
    boxes = {
        "ui": (60, 150, 455, 375),
        "api": (705, 150, 1095, 342),
        "main": (705, 405, 1095, 590),
        "skills": (60, 430, 455, 620),
        "design": (60, 680, 455, 895),
        "service": (505, 680, 900, 895),
        "production": (950, 680, 1410, 920),
        "data": (1430, 360, 1740, 625),
        "future": (1430, 700, 1740, 930),
        "hermes": (505, 985, 940, 1175),
        "training": (970, 985, 1405, 1175),
    }

    DRAW.text((60, 42), "Santoni Athena Current Structure", font=F_TITLE, fill="#08783f")
    DRAW.text((60, 92), "v0.113.0 路 鏈湴 Demo / 鍙璇佹嵁 / Hermes 璁粌闂幆 路 2026-06-11", font=F_SUB, fill="#56665c")

    rounded_box(
        DRAW,
        boxes["ui"],
        title="浜や簰灞?Web Surfaces",
        body="/ 鐢ㄦ埛椤碉細鎬荤粡鐞?Agent 宸ヤ綔鍙癨n/developer.html 璋冭瘯椤礬n/production.html 鐢熶骇鎺у埗鍙癨n/training.html 璁粌鎺у埗鍙癨n/hermes.html Hermes 鎺у埗鍙癨n/athena-mvp.html 璁捐缁撴瀯鍖栭〉",
        fill="#ffffff",
    )
    rounded_box(
        DRAW,
        boxes["api"],
        title="鏈湴 API / Runtime",
        body="scripts/run_web_demo.py\n/api/status active LLM 鐘舵€乗nworkflow template / overview / analyze\n鐗堟湰銆丆hangelog銆丏ocs 鍚屾",
        fill="#ffffff",
    )
    rounded_box(
        DRAW,
        boxes["main"],
        title="MainAgent 缂栨帓灞?",
        body="韬唤鎸夐挳浼樺厛\n涓枃 / 鑻辨枃璺敱璇嶅吀鍏滃簳\nDesigner / Service / Production 鍒嗘祦\nathena_runtime_event 杈撳嚭",
        fill="#ffffff",
    )
    rounded_box(
        DRAW,
        boxes["skills"],
        title="Athena Skill Layer",
        body="GM daily brief / delivery risk\nmachine fit / material constraint\nbottleneck / quality-scrap\nservice escalation / local follow-up\nSkill Execution Trace 灞曠ず鍒嗘瀽杩囩▼",
        fill="#f3fbff",
    )
    rounded_box(
        DRAW,
        boxes["design"],
        title="Design / Athena MVP",
        body="Design Request 杈撳叆\nStyle3D / CLO / AI 鍥剧墖 / TP 缁撴瀯鍖朶nSWS / Arachne engineering brief\nmanufacturability / sampling / revision",
        fill="#edf7f0",
    )
    rounded_box(
        DRAW,
        boxes["service"],
        title="Service Agent",
        body="Service Case Library\n閿佹満婵€娲?/ online assist\nservice request candidate\n涓嶈嚜鍔ㄦ淳宸ワ紝涓嶅啓鐪熷疄 ticket",
        fill="#edf7f0",
    )
    rounded_box(
        DRAW,
        boxes["production"],
        title="Production Operations Agent",
        body="璁㈠崟鍙锋槸 workflow spine\nERP -> APS -> IOT -> 鐢熶骇 -> 鎴愯。\n浜や粯 / 璐ㄩ噺 / 鎴愭湰 KPI\nRoot cause: 娆惧紡銆佹満鍙般€佺墿鏂欍€佹柟娉曘€佺幆澧冦€佹娴?",
        fill="#e8f4fb",
    )
    rounded_box(
        DRAW,
        boxes["data"],
        title="褰撳墠鏁版嵁灞?",
        body="mock production snapshot\nTianpai 绾辩嚎搴撳瓨 aggregate\nAPS / IOT export fragments\nService cases / training reviews\n涓嶄繚瀛樺師濮嬫晱鎰熷嚟鎹?",
        fill="#ffffff",
    )
    rounded_box(
        DRAW,
        boxes["future"],
        title="鏈潵鐪熷疄闆嗘垚杈圭晫",
        body="ERP DB / APS DB / IOT DB\nHermes live endpoint\n鍙浼樺厛锛屽啓鍏ラ渶纭\ntenant / factory 绾ц蹇嗛殧绂?",
        fill="#ffffff",
    )
    rounded_box(
        DRAW,
        boxes["hermes"],
        title="Hermes / Memory Governance",
        body="memory event: scope / tenant / source\nplaybook candidate / review gate\npromotion: candidate -> reviewed -> approved\n褰撳墠涓?local adapter contract",
        fill="#fff8e8",
    )
    rounded_box(
        DRAW,
        boxes["training"],
        title="Training Automation",
        body="Tianpai task set / regression set\nHermes-style JSON result\nCodex promotion gates\n灏忎慨鑷姩鎺ㄨ繘锛屽ぇ鏀瑰姩浜哄伐纭",
        fill="#fff8e8",
    )

    arrow(DRAW, side(boxes["ui"], "right"), side(boxes["api"], "left"), bend=-12)
    label(DRAW, (520, 232), "HTTP + static pages")
    arrow(DRAW, side(boxes["api"], "bottom"), side(boxes["main"], "top"), bend=0)
    label(DRAW, (815, 362), "active LLM status")
    arrow(DRAW, side(boxes["main"], "left"), side(boxes["skills"], "right"), bend=-16, color="#52725e")
    label(DRAW, (475, 475), "skill routing")
    arrow(DRAW, side(boxes["skills"], "bottom"), side(boxes["production"], "left"), bend=58, color="#52725e", dashed=True)
    label(DRAW, (500, 640), "鎵ц杩囩▼")
    arrow(DRAW, (780, 590), side(boxes["design"], "top"), bend=-64)
    arrow(DRAW, (900, 590), side(boxes["service"], "top"), bend=-18)
    arrow(DRAW, (1010, 590), side(boxes["production"], "top"), bend=28)
    label(DRAW, (1160, 610), "鐢熶骇闂幆")
    arrow(DRAW, side(boxes["production"], "bottom"), side(boxes["hermes"], "top"), bend=65, color="#6e8c79")
    label(DRAW, (755, 946), "璁板繂鍊欓€?")
    arrow(DRAW, side(boxes["hermes"], "right"), side(boxes["training"], "left"), bend=22, color="#6e8c79")
    label(DRAW, (1108, 946), "鍥炲綊璁粌")
    arrow(DRAW, side(boxes["data"], "left"), side(boxes["production"], "right"), bend=-34, color="#8aa097", dashed=True)
    label(DRAW, (1258, 790), "鍙璇佹嵁")
    arrow(DRAW, side(boxes["future"], "left"), side(boxes["production"], "right"), color="#9caf9f", bend=36, dashed=True)
    arrow(DRAW, (1430, 815), side(boxes["hermes"], "right"), color="#9caf9f", bend=72, dashed=True)

    DRAW.rounded_rectangle((60, 1198, 1740, 1246), radius=12, fill="#eef3ef", outline="#d7e0d8")
    DRAW.text(
        (84, 1211),
        "褰撳墠缁撹锛欰thena 宸插舰鎴愪氦浜掑眰銆佺紪鎺掑眰銆佷笟鍔?workflow銆佽瘉鎹暟鎹眰銆丠ermes/Training 杩涘寲灞傦紱鐪熷疄 ERP/APS/IOT/Hermes 浠嶅湪 adapter contract / planned 闃舵銆?",
        font=F_SMALL,
        fill="#44564b",
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    IMAGE.save(OUTPUT_PATH)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()



