import csv
from pathlib import Path
import sys

import matplotlib as mpl
import matplotlib.font_manager as fm
from matplotlib.patches import PathPatch
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud

import settings as cfg


def load_frequencies(csv_path: str) -> dict[str, int]:
    freqs = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = row["keyword"].strip()
            cnt = int(row["count"])
            if kw and cnt > 0:
                freqs[kw] = cnt
    return freqs


def get_font_path(family: str, weight: str) -> str:
    prop = fm.FontProperties(family=family, weight=weight)
    return fm.findfont(prop)


def make_frequency_color_func(
    frequencies: dict[str, int],
    cmap_name: str,
    cmap_range: tuple[float, float],
):
    cmap = mpl.colormaps[cmap_name]
    lo, hi = cmap_range
    counts = list(frequencies.values())
    min_c, max_c = min(counts), max(counts)

    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        c = frequencies.get(word, min_c)
        if max_c > min_c:
            norm = ((c - min_c) / (max_c - min_c)) ** 0.65
        else:
            norm = 1.0
        val = lo + norm * (hi - lo)
        r, g, b, _ = cmap(val)
        return f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})"

    return color_func


def create_ellipse_mask(width: int = 2200, height: int = 1200) -> np.ndarray:
    y, x = np.ogrid[:height, :width]
    cy, cx = height / 2.0, width / 2.0
    ry, rx = height * 0.47, width * 0.48
    inside = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0
    mask = np.full((height, width), 255, dtype=np.uint8)
    mask[inside] = 0
    return mask


def get_oil_drop_polygon(width: int = 1800, height: int = 2000) -> list[tuple[float, float]]:
    cx = width / 2.0
    top_y = height * 0.06
    circle_cy = height * 0.62
    radius = width * 0.39

    dy = circle_cy - top_y
    sin_alpha = radius / dy
    alpha = np.arcsin(np.clip(sin_alpha, -1.0, 1.0))

    theta_right = -alpha
    theta_left = np.pi + alpha

    points = [(cx, top_y)]

    t_vals = np.linspace(0, 1, 100)
    tx_r = cx + radius * np.cos(theta_right)
    ty_r = circle_cy + radius * np.sin(theta_right)
    ctrl_r_x = cx + radius * 0.42
    ctrl_r_y = top_y + (ty_r - top_y) * 0.55
    for t in t_vals[1:]:
        px = (1 - t) ** 2 * cx + 2 * (1 - t) * t * ctrl_r_x + t**2 * tx_r
        py = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * ctrl_r_y + t**2 * ty_r
        points.append((px, py))

    angles = np.linspace(theta_right, theta_left, 200)
    for ang in angles:
        px = cx + radius * np.cos(ang)
        py = circle_cy + radius * np.sin(ang)
        points.append((px, py))

    tx_l = cx + radius * np.cos(theta_left)
    ty_l = circle_cy + radius * np.sin(theta_left)
    ctrl_l_x = cx - radius * 0.42
    ctrl_l_y = top_y + (ty_l - top_y) * 0.55
    for t in t_vals[1:]:
        px = (1 - t) ** 2 * tx_l + 2 * (1 - t) * t * ctrl_l_x + t**2 * cx
        py = (1 - t) ** 2 * ty_l + 2 * (1 - t) * t * ctrl_l_y + t**2 * top_y
        points.append((px, py))

    return points


def create_oil_drop_mask(width: int = 1800, height: int = 2000) -> tuple[np.ndarray, list[tuple[float, float]]]:
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)
    points = get_oil_drop_polygon(width, height)
    draw.polygon(points, fill=0)
    return np.array(img, dtype=np.uint8), points


def load_external_mask(mask_path: str, target_size: int = 2048) -> tuple[np.ndarray, np.ndarray]:
    im = Image.open(mask_path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    comp = Image.alpha_composite(bg, im).convert("L")

    pad = int(im.size[0] * 0.04)
    padded = Image.new("L", (im.size[0] + 2 * pad, im.size[1] + 2 * pad), 255)
    padded.paste(comp, (pad, pad))

    w, h = padded.size
    scale = target_size / max(w, h)
    new_size = (int(w * scale), int(h * scale))
    resized = padded.resize(new_size, Image.Resampling.LANCZOS)

    arr = np.array(resized, dtype=np.float32)
    mask = np.where(arr < 128, 0, 255).astype(np.uint8)
    return mask, arr


def parse_rgb_color(color_str: str) -> tuple[float, float, float]:
    if color_str.startswith("rgb(") and color_str.endswith(")"):
        parts = [int(v.strip()) for v in color_str[4:-1].split(",")]
        return (parts[0] / 255.0, parts[1] / 255.0, parts[2] / 255.0)
    return mpl.colors.to_rgb(color_str)


def render_vector_wordcloud(ax: plt.Axes, wc: WordCloud) -> None:
    if wc.mask is not None:
        height, width = wc.mask.shape[:2]
    else:
        height, width = wc.height, wc.width

    scale = wc.scale
    ax.set_xlim(0, width * scale)
    ax.set_ylim(height * scale, 0)
    ax.set_aspect("equal")

    prop = fm.FontProperties(fname=wc.font_path)
    rot90_vals = {Image.ROTATE_90}
    if hasattr(Image, "Transpose"):
        rot90_vals.add(Image.Transpose.ROTATE_90)

    for (word, _count), font_size, (y, x), orientation, color in wc.layout_:
        x_scaled = x * scale
        y_scaled = y * scale
        fsize = font_size * scale

        pil_font = ImageFont.truetype(wc.font_path, int(fsize))
        (size_x, _size_y), (offset_x, offset_y) = pil_font.font.getsize(word)
        ascent, _descent = pil_font.getmetrics()

        min_x = -offset_x
        max_x = size_x - offset_x
        max_y = ascent - offset_y

        tp = TextPath((0, 0), word, size=fsize, prop=prop)
        if orientation in rot90_vals:
            tx = x_scaled + max_y
            ty = y_scaled + (max_x - min_x)
            transform = Affine2D().scale(1, -1).rotate_deg(-90).translate(tx, ty)
        else:
            tx = x_scaled + min_x
            ty = y_scaled + max_y
            transform = Affine2D().scale(1, -1).translate(tx, ty)

        patch = PathPatch(
            tp.transformed(transform),
            facecolor=parse_rgb_color(color),
            edgecolor="none",
            lw=0,
            antialiased=True,
        )
        ax.add_patch(patch)


def save_wordcloud_figure(
    wc: WordCloud,
    figsize: tuple[float, float],
    out_stem: Path,
    formats: list[str],
    dpi: int,
    bg_color: str,
    outline_points: list[tuple[float, float]] | None = None,
    contour_field: np.ndarray | None = None,
    outline_color: str = "#2C7CBA",
    outline_lw: float = 2.0,
) -> list[Path]:
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["svg.fonttype"] = "none"

    fig, ax = plt.subplots(figsize=figsize, facecolor=bg_color)
    render_vector_wordcloud(ax, wc)

    if outline_points is not None and outline_lw > 0:
        xs = [p[0] for p in outline_points] + [outline_points[0][0]]
        ys = [p[1] for p in outline_points] + [outline_points[0][1]]
        ax.plot(xs, ys, color=outline_color, linewidth=outline_lw, antialiased=True)
    if contour_field is not None and outline_lw > 0:
        ax.contour(
            contour_field,
            levels=[128.0],
            colors=[outline_color],
            linewidths=outline_lw,
            antialiased=True,
        )
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    saved = []
    for ext in formats:
        out_path = out_stem.with_suffix(f".{ext}")
        fig.savefig(
            out_path,
            format=ext,
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.03,
            facecolor=bg_color,
        )
        saved.append(out_path)

    plt.close(fig)
    return saved


def main() -> int:
    fig_cfg = cfg.FIGURE
    frequencies = load_frequencies(cfg.KEYWORDS_COUNTS_CSV)
    if not frequencies:
        print(f"Nenhuma keyword encontrada em {cfg.KEYWORDS_COUNTS_CSV}")
        return 1

    out_dir = Path(cfg.RESULTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    masks_dir = Path(cfg.MASKS_DIR)
    masks_dir.mkdir(parents=True, exist_ok=True)

    font_path = get_font_path(fig_cfg["font_family"], fig_cfg["font_weight"])
    color_func = make_frequency_color_func(
        frequencies,
        fig_cfg["colormap"],
        fig_cfg["colormap_range"],
    )

    reg_mask = create_ellipse_mask(width=2200, height=1200)
    wc_regular = WordCloud(
        width=2200,
        height=1200,
        background_color=fig_cfg["background_color"],
        mask=reg_mask,
        font_path=font_path,
        max_words=fig_cfg["max_words_regular"],
        prefer_horizontal=fig_cfg["prefer_horizontal"],
        relative_scaling=fig_cfg["relative_scaling"],
        min_font_size=fig_cfg["min_font_size"],
        max_font_size=fig_cfg["max_font_size_regular"],
        margin=fig_cfg["margin"],
        random_state=fig_cfg["random_state"],
        collocations=False,
    ).generate_from_frequencies(frequencies)
    wc_regular.recolor(color_func=color_func)

    saved_reg = save_wordcloud_figure(
        wc_regular,
        figsize=fig_cfg["figsize_regular"],
        out_stem=out_dir / "keywords_regular",
        formats=fig_cfg["output_formats"],
        dpi=fig_cfg["dpi"],
        bg_color=fig_cfg["background_color"],
    )

    drop_mask, drop_points = create_oil_drop_mask(width=1800, height=2000)
    Image.fromarray(drop_mask).save(masks_dir / "oil_drop_mask.png")

    wc_masked = WordCloud(
        width=1800,
        height=2000,
        background_color=fig_cfg["background_color"],
        mask=drop_mask,
        font_path=font_path,
        max_words=fig_cfg["max_words_mask"],
        prefer_horizontal=fig_cfg["prefer_horizontal"],
        relative_scaling=fig_cfg["relative_scaling"],
        min_font_size=fig_cfg["min_font_size"],
        max_font_size=fig_cfg["max_font_size_mask"],
        margin=fig_cfg["margin"],
        random_state=fig_cfg["random_state"],
        collocations=False,
    ).generate_from_frequencies(frequencies)
    wc_masked.recolor(color_func=color_func)

    saved_mask = save_wordcloud_figure(
        wc_masked,
        figsize=fig_cfg["figsize_mask"],
        out_stem=out_dir / "keywords_mascara_oleo_gas",
        formats=fig_cfg["output_formats"],
        dpi=fig_cfg["dpi"],
        bg_color=fig_cfg["background_color"],
        outline_points=drop_points,
        outline_color=fig_cfg["mask_contour_color"],
        outline_lw=fig_cfg["mask_contour_width"],
    )

    saved_helmet = []
    helmet_path = Path(cfg.HELMET_MASK_PATH)
    if helmet_path.exists():
        helmet_mask, helmet_field = load_external_mask(str(helmet_path), target_size=2048)
        wc_helmet = WordCloud(
            width=helmet_mask.shape[1],
            height=helmet_mask.shape[0],
            background_color=fig_cfg["background_color"],
            mask=helmet_mask,
            font_path=font_path,
            max_words=116,
            prefer_horizontal=0.72,
            relative_scaling=0.50,
            min_font_size=8,
            max_font_size=120,
            margin=4,
            random_state=fig_cfg["random_state"],
            collocations=False,
        ).generate_from_frequencies(frequencies)
        wc_helmet.recolor(color_func=color_func)

        saved_helmet = save_wordcloud_figure(
            wc_helmet,
            figsize=fig_cfg["figsize_helmet"],
            out_stem=out_dir / "keywords_mascara_helmet",
            formats=fig_cfg["output_formats"],
            dpi=fig_cfg["dpi"],
            bg_color=fig_cfg["background_color"],
            contour_field=helmet_field,
            outline_color=fig_cfg["mask_contour_color"],
            outline_lw=fig_cfg["mask_contour_width"],
        )

    print("Nuvens de palavras geradas com sucesso:")
    for p in saved_reg + saved_mask + saved_helmet:
        print(f"  - {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
