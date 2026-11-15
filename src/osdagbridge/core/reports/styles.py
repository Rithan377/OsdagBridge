# =============================================================================
# styles.py — Centralized Formatting Module for OsdagBridge Reports
# Single source of truth for all LaTeX formatting parameters.
# =============================================================================

"""
Centralized formatting constants and helpers for the OsdagBridge LaTeX report.

All colors, geometry, table styling, fonts, margins, and header/footer
definitions are collected here so that chapter files and the main
report_generator can import a single module instead of scattering
formatting across dozens of files.
"""

# ─────────────────────────────────────────────────────────────────────────────
# COLORS (HTML hex — used in LaTeX via \definecolor)
# ─────────────────────────────────────────────────────────────────────────────

OSDAG_GREEN = "91B014"          # Brand green for rules, headings
PASS_COLOR  = "000000"          # Black text for PASS status
FAIL_COLOR  = "FF0000"          # Red text for FAIL status
HEADER_BG   = "E8F0D8"          # Light green for optional header row backgrounds

# ─────────────────────────────────────────────────────────────────────────────
# GEOMETRY (page layout — passed to \usepackage[...]{geometry})
# ─────────────────────────────────────────────────────────────────────────────

PAGE_TOP_MARGIN    = "25mm"
PAGE_BOTTOM_MARGIN = "28mm"
PAGE_LEFT_MARGIN   = "20mm"
PAGE_RIGHT_MARGIN  = "20mm"
HEAD_HEIGHT        = "16pt"
HEAD_SEP           = "14pt"
FOOT_SKIP          = "18pt"

def geometry_options():
    """Return the LaTeX geometry option string."""
    return (
        f"a4paper, top={PAGE_TOP_MARGIN}, bottom={PAGE_BOTTOM_MARGIN}, "
        f"left={PAGE_LEFT_MARGIN}, right={PAGE_RIGHT_MARGIN}, "
        f"headheight={HEAD_HEIGHT}, headsep={HEAD_SEP}, footskip={FOOT_SKIP}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# TABLE STYLING
# ─────────────────────────────────────────────────────────────────────────────

TABCOLSEP        = "6pt"        # Default horizontal cell padding
ARRAYSTRETCH     = "1.12"       # Default row-height multiplier
LT_PRE           = "0pt"        # Space before longtable
LT_POST          = "6pt"        # Space after longtable
ARRAYRULEWIDTH   = "0.5pt"      # Table rule thickness
EXTRAROWHEIGHT   = "0.6pt"      # Extra vertical padding in rows

# ─────────────────────────────────────────────────────────────────────────────
# FONT / SPACING
# ─────────────────────────────────────────────────────────────────────────────

DOCUMENT_FONT_SIZE = "12pt"
LINE_STRETCH       = "1.15"

# ─────────────────────────────────────────────────────────────────────────────
# HEADER / FOOTER SPACING  (fixes footer overlap — Issue #2)
# ─────────────────────────────────────────────────────────────────────────────

# Positive spacing before the green rule in the footer.
# The original used negative vspace (-20pt / -8pt) which caused text to
# collide with the footer rule.  These positive values keep the content
# safely above.
FOOTER_SD_VSPACE   = "2pt"    # Space above SD asterisk note line
FOOTER_RULE_VSPACE = "6pt"    # Space between footer text and green rule
FOOTER_NO_SD_GAP   = "0pt"   # Space above green rule when no SD on page

# ─────────────────────────────────────────────────────────────────────────────
# LONGTABLE HEADER REPETITION HELPER  (fixes Issue #1)
# ─────────────────────────────────────────────────────────────────────────────

def build_longtable_header(header_row_tex, caption_tex=None, col_spec=None):
    r"""
    Return the LaTeX block that makes a longtable repeat its header row
    on every page using \endfirsthead / \endhead / \endfoot / \endlastfoot.

    Parameters
    ----------
    header_row_tex : str
        The full header row(s) including \\hline and column titles,
        ending with ``\\\\`` and ``\\hline``.
        Example::

            r'\hline\n\\textbf{A} & \\textbf{B} \\\\\n\\hline'

    caption_tex : str or None
        If given, placed before the first-page header as a
        ``\caption{...}`` line.

    col_spec : str or None
        Not used in the output — reserved for possible future
        auto-width helpers.

    Returns
    -------
    str
        A LaTeX fragment to insert right after ``\begin{longtable}{...}``.
    """
    parts = []

    # ── First page header ──
    if caption_tex:
        parts.append(caption_tex)
    parts.append(header_row_tex)
    parts.append(r"\endfirsthead")

    # ── Continuation pages ──
    parts.append(r"\multicolumn{1}{c}{\small\textit{(continued)}} \\")
    parts.append(header_row_tex)
    parts.append(r"\endhead")

    # ── Continuation footer ──
    parts.append(r"\hline")
    parts.append(r"\multicolumn{1}{r}{\small\textit{Continued on next page}} \\")
    parts.append(r"\endfoot")

    # ── Last-page footer ──
    parts.append(r"\hline")
    parts.append(r"\endlastfoot")

    return "\n".join(parts)


def longtable_continuation_header(ncols, header_row_tex, caption_tex=None):
    r"""
    Convenience wrapper: generates \endfirsthead / \endhead / \endfoot /
    \endlastfoot for a longtable with *ncols* columns.

    This version uses the correct ``\multicolumn{<ncols>}`` span for the
    "continued" notes.

    Parameters
    ----------
    ncols : int
        Number of columns in the longtable.
    header_row_tex : str
        Header rows (\\hline … column titles … \\hline).
    caption_tex : str or None
        Optional ``\\caption{…}`` line for the first page.
    """
    parts = []

    # First page
    if caption_tex:
        parts.append(caption_tex)
    parts.append(header_row_tex)
    parts.append(r"\endfirsthead")

    # Continuation pages
    parts.append(
        r"\multicolumn{" + str(ncols) + r"}{c}"
        r"{\small\textit{(Table continued from previous page)}} \\"
    )
    parts.append(header_row_tex)
    parts.append(r"\endhead")

    # Bottom of every page except the last
    parts.append(r"\hline")
    parts.append(
        r"\multicolumn{" + str(ncols) + r"}{r}"
        r"{\small\textit{Continued on next page}} \\"
    )
    parts.append(r"\endfoot")

    # Bottom of the last page
    parts.append(r"\hline")
    parts.append(r"\endlastfoot")

    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# CHART STYLING (for matplotlib-generated utilization-ratio and BOQ charts)
# ─────────────────────────────────────────────────────────────────────────────

CHART_DPI         = 200
CHART_FIGSIZE     = (8, 4.5)    # (width, height) in inches
CHART_BAR_COLOR   = "#4A90D9"   # Steel blue for bars
CHART_PASS_COLOR  = "#2ECC71"   # Green for passing UR
CHART_FAIL_COLOR  = "#E74C3C"   # Red for failing UR
CHART_THRESHOLD   = 1.0         # UR threshold (dashed red line)
CHART_FONT_SIZE   = 10
CHART_TITLE_SIZE  = 13
CHART_BG_COLOR    = "#FAFAFA"

# BOQ chart colors
BOQ_STEEL_COLOR    = "#4A90D9"
BOQ_CONCRETE_COLOR = "#95A5A6"
BOQ_REBAR_COLOR    = "#E67E22"

