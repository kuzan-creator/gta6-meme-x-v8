#!/usr/bin/env python3
"""Draw v8 meme: MISSING poster for GTA VI. Fresh build, 1200x1200.
Renders at 2x (2400x2400), downscales with LANCZOS. Deterministic sine-hash grain.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SC = 2  # supersample factor
W, H = 1200 * SC, 1200 * SC


def v(x):
    """1200-space coordinate -> 2x canvas coordinate."""
    return int(round(x * SC))


def font(path, size):
    return ImageFont.truetype(path, v(size))


FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ---- palette (1200-space layout, 2x canvas) ----
PAPER_TOP = (251, 246, 227)
PAPER_BOT = (243, 234, 208)
FRAME = (32, 40, 62)
NAVY = (31, 42, 68)
RED = (200, 16, 46)
MAGENTA = (214, 51, 108)
MAGENTA_DK = (176, 30, 90)
PINK_BOX = (253, 233, 233)
SKY_TOP = (255, 140, 66)
SKY_MID = (240, 98, 146)
SKY_BOT = (123, 45, 94)
SILH = (61, 30, 58)
SUN = (255, 233, 168)
GLASS_RIM = (31, 42, 68)
GHOST_WHITE = (255, 255, 255)
GHOST_EDGE = (205, 205, 205)

text_bboxes = []  # (label, x0, y0, x1, y1) in 2x coords


def record(label, box):
    text_bboxes.append((label,) + tuple(int(round(c)) for c in box))


def grad_rect(img, box, top, bot):
    """Vertical gradient fill of box (2x coords)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    arr = np.zeros((h, x1 - x0, 3), dtype=np.uint8)
    for i, ch in enumerate(range(3)):
        arr[:, :, ch] = np.linspace(top[ch], bot[ch], h, dtype=np.float64)[:, None]
    img.paste(Image.fromarray(arr, "RGB"), (x0, y0))


def draw_ghost(d, x, y, w, h, edge=True):
    """Small white make.fun ghost: capsule body, two oval eyes, small smile."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=w // 2, fill=GHOST_WHITE,
                        outline=GHOST_EDGE if edge else None, width=v(2) if edge else 1)
    ex, ey = x + w // 2, y + int(h * 0.42)
    ew, eh = max(v(4), w // 7), max(v(6), h // 9)
    gap = w // 5
    d.ellipse([ex - gap - ew, ey - eh, ex - gap + ew, ey + eh], fill=(20, 20, 20))
    d.ellipse([ex + gap - ew, ey - eh, ex + gap + ew, ey + eh], fill=(20, 20, 20))
    d.arc([ex - w // 6, ey + h // 10, ex + w // 6, ey + h // 4],
          start=15, end=165, fill=(20, 20, 20), width=v(2))


def text_center(d, cx, y, s, fnt, fill):
    wlen = d.textlength(s, font=fnt)
    d.text((cx - wlen / 2, y), s, font=fnt, fill=fill)
    return (cx - wlen / 2, y, cx + wlen / 2, y + fnt.size)


def fit_font(draw, s, size, bold, max_w):
    """Largest font size <= size (1200-space) whose width fits max_w (1200-space)."""
    sz = size
    while sz > 10:
        f = font(FB if bold else FR, sz)
        if draw.textlength(s, font=f) / SC <= max_w:
            return f, sz
        sz -= 1
    return font(FB if bold else FR, sz), sz


def main():
    img = Image.new("RGB", (W, H), PAPER_TOP)
    grad_rect(img, (0, 0, W, H), PAPER_TOP, PAPER_BOT)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- frame ----
    d.rectangle([0, 0, W - 1, H - 1], outline=FRAME, width=v(8))
    d.rectangle([v(16), v(16), W - 1 - v(16), H - 1 - v(16)], outline=FRAME, width=v(2))

    # ---- header ----
    f_missing = font(FB, 150)
    box = text_center(d, W / 2, v(18), "MISSING", f_missing, RED)
    record("header MISSING", box)
    f_sub = font(FB, 44)
    box = text_center(d, W / 2, v(158), "HAVE YOU SEEN THIS GAME?", f_sub, NAVY)
    record("subheader", box)

    # ---- sky / illustration zone ----
    sky = (v(60), v(212), v(1140), v(545))
    grad_rect(img, sky, SKY_TOP, SKY_BOT)
    # sun
    sx, sy, sr = v(1000), v(288), v(52)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SUN)
    # skyline silhouettes along the bottom of the sky
    rng = [(60, 470, 150, 545), (150, 440, 250, 545), (250, 485, 330, 545),
           (330, 430, 420, 545), (420, 480, 520, 545), (520, 445, 610, 545),
           (610, 490, 700, 545), (700, 455, 800, 545), (800, 490, 900, 545),
           (900, 440, 990, 545), (990, 480, 1060, 545), (1060, 460, 1140, 545)]
    for (x0, y0, x1, y1) in rng:
        d.rectangle([v(x0), v(y0), v(x1), v(y1)], fill=SILH)
    # one tower with antenna
    d.rectangle([v(355), v(395), v(385), v(545)], fill=SILH)
    d.line([v(370), v(395), v(370), v(368)], fill=SILH, width=v(4))
    d.ellipse([v(366), v(362), v(374), v(370)], fill=(255, 90, 90))

    # ---- game case (own layer, rotated -8 deg) ----
    case = Image.new("RGBA", (v(260), v(330)), (0, 0, 0, 0))
    cd = ImageDraw.Draw(case)
    grad_rect(case, (0, 0, v(260), v(330)), (255, 122, 26), (232, 93, 117))
    cd.rectangle([0, 0, v(260) - 1, v(330) - 1], outline=(26, 26, 46), width=v(6))
    # skyline on the cover
    for (x0, y0, x1) in [(12, 250, 60), (60, 225, 110), (110, 255, 150),
                         (150, 215, 200), (200, 250, 235), (235, 230, 252)]:
        cd.rectangle([v(x0), v(y0), v(x1), v(330)], fill=(123, 45, 94))
    cd.rectangle([v(8), 0, v(26), v(330)], fill=(255, 255, 255))  # spine highlight
    f_tiny = font(FB, 18)
    cd.text((v(130) - cd.textlength("GRAND THEFT AUTO", font=f_tiny) / 2, v(34)),
            "GRAND THEFT AUTO", font=f_tiny, fill=(255, 255, 255))
    f_vi = font(FB, 150)
    vi = "VI"
    tw = cd.textlength(vi, font=f_vi)
    cd.text((v(130) - tw / 2 + v(4), v(118)), vi, font=f_vi, fill=(123, 45, 94))
    cd.text((v(130) - tw / 2, v(112)), vi, font=f_vi, fill=(255, 255, 255))
    f_case = font(FB, 20)
    cd.text((v(130) - cd.textlength("VICE CITY", font=f_case) / 2, v(272)),
            "VICE CITY", font=f_case, fill=(255, 255, 255))
    case = case.rotate(-8, resample=Image.BICUBIC, expand=True)
    img.paste(case, (v(455) - case.width // 2, v(375) - case.height // 2), case)

    # ---- magnifying glass ----
    gx, gy, gr = v(790), v(360), v(105)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr],
              fill=(200, 230, 255, 110), outline=GLASS_RIM, width=v(12))
    # handle down-left
    hx0, hy0 = gx - int(gr * 0.72), gy + int(gr * 0.72)
    hx1, hy1 = v(650), v(505)
    d.line([hx0, hy0, hx1, hy1], fill=GLASS_RIM, width=v(24))
    d.ellipse([hx1 - v(12), hy1 - v(12), hx1 + v(12), hy1 + v(12)], fill=GLASS_RIM)

    # ---- ghost holding the handle ----
    draw_ghost(d, v(584), v(478), v(62), v(76))

    # ---- details rows ----
    rows = [
        ("LAST SEEN:", '5 DEC 2023 — TRAILER 1, VICE CITY'),
        ("MISSING SINCE:", '17 SEP 2013 — 4,811 DAYS'),
        ("HEIGHT:", '214 GB'),
        ("DISTINGUISHING MARKS:", 'NEON PINK "VI" LOGO · ALLIGATOR BITE'),
        ("ANSWERS TO:", '"VI" · "GTA 6" · "FINALLY"'),
    ]
    y = 565
    row_h = 46
    for label, value in rows:
        f_lab, _ = fit_font(d, label, 30, True, 420)
        f_val, _ = fit_font(d, value, 30, False, 640)
        d.text((v(70), v(y)), label, font=f_lab, fill=NAVY)
        vw = d.textlength(value, font=f_val)
        vx = v(1130) - vw
        d.text((vx, v(y)), value, font=f_val, fill=NAVY)
        record("detail label " + label, (v(70), v(y), v(70) + d.textlength(label, font=f_lab), v(y) + f_lab.size))
        record("detail value " + value, (vx, v(y), vx + vw, v(y) + f_val.size))
        # dotted leader between label and value
        lx = v(70) + d.textlength(label, font=f_lab) + v(12)
        rx = vx - v(12)
        dot_y = v(y) + f_lab.size // 2
        xx = lx
        while xx < rx:
            d.ellipse([xx, dot_y - v(2), xx + v(4), dot_y + v(2)], fill=(120, 110, 90))
            xx += v(11)
        y += row_h
    details_top = v(565)

    # ---- timeline ----
    f_tl, _ = fit_font(d, "FILED: 17 SEP 2013 · LAST SIGHTING: 5 DEC 2023 · FOUND: 19 NOV 2026", 27, False, 1060)
    segs = [("FILED: 17 SEP 2013", NAVY, False),
            (" · ", NAVY, False),
            ("LAST SIGHTING: 5 DEC 2023", NAVY, False),
            (" · ", NAVY, False),
            ("FOUND: 19 NOV 2026", RED, True)]
    total = sum(d.textlength(s, font=font(FB if b else FR, 27)) for s, _, b in segs)
    x = W / 2 - total / 2
    ty = v(812)
    for s, col, bold in segs:
        f = font(FB if bold else FR, 27)
        d.text((x, ty), s, font=f, fill=col)
        record("timeline " + s, (x, ty, x + d.textlength(s, font=f), ty + f.size))
        x += d.textlength(s, font=f)

    # ---- reward box ----
    box_y0, box_y1 = v(868), v(958)
    d.rectangle([v(60), box_y0, v(1140), box_y1], fill=PINK_BOX, outline=RED, width=v(3))
    draw_ghost(d, v(92), v(884), v(56), v(66))
    f_rw = font(FB, 46)
    box = text_center(d, W / 2, v(874), "REWARD $79.99", f_rw, RED)
    record("reward line1", box)
    # MAKE.FUN pill, right side of the box
    pill_txt = "MAKE.FUN"
    f_pill = font(FB, 26)
    pw = d.textlength(pill_txt, font=f_pill) + v(36)
    px0, py0 = v(1140) - v(18) - pw, v(882)
    d.rounded_rectangle([px0, py0, px0 + pw, py0 + v(44)], radius=v(22), fill=MAGENTA)
    d.text((px0 + v(18), py0 + v(7)), pill_txt, font=f_pill, fill=(255, 255, 255))
    record("reward pill MAKE.FUN", (px0, py0, px0 + pw, py0 + v(44)))
    f_rw2 = font(FR, 26)
    box = text_center(d, W / 2, v(924), "PAID IN FULL BY MY AI AGENT ON MAKE.FUN", f_rw2, NAVY)
    record("reward line2", box)

    # ---- punchline ----
    f_pl = font(FB, 30)
    box = text_center(d, W / 2, v(976), "IF FOUND, PLEASE RETURN TO ONE PATIENT GAMER.", f_pl, NAVY)
    record("punchline 1", box)
    box = text_center(d, W / 2, v(1014), "HE WAITED 4,811 DAYS — NO QUESTIONS ASKED.", f_pl, NAVY)
    record("punchline 2", box)

    # ---- footer ----
    grad_rect(img, (0, v(1078), W, H), MAGENTA, MAGENTA_DK)
    draw_ghost(d, v(78), v(1096), v(70), v(86), edge=False)
    # white pill MAKE.FUN
    f_fp = font(FB, 26)
    fpw = d.textlength("MAKE.FUN", font=f_fp) + v(36)
    fx0, fy0 = v(176), v(1106)
    d.rounded_rectangle([fx0, fy0, fx0 + fpw, fy0 + v(44)], radius=v(22), fill=(255, 255, 255))
    d.text((fx0 + v(18), fy0 + v(7)), "MAKE.FUN", font=f_fp, fill=(194, 24, 91))
    record("footer pill MAKE.FUN", (fx0, fy0, fx0 + fpw, fy0 + v(44)))
    f_ft = font(FR, 24)
    box = d.text((fx0, v(1166)), "POSTERS PRINTED BY MAKE.FUN — WHERE AI AGENTS EARN REAL MONEY.",
                 font=f_ft, fill=(255, 255, 255))
    record("footer line", (fx0, v(1166), fx0 + d.textlength("POSTERS PRINTED BY MAKE.FUN — WHERE AI AGENTS EARN REAL MONEY.", font=f_ft), v(1166) + f_ft.size))

    # ---- FOUND! stamp on its own layer ----
    stamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    cx, cy = v(1035), v(465)
    bw, bh = v(266), v(86)
    sd.rectangle([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2],
                 outline=RED, width=v(7))
    sd.rectangle([cx - bw // 2 + v(12), cy - bh // 2 + v(12),
                  cx + bw // 2 - v(12), cy + bh // 2 - v(12)],
                 outline=RED, width=v(3))
    f_st = font(FB, 58)
    st = "FOUND!"
    tw = sd.textlength(st, font=f_st)
    sd.text((cx - tw / 2, cy - f_st.size // 2 - v(4)), st, font=f_st, fill=RED)
    stamp = stamp.rotate(-12, resample=Image.BICUBIC, center=(cx, cy))
    img = Image.alpha_composite(img.convert("RGBA"), stamp).convert("RGB")

    # stamp bbox from the rotated mask
    mask = stamp.split()[3]
    mask.save("/tmp/v8_stamp_mask_2x.png")
    bbox = mask.getbbox()
    # rotated corners of the stamp box, for the report
    ang = math.radians(-12)
    corners = []
    for dx, dy in [(-bw // 2, -bh // 2), (bw // 2, -bh // 2),
                   (bw // 2, bh // 2), (-bw // 2, bh // 2)]:
        rx = cx + dx * math.cos(ang) - dy * math.sin(ang)
        ry = cy + dx * math.sin(ang) + dy * math.cos(ang)
        corners.append((rx, ry))
    stamp_box = (min(c[0] for c in corners), min(c[1] for c in corners),
                 max(c[0] for c in corners), max(c[1] for c in corners))

    # ---- downscale + deterministic grain ----
    img = img.resize((1200, 1200), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float64)
    yy, xx = np.mgrid[0:1200, 0:1200]
    noise = (np.sin(xx * 12.9898 + yy * 78.233) * 43758.5453) % 1.0 - 0.5
    arr += noise[:, :, None] * 6.0
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

    img.save(os.path.join(OUT_DIR, "meme.png"))
    img.save(os.path.join(OUT_DIR, "meme.jpg"), quality=92)
    img.resize((480, 480), Image.LANCZOS).save("/tmp/v8_480.png")

    meta = {
        "stamp_box_2x": [round(c) for c in stamp_box],
        "stamp_mask_bbox_2x": list(bbox),
        "details_top_2x": details_top,
        "footer_top_2x": v(1078),
        "text_bboxes": text_bboxes,
    }
    with open("/tmp/v8_meta.json", "w") as fh:
        json.dump(meta, fh, indent=1)
    print("saved meme.png + meme.jpg, stamp_box_2x =", [round(c) for c in stamp_box])


if __name__ == "__main__":
    main()
