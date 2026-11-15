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
        'steel_girders_vol_formula': '4 girders x 30m x 0.032 m\u00b2/m',
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

        # Analysis summary
        'analysis_summary': {
            'max_bm': '4250 kN-m', 'max_sf': '580 kN', 'max_defl': '12.5 mm',
        },

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
