#!/usr/bin/env python3
"""
test_report.py — Headless test script for OsdagBridge report generation.

Constructs a mock ReportPayload with sample bridge data and calls
generate_report() to produce a PDF + .tex without running the GUI or solver.

Usage:
    cd "/home/rithan/iitb OSDAG/OsdagBridge"
    source /home/rithan/iitb\ OSDAG/myenv/bin/activate
    python3 test_report.py [--output-dir DIR] [--stem NAME]
"""

import sys, os, types

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ── Mock unavailable heavy modules ──
for mod_name in [
    'openseespy', 'openseespy.opensees',
    'PySide6', 'PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui',
    'OCC', 'OCC.Core', 'OCC.Core.gp', 'OCC.Core.BRepPrimAPI',
    'OCC.Display', 'OCC.Display.SimpleGui',
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)

from osdagbridge.core.reports.report_generator import (
    ReportMetadata, ReportOptions, ReportRequest, ReportPayload,
    ReportFigures, ReportDataBridge, generate_report
)


def _generate_placeholder_figures(save_dir):
    """Generate simple matplotlib placeholder images for bridge drawings."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    figs = {}

    # Plan view
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 30); ax.set_ylim(0, 10)
    for i in range(4):
        y = 1.5 + i * 2.5
        ax.plot([0, 30], [y, y], 'b-', linewidth=2)
        ax.text(15, y + 0.3, f'Girder G{i+1}', ha='center', fontsize=8, color='blue')
    ax.add_patch(patches.Rectangle((0, 0.5), 30, 9, fill=False, edgecolor='black', linewidth=1.5))
    ax.set_title('Bridge Plan View (30m Span, 4 Girders)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Span (m)'); ax.set_ylabel('Width (m)')
    ax.set_aspect('equal')
    p = os.path.join(save_dir, 'girder_top.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['girder_top'] = p

    # Cross section
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-1, 11); ax.set_ylim(-2, 2)
    ax.add_patch(patches.Rectangle((0, 0), 10, 0.25, facecolor='#C0C0C0', edgecolor='black'))
    ax.text(5, 0.35, 'Concrete Deck Slab (250mm)', ha='center', fontsize=8)
    for i in range(4):
        x = 1.25 + i * 2.5
        ax.plot([x, x], [0, -1.2], 'b-', linewidth=3)
        ax.plot([x - 0.2, x + 0.2], [-1.2, -1.2], 'b-', linewidth=4)
        ax.text(x, -1.5, f'G{i+1}', ha='center', fontsize=8, color='blue')
    ax.add_patch(patches.Rectangle((0, 0.25), 0.5, 0.9, facecolor='#808080', edgecolor='black'))
    ax.add_patch(patches.Rectangle((9.5, 0.25), 0.5, 0.9, facecolor='#808080', edgecolor='black'))
    ax.text(0.25, 0.8, 'CB', ha='center', fontsize=6, color='white')
    ax.text(9.75, 0.8, 'CB', ha='center', fontsize=6, color='white')
    ax.set_title('Typical Cross-Section', fontsize=12, fontweight='bold')
    ax.set_xlabel('Width (m)'); ax.set_ylabel('Depth (m)')
    p = os.path.join(save_dir, 'cross_section.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['cross_section'] = p

    # 3D isometric view (simplified)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    # Draw girders in pseudo-3D
    for i in range(4):
        x_off = i * 1.2
        ax.plot([1 + x_off, 10 + x_off], [2 + i * 0.8, 2 + i * 0.8], 'b-', linewidth=2)
        ax.plot([1 + x_off, 10 + x_off], [3 + i * 0.8, 3 + i * 0.8], 'b-', linewidth=1)
        ax.plot([1 + x_off, 1 + x_off], [2 + i * 0.8, 3 + i * 0.8], 'b-', linewidth=1)
        ax.plot([10 + x_off, 10 + x_off], [2 + i * 0.8, 3 + i * 0.8], 'b-', linewidth=1)
    # Deck
    xs = [1, 10, 10 + 3.6, 1 + 3.6]
    ys = [3.8, 3.8, 6.2, 6.2]
    ax.fill(xs, ys, alpha=0.3, color='gray')
    ax.plot(xs + [xs[0]], ys + [ys[0]], 'k-', linewidth=1.5)
    ax.text(6, 7, '3D View — Steel Plate Girder Bridge', ha='center', fontsize=12, fontweight='bold')
    ax.axis('off')
    p = os.path.join(save_dir, 'final_geometry.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['final_geometry'] = p

    # ── BM Envelope ──
    fig, ax = plt.subplots(figsize=(10, 4))
    x = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
    bm_max = [0, 2100, 3400, 4000, 4200, 4250, 4200, 4000, 3400, 2100, 0]
    bm_min = [0, -150, -80, -30, -10, 0, -10, -30, -80, -150, 0]
    ax.fill_between(x, bm_max, bm_min, alpha=0.3, color='blue')
    ax.plot(x, bm_max, 'b-', linewidth=2, label='Max BM')
    ax.plot(x, bm_min, 'r--', linewidth=1.5, label='Min BM')
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xlabel('Distance from Left Support (m)')
    ax.set_ylabel('Bending Moment (kN-m)')
    ax.set_title('Bending Moment Envelope — ULS', fontweight='bold')
    ax.legend(); ax.grid(True, alpha=0.3)
    p = os.path.join(save_dir, 'bm_envelope.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['bm_envelope'] = p

    # ── SF Envelope ──
    fig, ax = plt.subplots(figsize=(10, 4))
    sf_max = [580, 450, 320, 200, 100, 0, -100, -200, -320, -450, -580]
    sf_min = [320, 240, 160, 80, 20, 0, -20, -80, -160, -240, -320]
    ax.fill_between(x, sf_max, sf_min, alpha=0.3, color='green')
    ax.plot(x, sf_max, 'g-', linewidth=2, label='Max SF')
    ax.plot(x, sf_min, 'r--', linewidth=1.5, label='Min SF')
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xlabel('Distance from Left Support (m)')
    ax.set_ylabel('Shear Force (kN)')
    ax.set_title('Shear Force Envelope — ULS', fontweight='bold')
    ax.legend(); ax.grid(True, alpha=0.3)
    p = os.path.join(save_dir, 'sf_envelope.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['sf_envelope'] = p

    # ── Deflection Diagram ──
    fig, ax = plt.subplots(figsize=(10, 4))
    import numpy as np
    xd = np.linspace(0, 30, 100)
    defl = -12.5 * np.sin(np.pi * xd / 30)
    ax.plot(xd, defl, 'b-', linewidth=2)
    ax.fill_between(xd, defl, 0, alpha=0.15, color='blue')
    ax.axhline(y=-37.5, color='red', linestyle='--', linewidth=1.2, label='L/800 = 37.5 mm')
    ax.set_xlabel('Distance from Left Support (m)')
    ax.set_ylabel('Vertical Deflection (mm)')
    ax.set_title('Vertical Deflection — 1.0 LL', fontweight='bold')
    ax.legend(); ax.grid(True, alpha=0.3)
    ax.invert_yaxis()
    p = os.path.join(save_dir, 'defl_ll.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['defl_ll'] = p

    # ── 3D View of Plate Girders (Fig 6.4) ──
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-1, 35); ax.set_ylim(-3, 12)
    for i in range(4):
        z = i * 2.5
        ax.plot([0 + i*1.2, 30 + i*1.2], [z + 1.2, z + 1.2], '#2060A0', lw=2.5)
        ax.plot([0 + i*1.2, 30 + i*1.2], [z, z], '#2060A0', lw=1.5)
        ax.plot([0 + i*1.2, 30 + i*1.2], [z - 1.2, z - 1.2], '#2060A0', lw=2.5)
        for sx in range(0, 31, 5):
            ax.plot([sx + i*1.2, sx + i*1.2], [z - 1.2, z + 1.2], '#A0A0A0', lw=1)
        ax.text(15 + i*1.2, z + 1.6, f'Girder G{i+1}', ha='center', fontsize=8, color='#2060A0')
    ax.set_title('3D View of Steel Plate Girders', fontsize=12, fontweight='bold')
    ax.axis('off')
    p = os.path.join(save_dir, 'girder_3d.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['girder_3d'] = p

    # ── Cross Section of Plate Girder (Fig 6.5) ──
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(-300, 300); ax.set_ylim(-750, 800)
    ax.add_patch(patches.Rectangle((-200, 575), 400, 25, facecolor='#2060A0', edgecolor='black', lw=1.5))
    ax.add_patch(patches.Rectangle((-200, -600), 400, 25, facecolor='#2060A0', edgecolor='black', lw=1.5))
    ax.add_patch(patches.Rectangle((-6, -575), 12, 1150, facecolor='#6090D0', edgecolor='black', lw=1.2))
    for sx in [-75, 75]:
        ax.add_patch(patches.Rectangle((sx-11, 600), 22, 100, facecolor='#FFA500', edgecolor='black', lw=1))
        ax.add_patch(patches.Circle((sx, 700), 16, facecolor='#FFA500', edgecolor='black', lw=1))
    ax.text(0, 730, 'Shear Studs (2 nos. \u03c622)', ha='center', fontsize=8, fontweight='bold')
    ax.annotate('Top Flange: 400 \u00d7 25 mm', xy=(200, 587.5), xytext=(220, 600),
                arrowprops=dict(arrowstyle='->', color='black'), fontsize=8)
    ax.annotate('Web: 1150 \u00d7 12 mm', xy=(6, 0), xytext=(40, 0),
                arrowprops=dict(arrowstyle='->', color='black'), fontsize=8)
    ax.annotate('Bottom Flange: 400 \u00d7 25 mm', xy=(200, -587.5), xytext=(220, -580),
                arrowprops=dict(arrowstyle='->', color='black'), fontsize=8)
    ax.annotate('', xy=(-240, -600), xytext=(-240, 600), arrowprops=dict(arrowstyle='<->', color='black'))
    ax.text(-260, 0, 'D = 1200 mm', va='center', ha='right', fontsize=9, rotation=90)
    ax.set_title('Cross Section of Plate Girder', fontsize=12, fontweight='bold')
    ax.axis('off'); ax.set_aspect('equal')
    p = os.path.join(save_dir, 'section_preview.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['section_preview'] = p

    # ── Side View of Girder / Stiffeners (Fig 6.6) ──
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(-1, 31); ax.set_ylim(-2, 2.5)
    ax.add_patch(patches.Rectangle((0, -0.6), 30, 1.2, facecolor='#D4E6FF', edgecolor='#2060A0', linewidth=1.5))
    ax.add_patch(patches.Rectangle((-0.05, 0.6), 30.1, 0.15, facecolor='#2060A0', edgecolor='black', linewidth=1))
    ax.add_patch(patches.Rectangle((-0.05, -0.75), 30.1, 0.15, facecolor='#2060A0', edgecolor='black', linewidth=1))
    for sx in range(0, 31, 3):
        ax.plot([sx, sx], [-0.6, 0.6], color='#808080', linewidth=1, linestyle='-')
    for sx in [0, 30]:
        ax.add_patch(patches.Rectangle((sx-0.15, -0.75), 0.3, 1.5, facecolor='#FF8C00', edgecolor='black', linewidth=1.5))
    ax.annotate('', xy=(0, -1.1), xytext=(30, -1.1), arrowprops=dict(arrowstyle='<->', color='black'))
    ax.text(15, -1.3, 'Span: 30,000 mm (Intermediate stiffeners @ 1500 mm)', ha='center', fontsize=9)
    ax.set_title('Side View of Girder (Stiffener Layout)', fontsize=12, fontweight='bold')
    ax.axis('off')
    p = os.path.join(save_dir, 'stiffener_preview.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['stiffener_preview'] = p

    # ── Cross-Bracing Layout (Fig 6.7) ──
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(-0.5, 3); ax.set_ylim(-1.5, 1.5)
    for gx in [0, 2.5]:
        ax.add_patch(patches.Rectangle((gx-0.08, -1.2), 0.16, 2.4, facecolor='#2060A0', edgecolor='black'))
    ax.plot([0, 2.5], [1.0, 1.0], 'g-', linewidth=3, label='Top Chord (ISA 100\u00d7100\u00d710)')
    ax.plot([0, 2.5], [-1.0, -1.0], 'g-', linewidth=3, label='Bottom Chord (ISA 100\u00d7100\u00d710)')
    ax.plot([0, 2.5], [-1.0, 1.0], 'r-', linewidth=2.5, label='Diagonal (ISA 100\u00d7100\u00d710)')
    ax.plot([0, 2.5], [1.0, -1.0], 'r-', linewidth=2.5)
    ax.text(0, 1.3, 'G1', ha='center', fontweight='bold', fontsize=10)
    ax.text(2.5, 1.3, 'G2', ha='center', fontweight='bold', fontsize=10)
    ax.set_title('Cross-Bracing Layout (X-Type)', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', fontsize=8)
    ax.axis('off'); ax.set_aspect('equal')
    p = os.path.join(save_dir, 'cb_diagram.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['cb_diagram'] = p

    # ── Cross Bracing Sections: Bracing, Top Chord, Bottom Chord (Figs 6.8, 6.9, 6.10) ──
    for sec_name, title, fname in [
        ('cb_bracing', 'Bracing Section', 'cb_bracing.png'),
        ('cb_top_chord', 'Top Chord Section', 'cb_top_chord.png'),
        ('cb_bottom_chord', 'Bottom Chord Section', 'cb_bottom_chord.png'),
    ]:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.set_xlim(-20, 120); ax.set_ylim(-20, 120)
        ax.add_patch(patches.Rectangle((0, 0), 10, 100, facecolor='#2060A0', edgecolor='black', lw=1.5))
        ax.add_patch(patches.Rectangle((0, 0), 100, 10, facecolor='#2060A0', edgecolor='black', lw=1.5))
        ax.text(50, 15, '100 mm', ha='center', fontsize=8)
        ax.text(15, 50, '100 mm', va='center', rotation=90, fontsize=8)
        ax.text(50, -15, 'ISA 100 \u00d7 100 \u00d7 10', ha='center', fontsize=9, fontweight='bold')
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.axis('off'); ax.set_aspect('equal')
        p = os.path.join(save_dir, fname)
        fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
        figs[sec_name] = p

    # ── End Diaphragm Layout (Fig 6.11) ──
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(-0.5, 3); ax.set_ylim(-1.5, 1.5)
    for gx in [0, 2.5]:
        ax.add_patch(patches.Rectangle((gx-0.08, -1.2), 0.16, 2.4, facecolor='#2060A0', edgecolor='black'))
    ax.plot([0, 2.5], [0.8, 0.8], 'g-', linewidth=3, label='Top Chord')
    ax.plot([0, 2.5], [-0.8, -0.8], 'g-', linewidth=3, label='Bottom Chord')
    ax.plot([0, 2.5], [-0.8, 0.8], 'r-', linewidth=2.5, label='Diagonal')
    ax.plot([0, 2.5], [0.8, -0.8], 'r-', linewidth=2.5)
    ax.text(0, 1.1, 'G1', ha='center', fontweight='bold', fontsize=10)
    ax.text(2.5, 1.1, 'G2', ha='center', fontweight='bold', fontsize=10)
    ax.text(1.25, -1.3, 'End Diaphragm at Bearing', ha='center', fontsize=9, style='italic')
    ax.set_title('End Diaphragm Layout (X-Type)', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', fontsize=8)
    ax.axis('off'); ax.set_aspect('equal')
    p = os.path.join(save_dir, 'ed_diagram.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
    figs['ed_diagram'] = p

    # ── End Diaphragm Sections (Figs 6.12, 6.13, 6.14) ──
    for sec_name, title, fname in [
        ('ed_bracing', 'ED Bracing Section', 'ed_bracing.png'),
        ('ed_top_chord', 'ED Top Chord Section', 'ed_top_chord.png'),
        ('ed_bottom_chord', 'ED Bottom Chord Section', 'ed_bottom_chord.png'),
    ]:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.set_xlim(-20, 120); ax.set_ylim(-20, 120)
        ax.add_patch(patches.Rectangle((0, 0), 10, 100, facecolor='#2060A0', edgecolor='black', lw=1.5))
        ax.add_patch(patches.Rectangle((0, 0), 100, 10, facecolor='#2060A0', edgecolor='black', lw=1.5))
        ax.text(50, 15, '100 mm', ha='center', fontsize=8)
        ax.text(15, 50, '100 mm', va='center', rotation=90, fontsize=8)
        ax.text(50, -15, 'ISA 100 \u00d7 100 \u00d7 10', ha='center', fontsize=9, fontweight='bold')
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.axis('off'); ax.set_aspect('equal')
        p = os.path.join(save_dir, fname)
        fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(fig)
        figs[sec_name] = p

    return figs


def build_mock_payload():
    """Create a ReportPayload with realistic sample data for all 9 chapters."""

    metadata = ReportMetadata(
        project_name="Sample Bridge Project — NH48 ROB",
        project_location="Pune, Maharashtra",
        designer="Eng. Test User",
        client="NHAI — National Highways Authority of India",
        company="IIT Bombay — FOSSEE Project",
        group_name="Structural Engineering",
        subtitle="Rev 0",
        job_number="OSDAG-2025-001",
        additional_comments="Test report generated headlessly",
        logo_path=None,
        report_date="2025-11-16",
        reviewer="Dr. Reviewer"
    )

    options = ReportOptions(
        sections=['loads', 'analysis', 'design_checks', 'drawings'],
        include_figures=True,
        include_toc=True,
        include_pdf=True
    )

    # ── input_dict uses the EXACT key strings from common.py ──
    input_dict = {
        # Project info (KEY_STRUCTURE_TYPE, KEY_SPAN, KEY_CARRIAGEWAY_WIDTH)
        'structure.type': 'Steel Plate Girder Bridge',
        'geometry.span': '30.0',
        'geometry.carriageway_width': '7.5',

        # Typical section (KEY_TS_*)
        'typical_section.no_of_girders': 4,
        'typical_section.girder_spacing': '2.5',
        'typical_section.deck_overhang': '1.25',
        'typical_section.overall_bridge_width': '10.0',
        'typical_section.deck_thickness': '250',
        'typical_section.no_of_footpaths': 1,
        'typical_section.footpath_width': '1.5',
        'typical_section.footpath_thickness': '0.15',

        # Material (KEY_MATERIAL_*)
        'material.girder.density': '78.5',
        'material.deck.density': '25.0',
        'material.steel_grade': 'E 350 (Fe 490)',

        # Loading — Permanent load (KEY_PL_*)
        'loading.permanent_load.dead_load.self_weight_factor': '1.00',

        # Live loads (KEY_LL_*) — EXACT strings from common.py
        'loading.live_load.irc.class_a': True,
        'loading.live_load.irc.70r_wheeled': True,
        'loading.live_load.irc.70r_tracked': True,
        'loading.live_load.irc.aa_wheeled': True,
        'loading.live_load.irc.aa_tracked': True,
        'loading.live_load.irc.class_sv': True,
        'loading.live_load.irc.70r_bogie': True,
        'loading.live_load.irc.class_fatigue': True,
        'loading.live_load.custom_vehicles': [],
        'loading.live_load.eccentricity': '1.2',
        # Also set the short aliases for code that uses them directly
        'live_load.custom_vehicles': [],
        'live_load.eccentricity': '1.2',
        'loading.live_load.footpath_pressure.mode': 'As per IRC 6',
        'loading.live_load.footpath_pressure.value': '',

        # Crash barrier (KEY_CB_*)
        'typical_section.crash_barrier.type': 'IRC 5 - RCC Crash Barrier',
        'typical_section.crash_barrier.load': '7.5',

        # Railing (KEY_RL_*)
        'typical_section.railing.load_value': '1.47',

        # Wearing course (KEY_WC_*)
        'typical_section.wearing_course.material': 'Concrete',
        'typical_section.wearing_course.thickness': '50.0',

        # Wind load (KEY_WL_*)
        'loading.wind_load.basic_wind_speed': '39',
        'loading.wind_load.terrain_type': 'Plain Terrain',
        'loading.wind_load.avg_exposed_height': '10',
        'loading.wind_load.computed.hourly_mean_wind': '30.5',
        'loading.wind_load.computed.hourly_wind_pressure': '560.0',
        'loading.wind_load.computed.transverse_wind_force': '45.2',
        'loading.wind_load.computed.longitudinal_wind_force': '15.6',
        'loading.wind_load.computed.vertical_wind_force': '22.1',
        # Also keep the short alias for fallback in ch3
        'wind_speed': '39',

        # Seismic load (KEY_SL_*)
        'loading.seismic_load.seismic_zone': 'IV',
        'loading.seismic_load.computed.zone_factor': '0.24',
        'loading.seismic_load.importance_factor': '1.5',
        'loading.seismic_load.soil_type': 'Type II \u2013 Medium Soil',
        'loading.seismic_load.computed.spectral_coeff': '2.50',
        'loading.seismic_load.computed.horizontal_coeff': '0.12',
        'loading.seismic_load.computed.vertical_coeff': '0.08',
        'loading.seismic_load.time_period': '0.5',
        'loading.seismic_load.damping': '2',
        'loading.seismic_load.dead_load.mode': 'Automatic',
        'loading.seismic_load.dead_load.value': '',
        'loading.seismic_load.live_load.mode': 'Automatic',
        'loading.seismic_load.live_load.value': '',

        # Temperature (KEY_TL_*)
        'loading.temperature_load.highest_max_temp': '47.5',
        'loading.temperature_load.lowest_min_temp': '2.0',
        'loading.temperature_load.computed.bridge_temp_min': '5.0',
        'loading.temperature_load.computed.bridge_temp_max': '55.0',
        'loading.temperature_load.computed.temp_rise': '25.0',
        'loading.temperature_load.computed.temp_fall': '22.5',

        # Lane count (KEY_WC_LD_LANE_TABLE_COUNT)
        'typical_section.lane_details.lane_table_count': '2',

        # Design mode (KEY_DESIGN_MODE)
        'geometry.design_mode': 'Optimized',

        # ── Girder section properties (KEY_MP_GD_* / KEY_MP_GIRDER_*) ──
        'member_properties.girder_details.select_girder.G1': 'G1',
        'member_properties.girder_details.select_girder.G2': 'G2',
        'member_properties.girder_details.select_girder.G3': 'G3',
        'member_properties.girder_details.select_girder.G4': 'G4',
        'member_properties.member_id.G1.M1': 'G1M1',
        'member_properties.member_id.G2.M1': 'G2M1',
        'member_properties.member_id.G3.M1': 'G3M1',
        'member_properties.member_id.G4.M1': 'G4M1',
        'member_properties.girder_details.section_input.depth.G1.M1': '1200',
        'member_properties.girder_details.section_input.depth.G2.M1': '1200',
        'member_properties.girder_details.section_input.depth.G3.M1': '1200',
        'member_properties.girder_details.section_input.depth.G4.M1': '1200',
        'member_properties.girder_details.section_input.symmetry.G1.M1': 'Girder Symmetric',
        'member_properties.girder_details.section_input.top_flange_width.G1.M1': '400',
        'member_properties.girder_details.section_input.top_flange_thickness.G1.M1': '25',
        'member_properties.girder_details.section_input.bottom_flange_width.G1.M1': '400',
        'member_properties.girder_details.section_input.bottom_flange_thickness.G1.M1': '25',
        'member_properties.girder_details.section_input.web_thickness.G1.M1': '12',

        # Cross bracing (KEY_MP_CB_* / KEY_CROSS_BRACING)
        'material.cross_bracing': 'Yes',
        'member_properties.cross_bracing_details.no_of_cross_bracings': 3,
        'member_properties.cross_bracing_details.type.G1G2.B1M1': 'X-bracing',
        'member_properties.cross_bracing_details.bracing_section_designation.G1G2.B1M1': 'IS 100 x 100 x 10',
        'member_properties.cross_bracing_details.spacing.G1G2.B1M1': '7.5',
        'member_properties.cross_bracing_details.select_girders.G1G2.B1M1': 'G1 to G2',
        'member_properties.cross_bracing_details.member_id.G1G2.B1M1': 'B1M1 to B1M3',

        # End diaphragm (KEY_MP_ED_*)
        'end_diaphragm': 'Yes',
        'member_properties.end_diaphragm_details.type.G1G2.E1M1': 'Cross Bracing',
        'member_properties.end_diaphragm_details.bracing_section_designation.G1G2.E1M1': 'IS 100 x 100 x 10',
        'member_properties.end_diaphragm_details.select_girders.G1G2.E1M1': 'G1 to G2',
        'member_properties.end_diaphragm_details.member_id.G1G2.E1M1': 'E1M1 to E1M2',

        # Partial safety factors (KEY_DO_*)
        'design_options_cont.gamma_c_basic': '1.50',
        'design_options_cont.gamma_m0': '1.10',
        'design_options_cont.gamma_m1': '1.25',
        'design_options_cont.gamma_s': '1.15',
        'design_options_cont.gamma_v': '1.25',
        'design_options_cont.gamma_flt': '1.00',
        'design_options_cont.gamma_mf': '1.35',

        # Shear connector (KEY_DS_*)
        'design_options.shear_stud_diameter': '20',
        'design_options.shear_stud_height': '100',
        'design_options.shear_stud_count': '2',
        'design_options.shear_stud_transverse_spacing': '100',
        'design_options.stud_yield_strength': '385',
        'design_options.stud_ultimate_strength': '495',
        'design_options.top_clear_cover': '50',
        'design_options.bottom_clear_cover': '50',
        'design_options.reinf_material': 'Fe 500',
        'design_options.construction_stage': 'Yes',

        # ── BOQ quantities (pre-computed) ──
        'steel_girders_vol_formula': '4 × (0.4×0.025×2 + 1.15×0.012) × 30 m',
        'steel_girders_qty': '4',
        'steel_girders_vol_total': '3.84 m\u00b3',
        'steel_girders_wt_single': '7.52',
        'steel_girders_wt_total': '30.08',
        'bracing_top_vol_formula': '6 panels x 2.5m x 0.002 m\u00b2',
        'bracing_top_qty': '6',
        'bracing_top_vol_total': '0.03 m\u00b3',
        'bracing_top_wt_single': '0.04',
        'bracing_top_wt_total': '0.24',
        'bracing_bot_vol_formula': '6 panels x 2.5m x 0.002 m\u00b2',
        'bracing_bot_qty': '6',
        'bracing_bot_vol_total': '0.03 m\u00b3',
        'bracing_bot_wt_single': '0.04',
        'bracing_bot_wt_total': '0.24',
        'bracing_diag_vol_formula': '12 diag x 2.8m x 0.002 m\u00b2',
        'bracing_diag_qty': '12',
        'bracing_diag_vol_total': '0.067 m\u00b3',
        'bracing_diag_wt_single': '0.044',
        'bracing_diag_wt_total': '0.53',
        'end_diaphragm_wt_total': '0.42',
        'ed_top_vol_formula': '2 panels × 2.5m × 0.002 m²',
        'ed_top_qty': '2',
        'ed_top_vol_total': '0.01 m³',
        'ed_top_wt_single': '0.04',
        'ed_top_wt_total': '0.08',
        'ed_bot_vol_formula': '2 panels × 2.5m × 0.002 m²',
        'ed_bot_qty': '2',
        'ed_bot_vol_total': '0.01 m³',
        'ed_bot_wt_single': '0.04',
        'ed_bot_wt_total': '0.08',
        'ed_diag_vol_formula': '4 diag × 2.8m × 0.002 m²',
        'ed_diag_qty': '4',
        'ed_diag_vol_total': '0.022 m³',
        'ed_diag_wt_single': '0.044',
        'ed_diag_wt_total': '0.18',
        'concrete_deck_vol_formula': '30m x 10m x 0.25m',
        'concrete_deck_qty': '1',
        'concrete_deck_vol_total': '75.0',
        'concrete_deck_wt_single': '187.5',
        'concrete_deck_wt_total': '187.5',
        'rebar_deck_vol_formula': '1.5% of 75 m\u00b3',
        'rebar_deck_qty': '1',
        'rebar_deck_vol_total': '1.125',
        'rebar_deck_wt_single': '8.83',
        'rebar_deck_wt_total': '8.83',
        'shear_studs_vol_formula': '\u03c0(10)\u00b2 x 100mm/stud',
        'shear_studs_qty': '600',
        'shear_studs_vol_total': '0.019',
        'shear_studs_wt_single': '0.00025',
        'shear_studs_wt_total': '0.15',
        'crash_barrier_vol_formula': '2 barriers x 30m x 0.16 m\u00b2',
        'crash_barrier_qty': '2',
        'crash_barrier_vol_total': '9.6',
        'crash_barrier_wt_single': '120.0',
        'crash_barrier_wt_total': '240.0',

        # Deck design keys (KEY_DD_*) — EXACT from common.py
        'deck.report.fy': '500',
        'deck.report.gamma_dl': 1.35,
        'deck.report.gamma_ll': 1.50,
        'deck.report.m_dl': 42.5,
        'deck.report.m_ll': 68.3,
        'deck.report.impact_factor': 1.127,
        'deck.report.m_uls_sag': 135.6,
        'deck.report.m_uls_hog': 98.2,
        'deck.report.mu_bot': 162.0,
        'deck.report.mu_top': 118.5,
        'deck.report.has_overhang': True,
        'deck.report.m_dl_oh': 15.2,
        'deck.report.m_ll_oh': 28.6,
        'deck.report.m_uls_oh': 62.5,
        'deck.report.mu_oh': 85.0,
        'deck.report.m_barrier': 12.5,
        'deck.report.d_bot': 195.0,
        'deck.report.dia_bot': 16,
        'deck.report.as_req_bot': 2850.0,
        'deck.report.as_bot': 3217.0,
        'deck.report.as_req_top': 1950.0,
        'deck.report.as_top': 2412.0,
        'deck.report.as_long': 645.0,
        'deck.report.as_min': 450.0,
        'deck.report.min_cover': 50,
        'deck.report.cover_ok': 'OK',
        'deck.report.punch_c1': 150.0,
        'deck.report.punch_c2': 100.0,
        'deck.report.punch_ved': 185.0,
        'deck.report.punch_ved_kn': 185.0,
        'deck.report.punch_ok': 'OK',
        'deck.report.vrd_c_mpa': 0.52,
        'deck.report.shear_ved': 95.0,
        'deck.report.shear_vrdc': 142.0,
        'deck.report.wk_bot': 0.18,
        'deck.report.wk_top': 0.12,
        'deckdesign.crack.wk.limit': 0.30,
        'deckdesign.crack.wk.bottom': 0.18,
        'deckdesign.crack.wk.top': 0.12,
        'deck.report.span': '30.0',
        'deck.report.vehicle_class': 'Class 70R (Wheeled)',
    }

    # ── output_dict with properly structured design results for Table 5.22 ──
    output_dict = {
        # Section designation (KEY_SD_SECTION_DESIGNATION)
        'steeldesign.details.section_designation': 'Welded I 1200 x 400 x 12 x 25',

        # Category URs for the UR chart
        'category_urs': {
            'flexure': 0.87,
            'shear': 0.62,
            'interaction': 0.78,
            'ltb': 0.45,
            'fatigue': 0.55,
        },

        # Deck UR
        'deck_ur': 0.72,

        # Design results structured for executive summary and Table 5.22
        'design_results': {
            'per_girder': {
                'G1': {
                    'checks': [
                        {'check_id': 1, 'name': 'Moment', 'dcr': 0.87, 'status': 'PASS',
                         'demand': 4250, 'capacity': 4885, 'demand_unit': 'kN-m', 'capacity_unit': 'kN-m'},
                        {'check_id': 2, 'name': 'Shear', 'dcr': 0.62, 'status': 'PASS',
                         'demand': 580, 'capacity': 935, 'demand_unit': 'kN', 'capacity_unit': 'kN'},
                        {'check_id': 5, 'name': 'LTB (Construction)', 'dcr': 0.45, 'status': 'PASS',
                         'demand': 2200, 'capacity': 4885, 'demand_unit': 'kN-m', 'capacity_unit': 'kN-m'},
                        {'check_id': 8, 'name': 'Fatigue — Normal Stress', 'dcr': 0.55, 'status': 'PASS',
                         'demand': 65, 'capacity': 118, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 9, 'name': 'Fatigue — Shear Stress', 'dcr': 0.42, 'status': 'PASS',
                         'demand': 35, 'capacity': 83, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 11, 'name': 'Stress Limitation', 'dcr': 0.78, 'status': 'PASS',
                         'demand': 234, 'capacity': 300, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 13, 'name': 'Deflection (LL)', 'dcr': 0.52, 'status': 'PASS',
                         'demand': 12.5, 'capacity': 24.0, 'demand_unit': 'mm', 'capacity_unit': 'mm'},
                        {'check_id': 16, 'name': 'Transverse Shear', 'dcr': 0.38, 'status': 'PASS',
                         'demand': 95, 'capacity': 250, 'demand_unit': 'kN', 'capacity_unit': 'kN'},
                    ],
                    'per_lc': {
                        'ULS-01: 1.35DL + 1.50LL': {
                            'max_dcr': 0.87,
                            'checks': [
                                {'id': 1, 'dcr': 0.87, 'demand': 4250, 'capacity': 4885},
                                {'id': 2, 'dcr': 0.62, 'demand': 580, 'capacity': 935},
                                {'id': 5, 'dcr': 0.45, 'demand': 2200, 'capacity': 4885},
                                {'id': 11, 'dcr': 0.78, 'demand': 234, 'capacity': 300},
                                {'id': 16, 'dcr': 0.38, 'demand': 95, 'capacity': 250},
                            ]
                        },
                        'SLS-Frequent: 1.0DL + 0.75LL': {
                            'max_dcr': 0.52,
                            'checks': [
                                {'id': 13, 'dcr': 0.52, 'demand': 12.5, 'capacity': 24.0},
                                {'id': 8, 'dcr': 0.55, 'demand': 65, 'capacity': 118},
                                {'id': 9, 'dcr': 0.42, 'demand': 35, 'capacity': 83},
                            ]
                        },
                    },
                },
                'G2': {
                    'checks': [
                        {'check_id': 1, 'name': 'Moment', 'dcr': 0.86, 'status': 'PASS',
                         'demand': 4180, 'capacity': 4885, 'demand_unit': 'kN-m', 'capacity_unit': 'kN-m'},
                        {'check_id': 2, 'name': 'Shear', 'dcr': 0.60, 'status': 'PASS',
                         'demand': 560, 'capacity': 935, 'demand_unit': 'kN', 'capacity_unit': 'kN'},
                        {'check_id': 5, 'name': 'LTB (Construction)', 'dcr': 0.44, 'status': 'PASS',
                         'demand': 2150, 'capacity': 4885, 'demand_unit': 'kN-m', 'capacity_unit': 'kN-m'},
                        {'check_id': 8, 'name': 'Fatigue — Normal Stress', 'dcr': 0.53, 'status': 'PASS',
                         'demand': 63, 'capacity': 118, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 9, 'name': 'Fatigue — Shear Stress', 'dcr': 0.40, 'status': 'PASS',
                         'demand': 33, 'capacity': 83, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 11, 'name': 'Stress Limitation', 'dcr': 0.76, 'status': 'PASS',
                         'demand': 228, 'capacity': 300, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 13, 'name': 'Deflection (LL)', 'dcr': 0.49, 'status': 'PASS',
                         'demand': 11.8, 'capacity': 24.0, 'demand_unit': 'mm', 'capacity_unit': 'mm'},
                        {'check_id': 16, 'name': 'Transverse Shear', 'dcr': 0.36, 'status': 'PASS',
                         'demand': 90, 'capacity': 250, 'demand_unit': 'kN', 'capacity_unit': 'kN'},
                    ],
                    'per_lc': {
                        'ULS-01: 1.35DL + 1.50LL': {
                            'max_dcr': 0.86,
                            'checks': [
                                {'id': 1, 'dcr': 0.86, 'demand': 4180, 'capacity': 4885},
                                {'id': 2, 'dcr': 0.60, 'demand': 560, 'capacity': 935},
                                {'id': 5, 'dcr': 0.44, 'demand': 2150, 'capacity': 4885},
                                {'id': 11, 'dcr': 0.76, 'demand': 228, 'capacity': 300},
                                {'id': 16, 'dcr': 0.36, 'demand': 90, 'capacity': 250},
                            ]
                        },
                        'SLS-Frequent: 1.0DL + 0.75LL': {
                            'max_dcr': 0.49,
                            'checks': [
                                {'id': 13, 'dcr': 0.49, 'demand': 11.8, 'capacity': 24.0},
                                {'id': 8, 'dcr': 0.53, 'demand': 63, 'capacity': 118},
                                {'id': 9, 'dcr': 0.40, 'demand': 33, 'capacity': 83},
                            ]
                        },
                    },
                },
                'G3': {
                    'checks': [
                        {'check_id': 1, 'name': 'Moment', 'dcr': 0.86, 'status': 'PASS',
                         'demand': 4180, 'capacity': 4885, 'demand_unit': 'kN-m', 'capacity_unit': 'kN-m'},
                        {'check_id': 2, 'name': 'Shear', 'dcr': 0.60, 'status': 'PASS',
                         'demand': 560, 'capacity': 935, 'demand_unit': 'kN', 'capacity_unit': 'kN'},
                        {'check_id': 5, 'name': 'LTB (Construction)', 'dcr': 0.44, 'status': 'PASS',
                         'demand': 2150, 'capacity': 4885, 'demand_unit': 'kN-m', 'capacity_unit': 'kN-m'},
                        {'check_id': 8, 'name': 'Fatigue — Normal Stress', 'dcr': 0.53, 'status': 'PASS',
                         'demand': 63, 'capacity': 118, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 9, 'name': 'Fatigue — Shear Stress', 'dcr': 0.40, 'status': 'PASS',
                         'demand': 33, 'capacity': 83, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 11, 'name': 'Stress Limitation', 'dcr': 0.76, 'status': 'PASS',
                         'demand': 228, 'capacity': 300, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 13, 'name': 'Deflection (LL)', 'dcr': 0.49, 'status': 'PASS',
                         'demand': 11.8, 'capacity': 24.0, 'demand_unit': 'mm', 'capacity_unit': 'mm'},
                        {'check_id': 16, 'name': 'Transverse Shear', 'dcr': 0.36, 'status': 'PASS',
                         'demand': 90, 'capacity': 250, 'demand_unit': 'kN', 'capacity_unit': 'kN'},
                    ],
                    'per_lc': {
                        'ULS-01: 1.35DL + 1.50LL': {
                            'max_dcr': 0.86,
                            'checks': [
                                {'id': 1, 'dcr': 0.86, 'demand': 4180, 'capacity': 4885},
                                {'id': 2, 'dcr': 0.60, 'demand': 560, 'capacity': 935},
                                {'id': 5, 'dcr': 0.44, 'demand': 2150, 'capacity': 4885},
                                {'id': 11, 'dcr': 0.76, 'demand': 228, 'capacity': 300},
                                {'id': 16, 'dcr': 0.36, 'demand': 90, 'capacity': 250},
                            ]
                        },
                        'SLS-Frequent: 1.0DL + 0.75LL': {
                            'max_dcr': 0.49,
                            'checks': [
                                {'id': 13, 'dcr': 0.49, 'demand': 11.8, 'capacity': 24.0},
                                {'id': 8, 'dcr': 0.53, 'demand': 63, 'capacity': 118},
                                {'id': 9, 'dcr': 0.40, 'demand': 33, 'capacity': 83},
                            ]
                        },
                    },
                },
                'G4': {
                    'checks': [
                        {'check_id': 1, 'name': 'Moment', 'dcr': 0.87, 'status': 'PASS',
                         'demand': 4250, 'capacity': 4885, 'demand_unit': 'kN-m', 'capacity_unit': 'kN-m'},
                        {'check_id': 2, 'name': 'Shear', 'dcr': 0.62, 'status': 'PASS',
                         'demand': 580, 'capacity': 935, 'demand_unit': 'kN', 'capacity_unit': 'kN'},
                        {'check_id': 5, 'name': 'LTB (Construction)', 'dcr': 0.45, 'status': 'PASS',
                         'demand': 2200, 'capacity': 4885, 'demand_unit': 'kN-m', 'capacity_unit': 'kN-m'},
                        {'check_id': 8, 'name': 'Fatigue — Normal Stress', 'dcr': 0.55, 'status': 'PASS',
                         'demand': 65, 'capacity': 118, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 9, 'name': 'Fatigue — Shear Stress', 'dcr': 0.42, 'status': 'PASS',
                         'demand': 35, 'capacity': 83, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 11, 'name': 'Stress Limitation', 'dcr': 0.78, 'status': 'PASS',
                         'demand': 234, 'capacity': 300, 'demand_unit': 'MPa', 'capacity_unit': 'MPa'},
                        {'check_id': 13, 'name': 'Deflection (LL)', 'dcr': 0.52, 'status': 'PASS',
                         'demand': 12.5, 'capacity': 24.0, 'demand_unit': 'mm', 'capacity_unit': 'mm'},
                        {'check_id': 16, 'name': 'Transverse Shear', 'dcr': 0.38, 'status': 'PASS',
                         'demand': 95, 'capacity': 250, 'demand_unit': 'kN', 'capacity_unit': 'kN'},
                    ],
                    'per_lc': {
                        'ULS-01: 1.35DL + 1.50LL': {
                            'max_dcr': 0.87,
                            'checks': [
                                {'id': 1, 'dcr': 0.87, 'demand': 4250, 'capacity': 4885},
                                {'id': 2, 'dcr': 0.62, 'demand': 580, 'capacity': 935},
                                {'id': 5, 'dcr': 0.45, 'demand': 2200, 'capacity': 4885},
                                {'id': 11, 'dcr': 0.78, 'demand': 234, 'capacity': 300},
                                {'id': 16, 'dcr': 0.38, 'demand': 95, 'capacity': 250},
                            ]
                        },
                        'SLS-Frequent: 1.0DL + 0.75LL': {
                            'max_dcr': 0.52,
                            'checks': [
                                {'id': 13, 'dcr': 0.52, 'demand': 12.5, 'capacity': 24.0},
                                {'id': 8, 'dcr': 0.55, 'demand': 65, 'capacity': 118},
                                {'id': 9, 'dcr': 0.42, 'demand': 35, 'capacity': 83},
                            ]
                        },
                    },
                },
            },
        },

        # Deck design results for Table 5.22 deck rows
        'deck_design_results': {
            'ur_sag': 0.84,
            'ur_hog': 0.83,
            'ur_oh': 0.74,
            'ur_punch': 0.71,
            'ur_shear': 0.67,
        },

        # Cross bracing design results
        'crossbracing_forces_dict': {
            'geometry': {'diagonal_length_m': 2.8, 'horiz_proj_m': 2.5, 'alpha_deg': 63.43},
            'brace_type': 'X',
            'pairs': {
                'G1-G2': {
                    'diag_tension_kN': 45.2, 'diag_compression_kN': -38.6,
                    'chord_tension_kN': 22.1, 'chord_compression_kN': -18.9,
                    'diag_compression_gov_lc': 'ULS-01',
                    'diag_tension_gov_lc': 'ULS-03',
                    'chord_compression_gov_lc': 'ULS-01',
                    'chord_tension_gov_lc': 'ULS-03',
                },
                'G2-G3': {
                    'diag_tension_kN': 42.8, 'diag_compression_kN': -36.1,
                    'chord_tension_kN': 20.5, 'chord_compression_kN': -17.2,
                    'diag_compression_gov_lc': 'ULS-01', 'diag_tension_gov_lc': 'ULS-03',
                    'chord_compression_gov_lc': 'ULS-01', 'chord_tension_gov_lc': 'ULS-03',
                },
                'G3-G4': {
                    'diag_tension_kN': 44.0, 'diag_compression_kN': -37.5,
                    'chord_tension_kN': 21.3, 'chord_compression_kN': -18.1,
                    'diag_compression_gov_lc': 'ULS-01', 'diag_tension_gov_lc': 'ULS-03',
                    'chord_compression_gov_lc': 'ULS-01', 'chord_tension_gov_lc': 'ULS-03',
                },
            }
        },
        # Cross bracing design results — use Osdag internal key format
        # so _extract_osdag_summary() can parse them correctly
        'crossbracing_design_results': {
            'G1-G2': {
                'diagonal': {
                    'tension': {'section_size.designation': 'IS 100 x 100 x 10', 'Member.tension_capacity': 180.5, 'Member.efficiency': 0.25, 'Member.Slenderness': 85.2},
                    'compression': {'section_size.designation': 'IS 100 x 100 x 10', 'Design.Strength': 120.3, 'Member.efficiency': 0.32, 'Member.Slenderness': 85.2},
                },
                'chord': {
                    'tension': {'section_size.designation': 'IS 100 x 100 x 10', 'Member.tension_capacity': 180.5, 'Member.efficiency': 0.12, 'Member.Slenderness': 65.0},
                    'compression': {'section_size.designation': 'IS 100 x 100 x 10', 'Design.Strength': 120.3, 'Member.efficiency': 0.16, 'Member.Slenderness': 65.0},
                },
            },
            'G2-G3': {
                'diagonal': {
                    'tension': {'section_size.designation': 'IS 100 x 100 x 10', 'Member.tension_capacity': 180.5, 'Member.efficiency': 0.24, 'Member.Slenderness': 85.2},
                    'compression': {'section_size.designation': 'IS 100 x 100 x 10', 'Design.Strength': 120.3, 'Member.efficiency': 0.30, 'Member.Slenderness': 85.2},
                },
                'chord': {
                    'tension': {'section_size.designation': 'IS 100 x 100 x 10', 'Member.tension_capacity': 180.5, 'Member.efficiency': 0.11, 'Member.Slenderness': 65.0},
                    'compression': {'section_size.designation': 'IS 100 x 100 x 10', 'Design.Strength': 120.3, 'Member.efficiency': 0.14, 'Member.Slenderness': 65.0},
                },
            },
            'G3-G4': {
                'diagonal': {
                    'tension': {'section_size.designation': 'IS 100 x 100 x 10', 'Member.tension_capacity': 180.5, 'Member.efficiency': 0.24, 'Member.Slenderness': 85.2},
                    'compression': {'section_size.designation': 'IS 100 x 100 x 10', 'Design.Strength': 120.3, 'Member.efficiency': 0.31, 'Member.Slenderness': 85.2},
                },
                'chord': {
                    'tension': {'section_size.designation': 'IS 100 x 100 x 10', 'Member.tension_capacity': 180.5, 'Member.efficiency': 0.12, 'Member.Slenderness': 65.0},
                    'compression': {'section_size.designation': 'IS 100 x 100 x 10', 'Design.Strength': 120.3, 'Member.efficiency': 0.15, 'Member.Slenderness': 65.0},
                },
            },
        },

        # End diaphragm results (same Osdag internal key format)
        'enddiaphragm_design_results': {
            'G1-G2': {
                'diagonal': {
                    'tension': {'section_size.designation': 'IS 100 x 100 x 10', 'Member.tension_capacity': 180.5, 'Member.efficiency': 0.22, 'Member.Slenderness': 82.0},
                    'compression': {'section_size.designation': 'IS 100 x 100 x 10', 'Design.Strength': 120.3, 'Member.efficiency': 0.28, 'Member.Slenderness': 82.0},
                },
                'chord': {
                    'tension': {'section_size.designation': 'IS 100 x 100 x 10', 'Member.tension_capacity': 180.5, 'Member.efficiency': 0.10, 'Member.Slenderness': 60.0},
                    'compression': {'section_size.designation': 'IS 100 x 100 x 10', 'Design.Strength': 120.3, 'Member.efficiency': 0.14, 'Member.Slenderness': 60.0},
                },
            },
        },

        # Design checks list (for generic fallback)
        'design_checks': [],

        # Deck report values (for Table 5.17 and Table 5.22 deck rows)
        # Uses KEY_DD_* constants from common.py as keys
        'deck_report_values': {
            'deck.report.fy': '500',
            'deck.report.gamma_dl': 1.35,
            'deck.report.gamma_ll': 1.50,
            'deck.report.m_dl': 42.5,
            'deck.report.m_ll': 68.3,
            'deck.report.impact_factor': 1.127,
            'deck.report.m_uls_sag': 135.6,
            'deck.report.m_uls_hog': 98.2,
            'deck.report.mu_bot': 162.0,
            'deck.report.mu_top': 118.5,
            'deck.report.has_overhang': True,
            'deck.report.m_dl_oh': 15.2,
            'deck.report.m_ll_oh': 28.6,
            'deck.report.m_uls_oh': 62.5,
            'deck.report.mu_oh': 85.0,
            'deck.report.m_barrier': 12.5,
            'deck.report.d_bot': 195.0,
            'deck.report.d_top': 180.0,
            'deck.report.d_oh': 170.0,
            'deck.report.dia_bot': 16,
            'deck.report.dia_top': 12,
            'deck.report.dia_oh': 12,
            'deck.report.as_req_bot': 2850.0,
            'deck.report.as_bot': 3217.0,
            'deck.report.as_req_top': 1950.0,
            'deck.report.as_top': 2412.0,
            'deck.report.as_req_oh': 1650.0,
            'deck.report.as_oh': 1810.0,
            'deck.report.as_long': 645.0,
            'deck.report.as_min': 450.0,
            'deck.report.min_cover': 50,
            'deck.report.cover_ok': 'OK',
            'deck.report.spc_bot': 125,
            'deck.report.spc_top': 150,
            'deck.report.spc_oh': 150,
            'deck.report.spacing_max': 200,
            'deck.report.punch_c1': 150.0,
            'deck.report.punch_c2': 100.0,
            'deck.report.punch_u1': 780.0,
            'deck.report.punch_ved': 0.42,
            'deck.report.punch_ved_kn': 185.0,
            'deck.report.punch_ok': 'OK',
            'deck.report.vrd_c_mpa': 0.52,
            'deck.report.shear_ved': 95.0,
            'deck.report.shear_vrdc': 142.0,
            'deck.report.shear_ok': 'OK',
            'deck.report.wk_bot': 0.18,
            'deck.report.wk_top': 0.12,
            'deck.report.wk_oh': 0.15,
            'deck.report.wk_limit': 0.30,
            'deckdesign.crack.wk.limit': 0.30,
            'deckdesign.crack.wk.bottom': 0.18,
            'deckdesign.crack.wk.top': 0.12,
            'deck.report.span': '30.0',
            'deck.report.vehicle_class': 'Class 70R (Wheeled)',
            'deck.report.tyre_contact_length': 250,
            'deck.report.tyre_contact_width': 500,
            'deck.report.wheel_load': 85.0,
            'deck.report.w_dl': 6.25,
        },

        # Analysis summary with per-load-case data for Chapter 4 table
        'analysis_summary': {
            'load_cases': {
                'ULS-01: 1.35DL + 1.50LL': {
                    'max_bm': 4250.0, 'bm_girder': 'G1', 'bm_location': 15.0,
                    'max_sf': 580.0, 'sf_girder': 'G1', 'sf_location': 0.0,
                },
                'ULS-02: 1.35DL + 1.50LL + 0.9WL': {
                    'max_bm': 3980.0, 'bm_girder': 'G1', 'bm_location': 15.0,
                    'max_sf': 545.0, 'sf_girder': 'G1', 'sf_location': 0.0,
                },
                'ULS-03: 1.35DL + 1.50WL + 0.75LL': {
                    'max_bm': 3620.0, 'bm_girder': 'G2', 'bm_location': 15.0,
                    'max_sf': 498.0, 'sf_girder': 'G1', 'sf_location': 0.0,
                },
                'SLS-Frequent: 1.0DL + 0.75LL': {
                    'max_bm': 2850.0, 'bm_girder': 'G1', 'bm_location': 15.0,
                    'max_sf': 390.0, 'sf_girder': 'G1', 'sf_location': 0.0,
                },
                'SLS-Rare: 1.0DL + 1.0LL': {
                    'max_bm': 3450.0, 'bm_girder': 'G1', 'bm_location': 15.0,
                    'max_sf': 470.0, 'sf_girder': 'G1', 'sf_location': 0.0,
                },
                'Construction: 1.35DL (steel only)': {
                    'max_bm': 2200.0, 'bm_girder': 'G1', 'bm_location': 15.0,
                    'max_sf': 295.0, 'sf_girder': 'G1', 'sf_location': 0.0,
                },
            },
            'reactions': {
                'ULS-01: 1.35DL + 1.50LL': {'left_kN': 580.0, 'right_kN': 580.0},
                'ULS-02: 1.35DL + 1.50LL + 0.9WL': {'left_kN': 545.0, 'right_kN': 545.0},
                'ULS-03: 1.35DL + 1.50WL + 0.75LL': {'left_kN': 498.0, 'right_kN': 498.0},
                'SLS-Frequent: 1.0DL + 0.75LL': {'left_kN': 390.0, 'right_kN': 390.0},
                'SLS-Rare: 1.0DL + 1.0LL': {'left_kN': 470.0, 'right_kN': 470.0},
                'Construction: 1.35DL (steel only)': {'left_kN': 295.0, 'right_kN': 295.0},
            },
            'max_bm': '4250 kN-m', 'max_sf': '580 kN', 'max_defl': '12.5 mm',
        },

        # Deflection data per girder (KEY_SD_DEFL_LIVE, KEY_SD_DEFL_TOTAL)
        'steeldesign.deflection.live_mm.G1': 12.5,
        'steeldesign.deflection.live_mm.G2': 11.8,
        'steeldesign.deflection.live_mm.G3': 11.8,
        'steeldesign.deflection.live_mm.G4': 12.5,
        'steeldesign.deflection.total_mm.G1': 18.2,
        'steeldesign.deflection.total_mm.G2': 17.1,
        'steeldesign.deflection.total_mm.G3': 17.1,
        'steeldesign.deflection.total_mm.G4': 18.2,

        # ── Section properties — BASE keys (used by chap5.py _render_value) ──
        'steeldesign.details.section_properties.iz': '1.85 × 10⁴ cm⁴',
        'steeldesign.details.section_properties.zz': '30833 cm³',
        'steeldesign.details.section_properties.zuz': '35280 cm³',
        'steeldesign.details.section_properties.area': '348 cm²',
        'steeldesign.details.section_properties.pna_depth': '600',
        'steeldesign.details.section_properties.mass': '273.2 kg/m',
        'steeldesign.details.section_properties.composite_iz': '3.42 × 10⁴ cm⁴',
        'steeldesign.details.total_depth': '1200',
        'steeldesign.details.top_flange_width': '400',
        'steeldesign.details.bottom_flange_width': '400',
        'steeldesign.details.top_flange_thickness': '25',
        'steeldesign.details.bottom_flange_thickness': '25',
        'steeldesign.details.web_thickness': '12',
        'steeldesign.details.effective_slab_width': '2500',
        'steeldesign.details.section_class': 'Plastic',
        'steeldesign.details.classification.flange_class': 'Plastic',
        'steeldesign.details.classification.web_class': 'Plastic',
        'steeldesign.details.classification.flange_slenderness': '7.5',
        'steeldesign.details.classification.web_slenderness': '95.8',
        'steeldesign.details.classification.flange_class_limit': '9.4',
        'steeldesign.details.classification.web_class_limit': '105.0',
        'steeldesign.details.moment.md_capacity': '4885',
        'steeldesign.details.moment.mu_applied': '4250',
        'steeldesign.details.shear_check.vu_applied': '580',
        'steeldesign.details.shear_check.av_area': '13800',
        'steeldesign.details.shear_check.kv': '5.35',
        'steeldesign.details.shear_check.lambda_w': '0.91',
        'steeldesign.details.shear_check.tau_b': '115.6',
        'steeldesign.details.shear_check.vcr': '1595',
        'steeldesign.details.ltb.mcr': '6520',
        'steeldesign.details.ltb.lambda_lt': '0.866',
        'steeldesign.details.ltb.chi_lt': '0.712',
        'steeldesign.details.ltb.mb': '3480',
        'steeldesign.details.interaction.high_shear': 'No ($V < 0.6\,V_d$)',
        'steeldesign.details.interaction.mdv': '4885',
        'steeldesign.details.interaction.mn_axial': 0.0,
        'steeldesign.details.interaction.mn_moment': 0.87,
        'steeldesign.details.interaction.mn_ratio': 0.87,
        'steeldesign.details.stiffener_summary.method': 'Tension Field Action',
        'steeldesign.details.stiffener_summary.end_count': '2 per bearing',
        'steeldesign.details.stiffener_summary.end_thickness': '20 mm',
        'steeldesign.details.stiffener_summary.int_spacing': '1500 mm',
        'steeldesign.details.stiffener_summary.int_thickness': '12 mm',
        'steeldesign.details.stiffener_summary.longitudinal': 'Not required',
        'steeldesign.details.bearing_stiffener.reaction': '580',
        'steeldesign.details.bearing_stiffener.fcd': '1850',
        'steeldesign.details.bearing_stiffener.fcdw_lc': '920',
        'steeldesign.details.bearing_stiffener.fcdw_wb': '850',
        'steeldesign.details.bearing_stiffener.fpsd': '1250',
        'steeldesign.details.int_stiffener.fq': '115',
        'steeldesign.details.int_stiffener.fqd': '165',
        'steeldesign.details.int_stiffener.iys_min': '120',
        'steeldesign.details.int_stiffener.iys_prov': '185',
        'steeldesign.details.shear_check.panel_cd': '210',
        'steeldesign.stress.steel': '195',
        'steeldesign.stress.steel.allowable': '217',
        'steeldesign.deflection.live_mm': '12.5',
        'steeldesign.deflection.total_mm': '18.2',
        'steeldesign.deflection.allow_live_mm': '37.5',
        'steeldesign.deflection.allow_total_mm': '50.0',
        'steeldesign.uls_per_girder': '4250 kN-m',
        'steeldesign.transverse_shear.vl_kN_per_m': '185',
        'steeldesign.transverse_shear.vrd_kN_per_m': '450',
        'steeldesign.shear_connector.qu_kN': '58.2',
        'steeldesign.shear_connector.qr_kN': '46.6',
        'steeldesign.shear_connector.sl1_mm': '180',
        'steeldesign.shear_connector.sl2_mm': '300',
        'steeldesign.shear_connector.sr_mm': '180',
        'steeldesign.shear_connector.edge_distance_mm': '30',
        'steeldesign.shear_connector.req_edge_distance_mm': '25',
        'steeldesign.shear_connector.d_limit_mm': '22',

        # ── Per-girder keys (kept for any per-girder accessor paths) ──
        'steeldesign.details.section_properties.iz.G1.M1': 1.85e10,
        'steeldesign.details.section_properties.iz.G2.M1': 1.85e10,
        'steeldesign.details.section_properties.iz.G3.M1': 1.85e10,
        'steeldesign.details.section_properties.iz.G4.M1': 1.85e10,
        'steeldesign.details.section_properties.zz.G1.M1': 30833.3,
        'steeldesign.details.section_properties.zz.G2.M1': 30833.3,
        'steeldesign.details.section_properties.zz.G3.M1': 30833.3,
        'steeldesign.details.section_properties.zz.G4.M1': 30833.3,
        'steeldesign.details.section_properties.zuz.G1.M1': 35280.0,
        'steeldesign.details.section_properties.zuz.G2.M1': 35280.0,
        'steeldesign.details.section_properties.zuz.G3.M1': 35280.0,
        'steeldesign.details.section_properties.zuz.G4.M1': 35280.0,
        'steeldesign.details.section_properties.area.G1.M1': 34800.0,
        'steeldesign.details.section_properties.area.G2.M1': 34800.0,
        'steeldesign.details.section_properties.area.G3.M1': 34800.0,
        'steeldesign.details.section_properties.area.G4.M1': 34800.0,
        'steeldesign.details.section_properties.pna_depth.G1.M1': 600.0,
        'steeldesign.details.section_properties.pna_depth.G2.M1': 600.0,
        'steeldesign.details.section_properties.pna_depth.G3.M1': 600.0,
        'steeldesign.details.section_properties.pna_depth.G4.M1': 600.0,
        'steeldesign.details.section_properties.mass.G1.M1': 273.2,
        'steeldesign.details.section_properties.mass.G2.M1': 273.2,
        'steeldesign.details.section_properties.mass.G3.M1': 273.2,
        'steeldesign.details.section_properties.mass.G4.M1': 273.2,
        'steeldesign.details.section_properties.composite_iz.G1.M1': 3.42e10,
        'steeldesign.details.section_properties.composite_iz.G2.M1': 3.42e10,
        'steeldesign.details.section_properties.composite_iz.G3.M1': 3.42e10,
        'steeldesign.details.section_properties.composite_iz.G4.M1': 3.42e10,

        # Section classification per-girder
        'steeldesign.details.section_class.G1.M1': 'Plastic',
        'steeldesign.details.section_class.G2.M1': 'Plastic',
        'steeldesign.details.section_class.G3.M1': 'Plastic',
        'steeldesign.details.section_class.G4.M1': 'Plastic',
        'steeldesign.details.classification.flange_class.G1.M1': 'Plastic',
        'steeldesign.details.classification.web_class.G1.M1': 'Plastic',
        'steeldesign.details.classification.flange_slenderness.G1.M1': 7.5,
        'steeldesign.details.classification.web_slenderness.G1.M1': 95.8,
        'steeldesign.details.classification.flange_class_limit.G1.M1': 9.4,
        'steeldesign.details.classification.web_class_limit.G1.M1': 105.0,

        # Moment capacity per-girder
        'steeldesign.details.moment.md_capacity.G1.M1': 4885.0,
        'steeldesign.details.moment.md_capacity.G2.M1': 4885.0,
        'steeldesign.details.moment.md_capacity.G3.M1': 4885.0,
        'steeldesign.details.moment.md_capacity.G4.M1': 4885.0,
        'steeldesign.details.moment.mu_applied.G1.M1': 4250.0,

        # Shear capacity per-girder
        'steeldesign.details.shear_check.vd.G1.M1': 935.0,
        'steeldesign.details.shear_check.vd.G2.M1': 935.0,
        'steeldesign.details.shear_check.vd.G3.M1': 935.0,
        'steeldesign.details.shear_check.vd.G4.M1': 935.0,

        # LTB per-girder
        'steeldesign.details.ltb.mcr.G1.M1': 6520.0,
        'steeldesign.details.ltb.lambda_lt.G1.M1': 0.866,
        'steeldesign.details.ltb.chi_lt.G1.M1': 0.712,
        'steeldesign.details.ltb.mb.G1.M1': 3480.0,

        # Effective slab width per-girder
        'steeldesign.details.effective_slab_width.G1.M1': 2500.0,
        'steeldesign.details.effective_slab_width.G2.M1': 2500.0,
        'steeldesign.details.effective_slab_width.G3.M1': 2500.0,
        'steeldesign.details.effective_slab_width.G4.M1': 2500.0,

        # Steel grade
        'steeldesign.details.grade_of_material': 'E 350 (Fe 490)',
        'steeldesign.details.total_depth.G1.M1': 1200.0,
        'steeldesign.details.web_thickness.G1.M1': 12.0,
        'steeldesign.details.top_flange_width.G1.M1': 400.0,
        'steeldesign.details.bottom_flange_width.G1.M1': 400.0,
        'steeldesign.details.bottom_flange_thickness.G1.M1': 25.0,

        # ── Utilization ratios (percentage values, divided by 100 in chap5) ──
        'util.flexure': 87.0,        # Mu/Md = 4250/4885 ≈ 0.87
        'util.shear': 48.8,          # Vu/Vcr = 780/1595 ≈ 0.49
        'util.interaction': 87.0,    # M-V interaction
        'util.ltb': 71.2,            # Mu/Mb = 4250/3480... but capped by chi_lt

        # Design log
        'design_log': [
            'Stage 1: Initial sizing complete \u2014 D=1200mm, tw=12mm',
            'Stage 2: Flange sizing \u2014 tf=25mm, bf=400mm',
            'Stage 3: Section properties computed',
            'Stage 4: Grillage analysis complete (OSPGrillage)',
            'Stage 5: ULS Bending check \u2014 PASS (UR=0.87)',
            'Stage 6: ULS Shear check \u2014 PASS (UR=0.62)',
            'Stage 7: LTB check (construction) \u2014 PASS (UR=0.45)',
            'Stage 8: Stiffener design complete',
            'Stage 9: Cross bracing design \u2014 PASS',
            'Stage 10: End diaphragm design \u2014 PASS',
            'Stage 11: Deck slab design \u2014 PASS',
            'Stage 12: Shear connector design \u2014 PASS',
            'Stage 13: SLS stress limitation \u2014 PASS',
            'Stage 14: Fatigue check \u2014 PASS (UR=0.55)',
        ],
    }

    analysis_summary = output_dict.get('analysis_summary', {})

    payload = ReportPayload(
        metadata=metadata,
        options=options,
        inputs=input_dict,
        analysis_summary=analysis_summary,
        design_checks=output_dict.get('design_checks', []),
        figures=ReportFigures(),
        log_entries=output_dict.get('design_log', []),
        output_dict=output_dict,
        figure_data={},
    )

    return payload


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate OsdagBridge test report')
    parser.add_argument('--output-dir', default='/home/rithan/iitb OSDAG/test_reports',
                        help='Output directory for the report')
    parser.add_argument('--stem', default='Report_After',
                        help='File stem (name without extension)')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    payload = build_mock_payload()

    # Generate placeholder bridge figures
    import tempfile
    fig_dir = os.path.join(args.output_dir, '_fig_tmp')
    os.makedirs(fig_dir, exist_ok=True)
    figs = _generate_placeholder_figures(fig_dir)

    # Wire figures into payload and figure_data as PNG bytes
    for attr, path in figs.items():
        with open(path, 'rb') as f:
            payload.figure_data[attr] = f.read()

    request = ReportRequest(
        metadata=payload.metadata,
        options=payload.options,
        output_dir=args.output_dir,
        file_stem=args.stem,
    )

    print(f"Generating report: {args.stem}...")
    print(f"Output dir: {args.output_dir}")
    result = generate_report(payload, request)

    if result.pdf_path and os.path.exists(result.pdf_path):
        size = os.path.getsize(result.pdf_path)
        print(f"\u2713 PDF generated: {result.pdf_path} ({size:,} bytes)")
    else:
        print("\u2717 PDF was NOT generated.")
        if result.tex_path and os.path.exists(result.tex_path):
            print(f"  .tex file saved: {result.tex_path}")
            log_path = result.tex_path.replace('.tex', '.log')
            if os.path.exists(log_path):
                print(f"\n  Last 50 lines of {log_path}:")
                with open(log_path) as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        print(f"    {line.rstrip()}")

    if result.tex_path and os.path.exists(result.tex_path):
        print(f"  .tex source: {result.tex_path}")

    return 0 if (result.pdf_path and os.path.exists(result.pdf_path)) else 1


if __name__ == '__main__':
    sys.exit(main())
