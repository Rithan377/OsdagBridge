# =============================================================================
# report_charts.py — Matplotlib chart generators for OsdagBridge reports
# Generates utilization-ratio (UR) and material-quantity (BOQ) bar charts.
# =============================================================================

import os
import tempfile
import logging

logger = logging.getLogger(__name__)

def generate_ur_summary_chart(output_dict, input_dict, save_dir):
    """
    Generate a grouped bar chart of Utilization Ratios (UR) for all primary
    structural elements: Steel Plate Girders, Concrete Deck Slab, Cross
    Bracing, and End Diaphragms.

    A horizontal red dashed line at UR = 1.0 marks the pass/fail threshold.

    Parameters
    ----------
    output_dict : dict
        The full output_dict from the design pipeline.
    input_dict : dict
        The full input_dict (merged with BOQ quantities).
    save_dir : str
        Directory to save the chart PNG.

    Returns
    -------
    str or None
        Absolute path to the saved PNG, or None on failure.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from osdagbridge.core.reports.styles import (
            CHART_DPI, CHART_FIGSIZE, CHART_PASS_COLOR, CHART_FAIL_COLOR,
            CHART_THRESHOLD, CHART_FONT_SIZE, CHART_TITLE_SIZE, CHART_BG_COLOR
        )

        # ── Collect UR values from output_dict ──
        ur_data = []

        # 1. Steel Plate Girder URs (from category_urs)
        category_urs = output_dict.get("category_urs", {})
        girder_checks = [
            ("Flexure", "flexure"),
            ("Shear", "shear"),
            ("Interaction", "interaction"),
            ("LTB", "ltb"),
            ("Fatigue", "fatigue"),
        ]
        for label, key in girder_checks:
            val = category_urs.get(key)
            if val is not None:
                try:
                    ur_data.append((f"Girder — {label}", float(val)))
                except (TypeError, ValueError):
                    pass

        # If no category_urs, try design_checks list
        if not ur_data:
            for dc in output_dict.get("design_checks", []):
                if isinstance(dc, dict) and dc.get("ur") is not None:
                    try:
                        label = dc.get("check", dc.get("name", "Check"))
                        ur_data.append((str(label), float(dc["ur"])))
                    except (TypeError, ValueError):
                        pass

        # 2. Concrete Deck Slab UR
        deck_ur = output_dict.get("deck_ur") or output_dict.get("deck_design", {}).get("ur")
        if deck_ur is not None:
            try:
                ur_data.append(("Deck Slab", float(deck_ur)))
            except (TypeError, ValueError):
                pass

        # 3. Cross Bracing URs (max UR per pair)
        cb_results = output_dict.get("crossbracing_design_results", {})
        max_cb_ur = 0.0
        found_cb = False
        for pair_key, pair_data in cb_results.items():
            if not isinstance(pair_data, dict):
                continue
            for member in ("diagonal", "chord"):
                mdata = pair_data.get(member, {})
                if not isinstance(mdata, dict):
                    continue
                for ft in ("tension", "compression"):
                    ftdata = mdata.get(ft, {})
                    if isinstance(ftdata, dict):
                        eff = ftdata.get("efficiency") or ftdata.get("ur") or ftdata.get("Member.efficiency")
                        if eff is not None:
                            try:
                                max_cb_ur = max(max_cb_ur, float(eff))
                                found_cb = True
                            except (TypeError, ValueError):
                                pass
        if found_cb:
            ur_data.append(("Cross Bracing", max_cb_ur))

        # 4. End Diaphragm URs (same structure as cross bracing)
        ed_results = output_dict.get("enddiaphragm_design_results", {})
        max_ed_ur = 0.0
        found_ed = False
        for pair_key, pair_data in ed_results.items():
            if not isinstance(pair_data, dict):
                continue
            for member in ("diagonal", "chord"):
                mdata = pair_data.get(member, {})
                if not isinstance(mdata, dict):
                    continue
                for ft in ("tension", "compression"):
                    ftdata = mdata.get(ft, {})
                    if isinstance(ftdata, dict):
                        eff = ftdata.get("efficiency") or ftdata.get("ur") or ftdata.get("Member.efficiency")
                        if eff is not None:
                            try:
                                max_ed_ur = max(max_ed_ur, float(eff))
                                found_ed = True
                            except (TypeError, ValueError):
                                pass
        if found_ed:
            ur_data.append(("End Diaphragm", max_ed_ur))

        if not ur_data:
            logger.info("No UR data available for chart generation.")
            return None

        # ── Plot ──
        labels = [d[0] for d in ur_data]
        values = [d[1] for d in ur_data]
        colors = [CHART_PASS_COLOR if v <= CHART_THRESHOLD else CHART_FAIL_COLOR
                  for v in values]

        fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
        fig.patch.set_facecolor(CHART_BG_COLOR)
        ax.set_facecolor(CHART_BG_COLOR)

        x_pos = range(len(labels))
        bars = ax.bar(x_pos, values, color=colors, edgecolor='#333333',
                      linewidth=0.5, width=0.55)

        # Horizontal threshold line
        ax.axhline(y=CHART_THRESHOLD, color='#E74C3C', linestyle='--',
                   linewidth=1.8, label=f'Threshold (UR = {CHART_THRESHOLD})')

        # Value labels on bars
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                    f'{val:.3f}', ha='center', va='bottom',
                    fontsize=CHART_FONT_SIZE - 1, fontweight='bold')

        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=CHART_FONT_SIZE - 1, rotation=30,
                           ha='right')
        ax.set_ylabel('Utilization Ratio (Demand / Capacity)',
                      fontsize=CHART_FONT_SIZE)
        ax.set_title('Overall Utilization Ratio Summary',
                     fontsize=CHART_TITLE_SIZE, fontweight='bold', pad=12)
        ax.legend(loc='upper right', fontsize=CHART_FONT_SIZE - 1)
        ax.set_ylim(0, max(max(values) * 1.25, 1.3))
        ax.tick_params(axis='both', labelsize=CHART_FONT_SIZE - 1)

        plt.tight_layout()
        path = os.path.join(save_dir, 'ur_summary_chart.png')
        fig.savefig(path, dpi=CHART_DPI, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        logger.info("UR summary chart saved: %s", path)
        return path

    except Exception as exc:
        logger.warning("Failed to generate UR summary chart: %s", exc, exc_info=True)
        return None


def generate_boq_steel_chart(input_dict, save_dir):
    """
    Generate a bar chart of structural steel tonnage by component.

    Parameters
    ----------
    input_dict : dict
        Must contain BOQ keys (steel_girders_wt_total, bracing_*_wt_total, etc.)
    save_dir : str
        Directory to save the chart PNG.

    Returns
    -------
    str or None
        Absolute path to the saved PNG, or None on failure.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from osdagbridge.core.reports.styles import (
            CHART_DPI, CHART_FIGSIZE, BOQ_STEEL_COLOR,
            CHART_FONT_SIZE, CHART_TITLE_SIZE, CHART_BG_COLOR
        )

        steel_items = [
            ("Steel Girders",             "steel_girders_wt_total"),
            ("CB — Top Chord",            "bracing_top_wt_total"),
            ("CB — Bottom Chord",         "bracing_bot_wt_total"),
            ("CB — Diagonal",             "bracing_diag_wt_total"),
            ("End Diaphragms",            "end_diaphragm_wt_total"),
            ("Shear Stud\nConnectors",    "shear_studs_wt_total"),
        ]

        labels, values = [], []
        for lbl, key in steel_items:
            val = input_dict.get(key)
            if val not in (None, "", "N.A."):
                try:
                    labels.append(lbl)
                    values.append(float(val))
                except (TypeError, ValueError):
                    pass

        if not labels:
            logger.info("No steel BOQ data for chart.")
            return None

        fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
        fig.patch.set_facecolor(CHART_BG_COLOR)
        ax.set_facecolor(CHART_BG_COLOR)

        bars = ax.bar(labels, values, color=BOQ_STEEL_COLOR,
                      edgecolor='#333333', linewidth=0.5, width=0.55)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{val:.2f}', ha='center', va='bottom',
                    fontsize=CHART_FONT_SIZE - 1, fontweight='bold')

        ax.set_ylabel('Weight (MT)', fontsize=CHART_FONT_SIZE)
        ax.set_title('Structural Steel Quantity by Component',
                     fontsize=CHART_TITLE_SIZE, fontweight='bold', pad=12)
        ax.tick_params(axis='both', labelsize=CHART_FONT_SIZE - 1)
        plt.tight_layout()

        path = os.path.join(save_dir, 'boq_steel_chart.png')
        fig.savefig(path, dpi=CHART_DPI, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        logger.info("BOQ steel chart saved: %s", path)
        return path

    except Exception as exc:
        logger.warning("Failed to generate BOQ steel chart: %s", exc, exc_info=True)
        return None


def generate_boq_concrete_chart(input_dict, save_dir):
    """
    Generate a grouped bar chart: concrete volume (m³) vs rebar weight (MT).

    Parameters
    ----------
    input_dict : dict
        Must contain concrete_deck_vol_total and rebar_deck_wt_total.
    save_dir : str
        Directory to save the chart PNG.

    Returns
    -------
    str or None
        Absolute path to the saved PNG, or None on failure.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from osdagbridge.core.reports.styles import (
            CHART_DPI, CHART_FIGSIZE, BOQ_CONCRETE_COLOR, BOQ_REBAR_COLOR,
            CHART_FONT_SIZE, CHART_TITLE_SIZE, CHART_BG_COLOR
        )

        concrete_vol = input_dict.get("concrete_deck_vol_total")
        rebar_wt     = input_dict.get("rebar_deck_wt_total")

        vals = []
        labels = []
        colors = []
        if concrete_vol not in (None, "", "N.A."):
            try:
                vals.append(float(concrete_vol))
                labels.append("Concrete\nVolume (m³)")
                colors.append(BOQ_CONCRETE_COLOR)
            except (TypeError, ValueError):
                pass
        if rebar_wt not in (None, "", "N.A."):
            try:
                vals.append(float(rebar_wt))
                labels.append("Reinforcement\nSteel (MT)")
                colors.append(BOQ_REBAR_COLOR)
            except (TypeError, ValueError):
                pass

        if not vals:
            logger.info("No concrete/rebar BOQ data for chart.")
            return None

        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor(CHART_BG_COLOR)
        ax.set_facecolor(CHART_BG_COLOR)

        bars = ax.bar(labels, vals, color=colors, edgecolor='#333333',
                      linewidth=0.5, width=0.45)

        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{val:.2f}', ha='center', va='bottom',
                    fontsize=CHART_FONT_SIZE, fontweight='bold')

        ax.set_title('Concrete & Reinforcement Quantities',
                     fontsize=CHART_TITLE_SIZE, fontweight='bold', pad=12)
        ax.set_ylabel('Quantity', fontsize=CHART_FONT_SIZE)
        ax.tick_params(axis='both', labelsize=CHART_FONT_SIZE - 1)
        plt.tight_layout()

        path = os.path.join(save_dir, 'boq_concrete_chart.png')
        fig.savefig(path, dpi=CHART_DPI, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        logger.info("BOQ concrete chart saved: %s", path)
        return path

    except Exception as exc:
        logger.warning("Failed to generate BOQ concrete chart: %s", exc, exc_info=True)
        return None

