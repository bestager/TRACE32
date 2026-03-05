#!/usr/bin/env python3
"""
Physical AI News Video Generator
- 1-minute news anchor-style video
- English narration with espeak-ng
- Slide frames rendered with Pillow
- Assembled with ffmpeg directly (reliable)
"""

import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ============================================================
# Configuration
# ============================================================
OUTPUT_DIR = Path("output/video")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1920, 1080
FPS = 24

# Colors
BG_COLOR = (15, 23, 42)
ACCENT = (30, 64, 175)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 210, 220)
RED_ACCENT = (220, 38, 38)
GOLD = (245, 189, 65)
CARD_BG = (25, 40, 65)
TICKER_BG = (220, 38, 38)


def get_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc" if bold
        else "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold
        else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ============================================================
# Narration Script
# ============================================================
SCENES = [
    {
        "id": "intro",
        "narration": (
            "Good evening. I'm reporting on the rise of Physical A.I. "
            "product development. Physical A.I. is now a key trend, "
            "with surging investment in autonomous vehicles, robots, and drones."
        ),
        "title": "THE RISE OF PHYSICAL AI",
        "subtitle": "Product Development Report 2026",
        "type": "intro",
    },
    {
        "id": "autonomous",
        "narration": (
            "First, the autonomous driving market. The Korean market is projected "
            "to grow at 29 percent compound annual growth rate, reaching "
            "17.5 billion dollars by 2033. "
            "Hyundai Motor Group is investing 125 trillion Korean Won between "
            "2026 and 2030. Their subsidiary 42dot is developing the "
            "software-defined vehicle known as Pace Car, targeting 2027 launch."
        ),
        "title": "AUTONOMOUS DRIVING",
        "bullets": [
            "Korean market: 29% CAGR -> $17.5B by 2033",
            "Hyundai: 125T KRW investment (2026-2030)",
            "42dot: SDV 'Pace Car' targeting 2027",
        ],
        "type": "content",
    },
    {
        "id": "robots",
        "narration": (
            "Next, robots and urban air mobility. Hyundai is investing "
            "400 billion Won in an A.I. robot factory, aiming to produce "
            "30,000 units per year by 2029. "
            "L.G. Electronics has acquired Bear Robotics to expand its "
            "commercial robot business. "
            "Meanwhile, Naver Labs and Woowa Brothers are leveraging "
            "TRACE32 for NVIDIA-based autonomous robot development."
        ),
        "title": "ROBOTS & UAM",
        "bullets": [
            "Hyundai: 400B KRW AI robot factory",
            "  -> 30K units/year by 2029",
            "LG acquires BearRobotics",
            "Naver Labs & Woowa: TRACE32 + NVIDIA",
        ],
        "type": "content",
    },
    {
        "id": "drones",
        "narration": (
            "In the drones and unmanned vehicles sector, "
            "Bone A.I. has raised 12 million dollars for U.A.V., "
            "U.G.V., and U.S.V. development. "
            "Hyundai Mobis has partnered with Supernal on urban air mobility "
            "battery management system development and D.O. 178 C certification, "
            "a critical safety standard for airborne systems."
        ),
        "title": "DRONES & UNMANNED VEHICLES",
        "bullets": [
            "Bone AI: $12M raised for UAV/UGV/USV",
            "Hyundai Mobis + Supernal partnership",
            "  -> UAM BMS development",
            "  -> DO-178C safety certification",
        ],
        "type": "content",
    },
    {
        "id": "outro",
        "narration": (
            "Physical A.I. is no longer a distant future. "
            "From self-driving cars to delivery robots and air taxis, "
            "Korean tech companies are leading this transformation "
            "with massive investments and strategic partnerships. "
            "That's your tech briefing for today. Stay informed."
        ),
        "title": "PHYSICAL AI: THE FUTURE IS NOW",
        "subtitle": "Korean Tech Leading the Transformation",
        "type": "intro",
    },
]


# ============================================================
# Frame Rendering
# ============================================================

def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)


def draw_news_chrome(draw):
    # Top bar
    draw.rectangle([0, 0, WIDTH, 70], fill=ACCENT)
    font_top = get_font(28, bold=True)
    draw.text((40, 18), "TECH BRIEFING  |  PHYSICAL AI REPORT", fill=WHITE, font=font_top)
    draw.text((WIDTH - 280, 18), "MARCH 2026", fill=GOLD, font=font_top)

    # Bottom ticker
    draw.rectangle([0, HEIGHT - 80, WIDTH, HEIGHT], fill=TICKER_BG)
    font_ticker = get_font(24, bold=True)
    ticker = "BREAKING: Physical AI investment surge across Korea  |  Hyundai, LG, Naver lead  |  $17.5B autonomous driving market"
    draw.text((40, HEIGHT - 58), ticker, fill=WHITE, font=font_ticker)

    # LIVE badge
    draw.rectangle([WIDTH - 160, 90, WIDTH - 40, 130], fill=RED_ACCENT)
    font_live = get_font(24, bold=True)
    draw.text((WIDTH - 140, 94), "* LIVE", fill=WHITE, font=font_live)


def render_intro_frame(scene):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_news_chrome(draw)

    font_title = get_font(72, bold=True)
    font_sub = get_font(36)

    title = scene["title"]
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 280), title, fill=WHITE, font=font_title)

    # Accent line
    draw.rectangle([(WIDTH // 2 - 200), 380, (WIDTH // 2 + 200), 384], fill=GOLD)

    if "subtitle" in scene:
        sub = scene["subtitle"]
        bbox = draw.textbbox((0, 0), sub, font=font_sub)
        sw = bbox[2] - bbox[0]
        draw.text(((WIDTH - sw) // 2, 420), sub, fill=LIGHT_GRAY, font=font_sub)

    if scene["id"] == "intro":
        categories = ["Autonomous", "Robots & UAM", "Drones"]
        icons = ["[car]", "[robot]", "[drone]"]
        card_w = 400
        gap = 60
        start_x = (WIDTH - (card_w * 3 + gap * 2)) // 2
        for i, (cat, icon) in enumerate(zip(categories, icons)):
            x = start_x + i * (card_w + gap)
            draw_rounded_rect(draw, (x, 530, x + card_w, 640), 12, CARD_BG)
            font_cat = get_font(32, bold=True)
            font_icon = get_font(26)
            bbox = draw.textbbox((0, 0), cat, font=font_cat)
            cw = bbox[2] - bbox[0]
            draw.text((x + (card_w - cw) // 2, 570), cat, fill=GOLD, font=font_cat)

    return img


def render_content_frame(scene):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_news_chrome(draw)

    # Section title
    font_section = get_font(56, bold=True)
    draw.text((80, 110), scene["title"], fill=GOLD, font=font_section)
    draw.rectangle([80, 185, 600, 189], fill=GOLD)

    # Content card
    cx, cy = 60, 220
    cw, ch = WIDTH - 120, HEIGHT - 330
    draw_rounded_rect(draw, (cx, cy, cx + cw, cy + ch), 16, CARD_BG)
    draw.rectangle([cx, cy, cx + 6, cy + ch], fill=GOLD)

    # Bullets
    font_b = get_font(40)
    font_bb = get_font(40, bold=True)
    y = cy + 50

    for bullet in scene.get("bullets", []):
        if bullet.startswith("  "):
            draw.text((160, y), "->", fill=GOLD, font=font_b)
            draw.text((230, y), bullet.strip(), fill=LIGHT_GRAY, font=font_b)
        else:
            draw.text((100, y), "*", fill=GOLD, font=font_bb)
            draw.text((150, y), bullet, fill=WHITE, font=font_bb)
        y += 80

    return img


def render_frame(scene):
    if scene["type"] == "intro":
        return render_intro_frame(scene)
    return render_content_frame(scene)


# ============================================================
# TTS via espeak-ng
# ============================================================

def generate_narration(text, output_mp3):
    wav = str(output_mp3).replace(".mp3", ".wav")
    subprocess.run([
        "espeak-ng", "-v", "en-us",
        "-s", "155", "-p", "40", "-a", "180",
        "-w", wav, text,
    ], check=True, capture_output=True)

    subprocess.run([
        "ffmpeg", "-y", "-i", wav,
        "-codec:a", "libmp3lame", "-qscale:a", "2",
        str(output_mp3),
    ], check=True, capture_output=True)

    os.unlink(wav)
    return output_mp3


def get_audio_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


# ============================================================
# Video Assembly (ffmpeg concat)
# ============================================================

def build_video():
    print("\n" + "=" * 60)
    print("  Physical AI News Video Generator")
    print("=" * 60)

    scene_videos = []

    for i, scene in enumerate(SCENES):
        sid = scene["id"]
        print(f"\n[{i+1}/{len(SCENES)}] {sid}")

        # 1. Narration
        audio_path = OUTPUT_DIR / f"narration_{sid}.mp3"
        print(f"  Generating narration...")
        generate_narration(scene["narration"], audio_path)
        duration = get_audio_duration(audio_path) + 0.5

        # 2. Frame
        frame_path = OUTPUT_DIR / f"frame_{sid}.png"
        print(f"  Rendering frame...")
        frame_img = render_frame(scene)
        frame_img.save(str(frame_path))

        # 3. Combine image + audio into video segment
        segment_path = OUTPUT_DIR / f"segment_{sid}.mp4"
        subprocess.run([
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(frame_path),
            "-i", str(audio_path),
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-shortest",
            "-movflags", "+faststart",
            str(segment_path),
        ], check=True, capture_output=True)

        scene_videos.append(segment_path)
        print(f"  Done: {duration:.1f}s")

    # 4. Concat all segments
    print(f"\nAssembling final video...")
    concat_list = OUTPUT_DIR / "concat.txt"
    with open(concat_list, "w") as f:
        for v in scene_videos:
            f.write(f"file '{v.name}'\n")

    final_path = OUTPUT_DIR / "physical_ai_news.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list.resolve()),
        "-c", "copy",
        "-movflags", "+faststart",
        str(final_path.resolve()),
    ], check=True, capture_output=True, cwd=str(OUTPUT_DIR.resolve()))

    # 5. Cleanup
    for f in OUTPUT_DIR.glob("narration_*.mp3"):
        f.unlink()
    for f in OUTPUT_DIR.glob("frame_*.png"):
        f.unlink()
    for f in OUTPUT_DIR.glob("segment_*.mp4"):
        f.unlink()
    concat_list.unlink()

    # 6. Report
    size_mb = os.path.getsize(final_path) / (1024 * 1024)
    dur = get_audio_duration(final_path)

    print(f"\n" + "=" * 60)
    print(f"  Video generated successfully!")
    print(f"  File: {final_path}")
    print(f"  Duration: {dur:.1f}s")
    print(f"  Size: {size_mb:.1f} MB")
    print(f"  Resolution: {WIDTH}x{HEIGHT}")
    print("=" * 60 + "\n")

    return str(final_path)


if __name__ == "__main__":
    build_video()
