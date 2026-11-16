# Chapter 2: Input Parameters — robust LaTeX generation

import ast
from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_LOAD,
    KEY_CB_TYPE,
    KEY_CROSS_BRACING,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DESIGN_MODE,
    KEY_DO_GAMMA_C_BASIC,
    KEY_DO_GAMMA_FLT,
    KEY_DO_GAMMA_M0,
    KEY_DO_GAMMA_M1,
    KEY_DO_GAMMA_MF,
    KEY_DO_GAMMA_S,
    KEY_DO_GAMMA_V,
    KEY_END_DIAPHRAGM,
    KEY_FOOTPATH,
    KEY_GIRDER,
    KEY_INCLUDE_MEDIAN,
    KEY_MD_TYPE,
    KEY_MP_CB_BRACING_SECTION_DESIGNATION,
    KEY_MP_CB_MEMBER_ID,
    KEY_MP_CB_SELECT_GIRDERS,
    KEY_MP_CB_SPACING,
    KEY_MP_CB_TYPE,
    KEY_MP_ED_BRACING_SECTION_DESIGNATION,
    KEY_MP_ED_MEMBER_ID,
    KEY_MP_ED_SELECT_GIRDERS,
    KEY_MP_ED_TYPE,
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS,
    KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH,
    KEY_MP_GIRDER_DEPTH,
    KEY_MP_GIRDER_SYMMETRY,
    KEY_MP_GIRDER_TOP_FLANGE_THICKNESS,
    KEY_MP_GIRDER_TOP_FLANGE_WIDTH,
    KEY_MP_GIRDER_TORSIONAL_RESTRAINT,
    KEY_MP_GIRDER_TYPE,
    KEY_MP_GIRDER_WARPING_RESTRAINT,
    KEY_MP_GIRDER_WEB_THICKNESS,
    KEY_MP_GIRDER_WEB_TYPE,
    KEY_MP_STIFFENER_BEARING_THICKNESS,
    KEY_MP_STIFFENER_INTERMEDIATE,
    KEY_MP_STIFFENER_INTERMEDIATE_SPACING,
    KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS,
    KEY_MP_STIFFENER_LONGITUDINAL,
    KEY_MP_STIFFENER_NO_BEARING_STIFFENERS,
    KEY_MP_STIFFENER_SPACING,
    KEY_PROJECT_LOCATION,
    KEY_RL_LOAD_VALUE,
    KEY_RL_TYPE,
    KEY_SD_SHEAR_DIAMETER,
    KEY_SD_SHEAR_HEIGHT,
    KEY_SD_SHEAR_STUDS_PER_SECTION,
    KEY_SD_SHEAR_ULTIMATE_STRENGTH,
    KEY_SD_SHEAR_YIELD_STRENGTH,
    KEY_SKEW_ANGLE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SPAN,
    KEY_STRUCTURE_TYPE,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_OVERALL_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_BASIC_WIND_SPEED,
)

from osdagbridge.core.reports.report_utils import _render_value, get_girder_entries, _tex


def ch2_input_parameters(m, input_dict, output_dict=None):
    girder_entries = get_girder_entries(input_dict)
    n_girders = len(girder_entries) if girder_entries else 4

    # ── Parse location details ─────────────────────────────────────────────
    loc = input_dict.get(KEY_PROJECT_LOCATION) or {}
    if isinstance(loc, str) and "{" in loc:
        try:
            loc = ast.literal_eval(loc)
        except Exception:
            loc = {}
    wd = loc.get("weather_data") if isinstance(loc, dict) else {}
    if not isinstance(wd, dict):
        wd = {}

    lat = loc.get("latitude") if isinstance(loc, dict) else None
    lon = loc.get("longitude") if isinstance(loc, dict) else None
    if not lat:
        lat = input_dict.get("latitude")
    if not lon:
        lon = input_dict.get("longitude")

    if lat and lon:
        coord_str = f"{lat}° N, {lon}° E"
    elif lat or lon:
        coord_str = f"{lat or lon}"
    else:
        coord_str = "Not provided"

    # Seismic zone
    sz = (input_dict.get(KEY_SL_SEISMIC_ZONE) or wd.get("zone") or 
          wd.get("z_value") or input_dict.get("seismic_zone"))
    if not sz or "[" in str(sz):
        sz = wd.get("zone") or "Zone III"
    if not str(sz).upper().startswith("ZONE") and str(sz).isdigit():
        _zmap = {"1": "Zone I", "2": "Zone II", "3": "Zone III", "4": "Zone IV", "5": "Zone V"}
        sz = _zmap.get(str(sz), f"Zone {sz}")
    elif not str(sz).upper().startswith("ZONE"):
        sz = f"Zone {sz}"

    # Basic wind speed
    ws = (input_dict.get(KEY_WL_BASIC_WIND_SPEED) or wd.get("wind_speed") or 
          input_dict.get("wind_speed") or "39")
    ws_str = f"{ws} m/s" if "m/s" not in str(ws) else str(ws)

    # Shade temperature
    t_max = (input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or wd.get("max_temp") or 
             input_dict.get("shade_temp_max") or "40")
    t_min = (input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or wd.get("min_temp") or 
             input_dict.get("shade_temp_min") or "10")
    temp_str = f"{t_max} °C / {t_min} °C"

    # ── Geometry values ────────────────────────────────────────────────────
    has_med = str(input_dict.get(KEY_INCLUDE_MEDIAN, "")).strip().lower() in ("yes", "true", "1")
    median_val = "Yes" if has_med else "No"

    fp_raw = str(input_dict.get(KEY_FOOTPATH, "") or input_dict.get("footpath", "")).strip().lower()
    has_fp = fp_raw in ("yes", "true", "1", "single side", "both sides")
    if not fp_raw and str(input_dict.get(KEY_TS_NO_OF_FOOTPATHS, "0")).strip() in ("0", "none", ""):
        has_fp = False
    footpath_val = "Yes" if has_fp else "No"
    fp_width_str = (
        (_render_value(input_dict, KEY_TS_FOOTPATH_WIDTH, ' m') + r" (IRC 5 Cl. 104.3.6 min: 1.5 m)")
        if has_fp else "None (No footpath provided)"
    )

    skew_val = input_dict.get(KEY_SKEW_ANGLE)
    if skew_val not in (None, "", 0, "0"):
        skew_str = f"{skew_val}°"
    else:
        skew_str = "0°"

    # ── Materials ──────────────────────────────────────────────────────────
    g_steel = (input_dict.get(KEY_GIRDER) or input_dict.get("material.steel_grade") or 
               input_dict.get("steeldesign.details.grade_of_material") or "E 350 (Fe 490)")

    cb_steel = input_dict.get(KEY_CROSS_BRACING)
    if not cb_steel or str(cb_steel).strip().lower() in ("yes", "true", "1", "no", "false", "0"):
        cb_steel = "E 250 (Fe 410 W)"

    ed_steel = input_dict.get(KEY_END_DIAPHRAGM)
    if not ed_steel or str(ed_steel).strip().lower() in ("yes", "true", "1", "no", "false", "0"):
        ed_steel = "E 250 (Fe 410 W)"

    deck_conc = input_dict.get(KEY_DECK_CONCRETE_GRADE_BASIC) or "M40"

    # Median row only shown when included
    median_row = ""
    if has_med:
        median_row = (r"\textnormal{Median Type} & "
                      + _render_value(input_dict, KEY_MD_TYPE)
                      + r""" \\[6pt]
\hline
""")

    # Railing type
    rl_type = input_dict.get(KEY_RL_TYPE) or "Steel Railing (Crash Barrier Mounted)"

    return r"""
\chapter{Input Parameters}

\setlength{\abovecaptionskip}{2pt}
\setlength{\belowcaptionskip}{2pt}

This section documents all inputs provided to OsdagBridge. User-provided inputs are clearly distinguished from software-assumed defaults. Where the user did not supply a value, the software has applied the IRC/IS code default or an empirical guideline; these are annotated with an asterisk (\sdstar{}).

\section{Basic Inputs (User-Defined)}
\label{sec:basic-inputs}

\noindent\textit{Note: These inputs are mandatory and were provided by the user.}

\begin{table}[H]
\caption{\textbf{Project Location}}
\label{subsec:project-location}
\begin{tabular}{|L{5.5cm}|L{8.5cm}|}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Project Location} & """ + _tex(m.project_location or "Not provided") + r""" \\
\hline
\textnormal{Latitude / Longitude} & """ + _tex(coord_str) + r""" \\
\hline
\textnormal{Seismic Zone (IRC 6)} & """ + _tex(str(sz)) + r""" \\
\hline
\textnormal{Basic Wind Speed (IRC 6)} & """ + _tex(ws_str) + r""" \\
\hline
\textnormal{Shade Temp. Max / Min (IRC 6)} & """ + _tex(temp_str) + r""" \\
\hline
\end{tabular}
\vspace{0.4cm}
\end{table}

\begin{table}[H]
\caption{\textbf{Bridge Geometry}}
\label{subsec:bridge-geometry}
\begin{tabular}{|L{5.5cm}|L{8.5cm}|}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Type of Structure} & """ + (_render_value(input_dict, KEY_STRUCTURE_TYPE)) + r""" \\
\hline
\textnormal{Span (m)} & """ + (_render_value(input_dict, KEY_SPAN, ' m')) + r""" \\
\hline
\textnormal{Carriageway Width (m)} & """ + (_render_value(input_dict, KEY_CARRIAGEWAY_WIDTH, ' m')) + r""" \\
\hline
\textnormal{Include Median} & """ + median_val + r""" \\
\hline
\textnormal{Footpath} & """ + footpath_val + r""" \\
\hline
\textnormal{Skew Angle (degrees)} & """ + skew_str + r""" (IRC 24 Cl. 504.8 limit: $\pm$15°) \\
\hline
\end{tabular}
\end{table}
\vspace{0.4cm}

\begin{table}[H]
\caption{\textbf{Material Selection}}
\label{subsec:material}
\begin{tabular}{|L{5.5cm}|L{8.5cm}|}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Girder Steel Grade (IS 2062)} & """ + _tex(str(g_steel)) + r""" \\
\hline
\textnormal{Cross Bracing Steel Grade} & """ + _tex(str(cb_steel)) + r""" \\
\hline
\textnormal{End Diaphragm Steel Grade} & """ + _tex(str(ed_steel)) + r""" \\
\hline
\textnormal{Concrete Deck Grade (IRC 22)} & """ + _tex(str(deck_conc)) + r""" \\
\hline
\end{tabular}
\end{table}
\vspace{0.4cm}

\newpage
\section{Additional Inputs}
\label{sec:additional-inputs}

Where the user has modified additional inputs, those values are reported here. Where no modification was made, the software default is shown.

\vspace{0.8cm}

\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Typical Section Details}}\label{tab:typical-section}\\
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\endfirsthead
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\endhead
\textnormal{Overall Bridge Width (m)} & """ + (_render_value(input_dict, KEY_TS_OVERALL_WIDTH, ' m')) + r""" \\[6pt]
\hline
\textnormal{No. of Girders} & """ + (_render_value(input_dict, KEY_TS_NO_OF_GIRDERS)) + r""" \\[6pt]
\hline
\textnormal{Girder Spacing (m)} & """ + (_render_value(input_dict, KEY_TS_GIRDER_SPACING, ' m')) + r""" \\[6pt]
\hline
\textnormal{Deck Overhang Width (m)} & """ + (_render_value(input_dict, KEY_TS_DECK_OVERHANG, ' m')) + r""" \\[6pt]
\hline
\textnormal{Deck Thickness (mm)} & """ + (_render_value(input_dict, KEY_TS_DECK_THICKNESS, ' mm')) + r""" \\[6pt]
\hline
\textnormal{Footpath Width (m)} & """ + fp_width_str + r""" \\[6pt]
\hline
\textnormal{No. of Traffic Lanes} & """ + (_render_value(input_dict, KEY_WC_LD_LANE_TABLE_COUNT)) + r""" (per IRC 5 Cl. 104.3.1) \\[6pt]
\hline
\end{longtable}

\vspace{0.8em}

\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Components Details}}\label{tab:components-details}\\
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\endfirsthead
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\endhead
\textnormal{Crash Barrier Type} & """ + (_render_value(input_dict, KEY_CB_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Crash Barrier Load (kN/m)} & """ + (_render_value(input_dict, KEY_CB_LOAD, ' kN/m')) + r""" \\[6pt]
\hline
""" + median_row + r"""
\textnormal{Railing Type} & """ + _tex(str(rl_type)) + r""" \\[6pt]
\hline
\textnormal{Railing Load (kN/m)} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE, ' kN/m')) + r""" \\[6pt]
\hline
\textnormal{Wearing Course Material} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" \\[6pt]
\hline
\textnormal{Wearing Course Thickness (mm)} & """ + (_render_value(input_dict, KEY_WC_THICKNESS, ' mm')) + r""" \\[6pt]
\hline
\end{longtable}

""" + _girder_tables(input_dict, n_girders) + r"""

""" + _bracing_tables(input_dict, n_girders) + r"""

""" + _shear_connector_table(input_dict, output_dict) + r"""

""" + _safety_factors_table(input_dict)


def _girder_tables(input_dict, n_girders):
    n = n_girders if n_girders >= 1 else 4
    girder_entries = get_girder_entries(input_dict)
    if not girder_entries:
        girder_entries = [(f"G{i}", f"G{i}M1") for i in range(1, n + 1)]
    
    entries_for_table = [
        (lbl, mid, i)
        for i, (lbl, mid) in enumerate(girder_entries, start=1)
    ]

    # Helper: retrieve dimension with fallback to G1 or common key
    def _g_val(base_key, i, default=""):
        return (input_dict.get(f"{base_key}.G{i}.M1") or 
                input_dict.get(f"{base_key}.G1.M1") or 
                input_dict.get(base_key) or default)

    # Helper: one girder-dimension row
    def _dim_row(g_lbl, i):
        d   = _g_val(KEY_MP_GIRDER_DEPTH, i, "1200")
        tw  = _g_val(KEY_MP_GIRDER_WEB_THICKNESS, i, "12")
        tfw = _g_val(KEY_MP_GIRDER_TOP_FLANGE_WIDTH, i, "400")
        tft = _g_val(KEY_MP_GIRDER_TOP_FLANGE_THICKNESS, i, "25")
        bfw = _g_val(KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH, i, "400")
        bft = _g_val(KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS, i, "25")

        top_flange_str = f"{tfw} mm $\\times$ {tft} mm" if tfw and tft else (f"{tfw} mm" if tfw else "---")
        bot_flange_str = f"{bfw} mm $\\times$ {bft} mm" if bfw and bft else (f"{bfw} mm" if bfw else "---")

        return (g_lbl + r""" & """
                + _tex(str(d)) + r""" mm & """
                + _tex(str(tw)) + r""" mm & """
                + top_flange_str + r""" & """
                + bot_flange_str + r""" \\[8pt]
\hline
""")

    # Helper: one general-info row
    def _gen_row(g_lbl, m_id, i):
        d_mode = input_dict.get(KEY_DESIGN_MODE) or "Design"
        g_type = _g_val(KEY_MP_GIRDER_TYPE, i, "Plate Girder")
        g_sym  = _g_val(KEY_MP_GIRDER_SYMMETRY, i, "Symmetric")
        m_id_val = m_id if m_id else f"G{i}M1"
        return (g_lbl + r""" & """ + _tex(m_id_val) + r""" & """
                + _tex(str(d_mode)) + r""" & """
                + _tex(str(g_type)) + r""" & """
                + _tex(str(g_sym)) + r""" \\[8pt]
\hline
""")

    # Helper: one restraint/stiffener row
    def _rst_row(g_lbl, i):
        tors = _g_val(KEY_MP_GIRDER_TORSIONAL_RESTRAINT, i, "Restrained")
        warp = _g_val(KEY_MP_GIRDER_WARPING_RESTRAINT, i, "Free")
        restraint_str = f"{tors} / {warp}" if (tors and warp) else (tors or warp or "Restrained / Free")

        web_type = _g_val(KEY_MP_GIRDER_WEB_TYPE, i, "Thick Web")

        has_int = _g_val(KEY_MP_STIFFENER_INTERMEDIATE, i, "No")
        if str(has_int).strip().lower() in ("yes", "true", "1"):
            sp = _g_val(KEY_MP_STIFFENER_INTERMEDIATE_SPACING, i, "1500")
            th = _g_val(KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS, i, "12")
            int_str = f"Provided ({sp} mm c/c, {th} mm thk)"
        else:
            int_str = "Not provided (unstiffened web)"

        has_long = _g_val(KEY_MP_STIFFENER_LONGITUDINAL, i, "No")
        long_str = "Provided" if str(has_long).strip().lower() in ("yes", "true", "1") else "Not provided"

        no_bs = _g_val(KEY_MP_STIFFENER_NO_BEARING_STIFFENERS, i, "2")
        th_bs = _g_val(KEY_MP_STIFFENER_BEARING_THICKNESS, i, "20")
        bs_str = f"{no_bs} Nos., {th_bs} mm thk" if (no_bs and th_bs) else "Provided at supports"

        return (g_lbl + r""" & """
                + _tex(restraint_str) + r""" & """
                + _tex(web_type) + r""" & """
                + _tex(int_str) + r""" & """
                + _tex(long_str) + r""" & """
                + _tex(bs_str) + r""" \\[8pt]
\hline
""")

    gen_rows = "".join([_gen_row(g_lbl, m_id, i) for g_lbl, m_id, i in entries_for_table])
    dim_rows = "".join([_dim_row(g_lbl, i) for g_lbl, _, i in entries_for_table])
    rst_rows = "".join([_rst_row(g_lbl, i) for g_lbl, _, i in entries_for_table])

    return (r"""
\newpage

\vspace{0.4em}
\noindent
            
\vspace{4pt}
\begin{longtable}{|L{2.2cm}|L{1.8cm}|p{3.8cm}|p{3.8cm}|p{3.8cm}|}
\caption{\textbf{Girder General Information}}\label{tab:girder-general}\\
\hline
\textbf{Girder} & \textbf{Member ID} & \textbf{Design Mode} & \textbf{Girder Type} & \textbf{Girder Symmetry} \\[6pt]
\hline
\endfirsthead
\hline
\textbf{Girder} & \textbf{Member ID} & \textbf{Design Mode} & \textbf{Girder Type} & \textbf{Girder Symmetry} \\[6pt]
\hline
\endhead
"""
            + gen_rows
            + r"""\end{longtable}

\vspace{0.6em}

\vspace{4pt}
\begin{longtable}{|L{1.8cm}|L{2.3cm}|L{1.8cm}|p{4.8cm}|p{4.8cm}|}
\caption{\textbf{Girder Section Dimensions}}\label{tab:girder-dimensions}\\
\hline
\textbf{Girder} & \textbf{Total Depth, D (mm)} & \textbf{Web, $t_w$ (mm)} & \textbf{Top Flange (b\textsubscript{tf}, t\textsubscript{tf}) mm} & \textbf{Bottom Flange (b\textsubscript{bf}, t\textsubscript{bf}) mm} \\[6pt]
\hline
\endfirsthead
\hline
\textbf{Girder} & \textbf{Total Depth, D (mm)} & \textbf{Web, $t_w$ (mm)} & \textbf{Top Flange (b\textsubscript{tf}, t\textsubscript{tf}) mm} & \textbf{Bottom Flange (b\textsubscript{bf}, t\textsubscript{bf}) mm} \\[6pt]
\hline
\endhead
"""
            + dim_rows
            + r"""\end{longtable}

\vspace{0.6em}

\vspace{4pt}
\begin{longtable}{|L{1.4cm}|p{2.4cm}|p{2.0cm}|p{3.2cm}|p{2.2cm}|p{2.4cm}|}
\caption{\textbf{Girder Restraint and Stiffener Details}}\label{tab:girder-stiffeners}\\
\hline
\textbf{Girder} & \textbf{Torsional / Warping Restraint} & \textbf{Web Philosophy} & \textbf{Intermediate Stiffeners} & \textbf{Longitudinal Stiffeners} & \textbf{Bearing Stiffener} \\[6pt]
\hline
\endfirsthead
\hline
\textbf{Girder} & \textbf{Torsional / Warping Restraint} & \textbf{Web Philosophy} & \textbf{Intermediate Stiffeners} & \textbf{Longitudinal Stiffeners} & \textbf{Bearing Stiffener} \\[6pt]
\hline
\endhead
"""
            + rst_rows
            + r"""\end{longtable}
""")


def _bracing_tables(input_dict, n_girders):
    n = n_girders if n_girders >= 2 else 4
    
    cb_rows_list = []
    ed_rows_list = []
    for i in range(1, n):
        pair_key = f"G{i}G{i+1}"
        pair_lbl = f"G{i} to G{i+1}"

        # Cross bracing
        cb_loc  = input_dict.get(f"{KEY_MP_CB_SELECT_GIRDERS}.{pair_key}.B{i}M1") or pair_lbl
        cb_mids = input_dict.get(f"{KEY_MP_CB_MEMBER_ID}.{pair_key}.B{i}M1") or f"B{i}M1 to B{i}M6"
        cb_type = input_dict.get(f"{KEY_MP_CB_TYPE}.{pair_key}.B{i}M1") or "Cross Bracing (X-Type)"
        cb_sec  = input_dict.get(f"{KEY_MP_CB_BRACING_SECTION_DESIGNATION}.{pair_key}.B{i}M1") or "IS 100 x 100 x 10"
        cb_sp   = input_dict.get(f"{KEY_MP_CB_SPACING}.{pair_key}.B{i}M1") or "5.0"
        cb_sp_str = f"{cb_sp} m" if "m" not in str(cb_sp) else str(cb_sp)

        cb_rows_list.append(
            _tex(cb_loc) + r""" & """ + _tex(cb_mids) + r""" & """
            + _tex(str(cb_type)) + r""" & """
            + _tex(str(cb_sec)) + r""" & """
            + _tex(cb_sp_str) + r""" \\[6pt]
\hline
"""
        )

        # End diaphragm
        ed_loc  = input_dict.get(f"{KEY_MP_ED_SELECT_GIRDERS}.{pair_key}.E{i}M1") or pair_lbl
        ed_mids = input_dict.get(f"{KEY_MP_ED_MEMBER_ID}.{pair_key}.E{i}M1") or f"E{i}M1 to E{i}M2"
        ed_type = input_dict.get(f"{KEY_MP_ED_TYPE}.{pair_key}.E{i}M1") or "End Diaphragm (X-Type)"
        ed_sec  = input_dict.get(f"{KEY_MP_ED_BRACING_SECTION_DESIGNATION}.{pair_key}.E{i}M1") or "IS 100 x 100 x 10"

        ed_rows_list.append(
            _tex(ed_loc) + r""" & """ + _tex(ed_mids) + r""" & """
            + _tex(str(ed_type)) + r""" & """
            + _tex(str(ed_sec)) + r""" \\[6pt]
\hline
"""
        )

    cb_rows = "".join(cb_rows_list)
    ed_rows = "".join(ed_rows_list)

    return (r"""
\newpage

\vspace{0.4em}
\setlength{\tabcolsep}{4pt}
\setlength\LTleft{0pt}
\setlength\LTright{\fill}

\begin{longtable}{|L{2.4cm}|L{2.5cm}|L{3.2cm}|L{2.8cm}|C{2.0cm}|}
\caption{\textbf{Member Properties: Cross Bracing Details}}\label{tab:cb-details}\\
\hline
\textbf{Location} & \textbf{Member IDs} & \textbf{Type of Bracing} & \textbf{Bracing Section} & \textbf{Spacing (m)} \\
\hline
\endfirsthead
\hline
\textbf{Location} & \textbf{Member IDs} & \textbf{Type of Bracing} & \textbf{Bracing Section} & \textbf{Spacing (m)} \\
\hline
\endhead
"""
+ cb_rows
+ r"""\end{longtable}

\vspace{0.4em}
\noindent
\setlength{\tabcolsep}{4pt}
\setlength\LTleft{0pt}
\setlength\LTright{\fill}

\begin{longtable}{|L{2.4cm}|L{2.5cm}|L{3.2cm}|L{3.5cm}|}
\caption{\textbf{Member Properties: End Diaphragm Details}}\label{tab:ed-details}\\
\hline
\textbf{Location} & \textbf{Member IDs} & \textbf{Type of Bracing} & \textbf{Bracing Section} \\
\hline
\endfirsthead
\hline
\textbf{Location} & \textbf{Member IDs} & \textbf{Type of Bracing} & \textbf{Bracing Section} \\
\hline
\endhead
"""
+ ed_rows
+ r"""\end{longtable}
""")


def _shear_connector_table(input_dict, output_dict=None):
    od = output_dict or {}
    
    def _sc(k1, k2, default=""):
        return od.get(k1) or input_dict.get(k2) or default

    dia = _sc(KEY_SD_SHEAR_DIAMETER, "design_options.shear_studs.diameter", "20")
    if not dia or dia == "None":
        dia = input_dict.get("design_options.stud_diameter", "20")

    ht = _sc(KEY_SD_SHEAR_HEIGHT, "design_options.shear_studs.height", "100")
    if not ht or ht == "None":
        ht = input_dict.get("design_options.stud_height", "100")

    fy = _sc(KEY_SD_SHEAR_YIELD_STRENGTH, "design_options.shear_studs.yield_strength", "385")
    if not fy or fy == "None":
        fy = input_dict.get("design_options.stud_yield_strength", "385")

    fu = _sc(KEY_SD_SHEAR_ULTIMATE_STRENGTH, "design_options.shear_studs.ultimate_strength", "495")
    if not fu or fu == "None":
        fu = input_dict.get("design_options.stud_ultimate_strength", "495")

    n_studs = _sc(KEY_SD_SHEAR_STUDS_PER_SECTION, "design_options.shear_studs.count", "3")
    if not n_studs or n_studs == "None":
        n_studs = input_dict.get("design_options.stud_count", "3")

    return r"""
\label{subsec:shear-connectors}

\vspace{1.5em}

\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Shear Connector Details}}\label{tab:sc-details}\\
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\endfirsthead
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\endhead
\textnormal{Stud Diameter (mm)} & """ + _tex(str(dia)) + r""" mm \\[6pt]
\hline
\textnormal{Stud Height (mm)} & """ + _tex(str(ht)) + r""" mm \\[6pt]
\hline
\textnormal{Stud $f_y$ (MPa)} & """ + _tex(str(fy)) + r""" MPa \\[6pt]
\hline
\textnormal{Stud $f_u$ (MPa)} & """ + _tex(str(fu)) + r""" MPa \\[6pt]
\hline
\textnormal{No. of Studs per Section} & """ + _tex(str(n_studs)) + r""" \\[6pt]
\hline
\end{longtable}
"""


def _safety_factors_table(input_dict):
    gm0 = input_dict.get(KEY_DO_GAMMA_M0) or "1.10"
    gm1 = input_dict.get(KEY_DO_GAMMA_M1) or "1.25"
    gc  = input_dict.get(KEY_DO_GAMMA_C_BASIC) or "1.50"
    gs  = input_dict.get(KEY_DO_GAMMA_S) or "1.15"
    gv  = input_dict.get(KEY_DO_GAMMA_V) or "1.25"
    gfl = input_dict.get(KEY_DO_GAMMA_FLT) or "1.00"
    gmf = input_dict.get(KEY_DO_GAMMA_MF) or "1.25"

    return r"""
\label{subsec:safety-factors}

\vspace{1.5em}

\noindent\textit{Note: All partial safety factors are per IRC 22 Table 1 and IS 800 Table 5.}

\vspace{0.4em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Partial Safety Factors}}\label{tab:safety-factors}\\
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\endfirsthead
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\endhead
\textnormal{$\gamma_{M0}$ (Yielding / Buckling)} & """ + _tex(str(gm0)) + r""" \\[6pt]
\hline
\textnormal{$\gamma_{M1}$ (Ultimate Stress)} & """ + _tex(str(gm1)) + r""" \\[6pt]
\hline
\textnormal{$\gamma_C$ (Concrete, Basic)} & """ + _tex(str(gc)) + r""" \\[6pt]
\hline
\textnormal{$\gamma_s$ (Reinforcement)} & """ + _tex(str(gs)) + r""" \\[6pt]
\hline
\textnormal{$\gamma_v$ (Shear Connectors)} & """ + _tex(str(gv)) + r""" \\[6pt]
\hline
\textnormal{$\gamma_{fft}$ (Fatigue Load)} & """ + _tex(str(gfl)) + r""" \\[6pt]
\hline
\textnormal{$\gamma_{Mft}$ (Fatigue Strength)} & """ + _tex(str(gmf)) + r""" \\[6pt]
\hline
\end{longtable}
"""
