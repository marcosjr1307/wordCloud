"""Gera as nuvens de palavras combinadas (Keywords + Abstract + Título sem termos de busca) com o degradê verde."""
from pathlib import Path
import sys

from PIL import Image
from wordcloud import WordCloud

from plot_wordcloud import (
    create_ellipse_mask,
    create_oil_drop_mask,
    get_font_path,
    load_external_mask,
    load_frequencies,
    make_custom_palette_color_func,
    save_wordcloud_figure,
)
import settings as cfg


def main() -> int:
    fig_cfg = cfg.FIGURE
    frequencies = load_frequencies(cfg.COMBINED_NO_SEARCH_COUNTS_CSV)
    if not frequencies:
        print(f"Nenhum termo encontrado em {cfg.COMBINED_NO_SEARCH_COUNTS_CSV}")
        return 1

    out_dir = Path(cfg.RESULTS_COMBINED_NO_SEARCH_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    masks_dir = Path(cfg.MASKS_DIR)
    masks_dir.mkdir(parents=True, exist_ok=True)

    font_path = get_font_path(fig_cfg["font_family"], fig_cfg["font_weight"])

    # Calibra o degradê verde nas 100 palavras mais frequentes para manter alto contraste visual
    top_n_freqs = dict(list(frequencies.items())[:100])
    green_color_func = make_custom_palette_color_func(
        top_n_freqs,
        fig_cfg["custom_palette"],
    )
    green_contour = fig_cfg["helmet_contour_color"]

    # 1. Nuvem de Palavras Regular (Formato padrão elíptico/retangular)
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
    wc_regular.recolor(color_func=green_color_func)

    saved_reg = save_wordcloud_figure(
        wc_regular,
        figsize=fig_cfg["figsize_regular"],
        out_stem=out_dir / "combinado_sem_busca_regular",
        formats=fig_cfg["output_formats"],
        dpi=fig_cfg["dpi"],
        bg_color=fig_cfg["background_color"],
    )

    # 2. Nuvem de Palavras com Máscara de Óleo e Gás (Gota de Petróleo)
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
    wc_masked.recolor(color_func=green_color_func)

    saved_mask = save_wordcloud_figure(
        wc_masked,
        figsize=fig_cfg["figsize_mask"],
        out_stem=out_dir / "combinado_sem_busca_mascara_oleo_gas",
        formats=fig_cfg["output_formats"],
        dpi=fig_cfg["dpi"],
        bg_color=fig_cfg["background_color"],
        outline_points=drop_points,
        outline_color=green_contour,
        outline_lw=fig_cfg["mask_contour_width"],
    )

    # 3. Nuvem de Palavras com Máscara de Capacete (Helmet Mask)
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
            max_words=105,
            prefer_horizontal=0.72,
            relative_scaling=0.50,
            min_font_size=8,
            max_font_size=120,
            margin=4,
            random_state=fig_cfg["random_state"],
            collocations=False,
        ).generate_from_frequencies(frequencies)
        wc_helmet.recolor(color_func=green_color_func)

        saved_helmet = save_wordcloud_figure(
            wc_helmet,
            figsize=fig_cfg["figsize_helmet"],
            out_stem=out_dir / "combinado_sem_busca_mascara_helmet",
            formats=fig_cfg["output_formats"],
            dpi=fig_cfg["dpi"],
            bg_color=fig_cfg["background_color"],
            contour_field=helmet_field,
            outline_color=green_contour,
            outline_lw=fig_cfg["mask_contour_width"],
        )

    print("Nuvens de palavras combinadas (Sem Termos de Busca - Gradiente Verde) geradas com sucesso:")
    for p in saved_reg + saved_mask + saved_helmet:
        print(f"  - {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
