#!/usr/bin/env python3
"""
test_report.py — Headless test script for OsdagBridge report generation.

Constructs a mock ReportPayload with sample bridge data and calls
generate_report() to produce a PDF + .tex without running the GUI or solver.

Usage:
    cd "/home/rithan/iitb OSDAG/OsdagBridge"
    source /home/rithan/iitb\ OSDAG/myenv/bin/activate
    python -m test_report [--output-dir DIR] [--stem NAME]
"""

import sys, os, types

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ── Mock unavailable heavy modules ──
# openseespy, PySide6, and pythonOCC are not installed in the headless env.
# Create stub modules so imports don't fail.
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

    # Build a comprehensive input_dict with all keys the chapters expect
    input_dict = {
        # Project info
        'project.location': "Pune, Maharashtra",
        'latitude': '18.52',
        'longitude': '73.85',

        # Typical section
        'typical_section.no_of_girders': 4,
        'typical_section.girder_spacing': '2.5',
        'typical_section.deck_overhang': '1.25',
        'typical_section.overall_width': '10.0',
        'typical_section.deck_thickness': '250',
        'typical_section.no_of_footpaths': 1,
        'typical_section.footpath_width': '1.5',
        'typical_section.footpath_thickness': '0.15',

        # Span
        'project_information.span': '30.0',

        # Material
        'material.girder_density': '78.5',
        'material.deck_density': '25.0',
        'material.steel_grade': 'E 350 (Fe 490)',

        # Loading
        'permanent_load.self_weight_factor': '1.00',

        # Live loads — all vehicle types enabled
        'live_load.irc_class_a': True,
        'live_load.irc_70r_wheeled': True,
        'live_load.irc_70r_tracked': True,
        'live_load.irc_aa_wheeled': True,
        'live_load.irc_aa_tracked': True,
        'live_load.irc_class_sv': True,
        'live_load.irc_70r_bogie': True,
        'live_load.irc_class_fatigue': True,
        'live_load.custom_vehicles': [],
        'live_load.eccentricity': '1.2',
        'live_load.footpath_pressure_mode': 'As per IRC 6',
        'live_load.footpath_pressure_value': '',

        # Crash barrier
        'crash_barrier.type': 'IRC 5 - RCC Crash Barrier',
        'crash_barrier.load': '7.5',

        # Railing
        'railing.load_value': '1.47',

        # Wearing course
        'wearing_course.material': 'Concrete',
        'wearing_course.thickness': '50.0',

        # Wind load
        'wind_speed': '39',
        'wind_load.terrain_type': 'Plain Terrain',
        'wind_load.avg_exposed_height': '10',
        'wind_load.hourly_mean_wind': '30.5',
        'wind_load.hourly_wind_pressure': '560.0',
        'wind_load.transverse_wind_force': '45.2',
        'wind_load.longitudinal_wind_force': '15.6',
        'wind_load.vertical_wind_force': '22.1',

        # Seismic load
        'seismic_zone': 'IV',
        'seismic_load.zone_factor': '0.24',
        'seismic_load.importance_factor': '1.5',
        'seismic_load.soil_type': 'Type II – Medium Soil',
        'seismic_load.spectral_coeff': '2.50',
        'seismic_load.horizontal_coeff': '0.12',
        'seismic_load.vertical_coeff': '0.08',
        'seismic_load.time_period': '0.5',
        'seismic_load.damping': '2',
        'seismic_load.dead_load_mode': 'Automatic',
        'seismic_load.dead_load_value': '',
        'seismic_load.live_load_mode': 'Automatic',
        'seismic_load.live_load_value': '',

        # Temperature
        'shade_temp_max': '47.5',
        'shade_temp_min': '2.0',
        'temperature_load.bridge_temp_min': '5.0',
        'temperature_load.bridge_temp_max': '55.0',
        'temperature_load.temp_rise': '25.0',
        'temperature_load.temp_fall': '22.5',

        # Lane count
        'wearing_course.lane_table_count': '2',

        # Girder details  (simplified for 4 girders)
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

        # Cross bracing details
        'cross_bracing': 'Yes',
        'member_properties.cross_bracing_details.no_of_cross_bracings': 3,
        'member_properties.cross_bracing_details.type.G1G2.B1M1': 'X-bracing',
        'member_properties.cross_bracing_details.bracing_section_designation.G1G2.B1M1': 'IS 100 x 100 x 10',
        'member_properties.cross_bracing_details.spacing.G1G2.B1M1': '7.5',
        'member_properties.cross_bracing_details.select_girders.G1G2.B1M1': 'G1 to G2',
        'member_properties.cross_bracing_details.member_id.G1G2.B1M1': 'B1M1 to B1M3',

        # End diaphragm details
        'end_diaphragm': 'Yes',
        'member_properties.end_diaphragm_details.type.G1G2.E1M1': 'Cross Bracing',
        'member_properties.end_diaphragm_details.bracing_section_designation.G1G2.E1M1': 'IS 100 x 100 x 10',
        'member_properties.end_diaphragm_details.select_girders.G1G2.E1M1': 'G1 to G2',
        'member_properties.end_diaphragm_details.member_id.G1G2.E1M1': 'E1M1 to E1M2',

        # Partial safety factors
        'design_options_cont.gamma_c_basic': '1.50',
        'design_options_cont.gamma_m0': '1.10',
        'design_options_cont.gamma_m1': '1.25',
        'design_options_cont.gamma_s': '1.15',
        'design_options_cont.gamma_v': '1.25',
        'design_options_cont.gamma_flt': '1.00',
        'design_options_cont.gamma_mf': '1.35',

        # Shear connector
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

        # BOQ quantities (normally computed by boq_generator)
        'steel_girders_vol_formula': '4 × 30m × 0.032m²',
        'steel_girders_qty': '4',
        'steel_girders_vol_total': '3.84',
        'steel_girders_wt_single': '7.52',
        'steel_girders_wt_total': '30.08',
        'bracing_top_vol_formula': '6 × 2.5m × 0.002m²',
        'bracing_top_qty': '6',
        'bracing_top_vol_total': '0.03',
        'bracing_top_wt_single': '0.04',
        'bracing_top_wt_total': '0.24',
        'bracing_bot_vol_formula': '6 × 2.5m × 0.002m²',
        'bracing_bot_qty': '6',
        'bracing_bot_vol_total': '0.03',
        'bracing_bot_wt_single': '0.04',
        'bracing_bot_wt_total': '0.24',
        'bracing_diag_vol_formula': '6 × 2.8m × 0.002m²',
        'bracing_diag_qty': '12',
        'bracing_diag_vol_total': '0.067',
        'bracing_diag_wt_single': '0.044',
        'bracing_diag_wt_total': '0.53',
        'concrete_deck_vol_formula': '30m × 10m × 0.25m',
        'concrete_deck_qty': '1',
        'concrete_deck_vol_total': '75.0',
        'concrete_deck_wt_single': '187.5',
        'concrete_deck_wt_total': '187.5',
        'rebar_deck_vol_formula': '~1.5% of 75m³',
        'rebar_deck_qty': '1',
        'rebar_deck_vol_total': '1.125',
        'rebar_deck_wt_single': '8.83',
        'rebar_deck_wt_total': '8.83',
        'shear_studs_vol_formula': 'π(10)²×100mm per stud',
        'shear_studs_qty': '600',
        'shear_studs_vol_total': '0.019',
        'shear_studs_wt_single': '0.00025',
        'shear_studs_wt_total': '0.15',
        'crash_barrier_vol_formula': '2 × 30m × 0.16m²',
        'crash_barrier_qty': '2',
        'crash_barrier_vol_total': '9.6',
        'crash_barrier_wt_single': '120.0',
        'crash_barrier_wt_total': '240.0',

        # Design mode
        'design_mode': 'Optimized',
    }

    # Build output_dict with sample design checks and UR data
    output_dict = {
        'overall_design_status': 'PASS',
        'governing_check': 'Flexure at Midspan',
        'overall_utilization_ratio': '0.87',
        'section_designation': 'ISWB 1200',

        # Category URs for the UR chart
        'category_urs': {
            'flexure': 0.87,
            'shear': 0.62,
            'interaction': 0.78,
            'ltb': 0.45,
            'fatigue': 0.55,
        },

        # Deck slab UR
        'deck_ur': 0.72,

        # Cross bracing design results
        'crossbracing_forces_dict': {
            'geometry': {
                'diagonal_length_m': 2.8,
                'horiz_proj_m': 2.5,
                'alpha_deg': 63.43,
            },
            'brace_type': 'X',
            'pairs': {
                'G1-G2': {
                    'diag_tension_kN': 45.2,
                    'diag_compression_kN': -38.6,
                    'chord_tension_kN': 22.1,
                    'chord_compression_kN': -18.9,
                },
                'G2-G3': {
                    'diag_tension_kN': 42.8,
                    'diag_compression_kN': -36.1,
                    'chord_tension_kN': 20.5,
                    'chord_compression_kN': -17.2,
                },
                'G3-G4': {
                    'diag_tension_kN': 44.0,
                    'diag_compression_kN': -37.5,
                    'chord_tension_kN': 21.3,
                    'chord_compression_kN': -18.1,
                },
            }
        },
        'crossbracing_design_results': {
            'G1-G2': {
                'diagonal': {
                    'tension': {
                        'section': 'IS 100 x 100 x 10',
                        'capacity_kN': 180.5,
                        'efficiency': 0.25,
                        'slenderness': 85.2,
                        'connection': 'Bolted',
                    },
                    'compression': {
                        'section': 'IS 100 x 100 x 10',
                        'capacity_kN': 120.3,
                        'efficiency': 0.32,
                        'slenderness': 85.2,
                        'connection': 'Bolted',
                    },
                },
                'chord': {
                    'tension': {
                        'section': 'IS 100 x 100 x 10',
                        'capacity_kN': 180.5,
                        'efficiency': 0.12,
                        'slenderness': 65.0,
                        'connection': 'Bolted',
                    },
                    'compression': {
                        'section': 'IS 100 x 100 x 10',
                        'capacity_kN': 120.3,
                        'efficiency': 0.16,
                        'slenderness': 65.0,
                        'connection': 'Bolted',
                    },
                },
            },
            'G2-G3': {
                'diagonal': {
                    'tension': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 180.5, 'efficiency': 0.24, 'slenderness': 85.2, 'connection': 'Bolted'},
                    'compression': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 120.3, 'efficiency': 0.30, 'slenderness': 85.2, 'connection': 'Bolted'},
                },
                'chord': {
                    'tension': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 180.5, 'efficiency': 0.11, 'slenderness': 65.0, 'connection': 'Bolted'},
                    'compression': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 120.3, 'efficiency': 0.14, 'slenderness': 65.0, 'connection': 'Bolted'},
                },
            },
            'G3-G4': {
                'diagonal': {
                    'tension': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 180.5, 'efficiency': 0.24, 'slenderness': 85.2, 'connection': 'Bolted'},
                    'compression': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 120.3, 'efficiency': 0.31, 'slenderness': 85.2, 'connection': 'Bolted'},
                },
                'chord': {
                    'tension': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 180.5, 'efficiency': 0.12, 'slenderness': 65.0, 'connection': 'Bolted'},
                    'compression': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 120.3, 'efficiency': 0.15, 'slenderness': 65.0, 'connection': 'Bolted'},
                },
            },
        },

        # End diaphragm (same structure)
        'enddiaphragm_design_results': {
            'G1-G2': {
                'diagonal': {
                    'tension': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 180.5, 'efficiency': 0.22, 'slenderness': 82.0, 'connection': 'Bolted'},
                    'compression': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 120.3, 'efficiency': 0.28, 'slenderness': 82.0, 'connection': 'Bolted'},
                },
                'chord': {
                    'tension': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 180.5, 'efficiency': 0.10, 'slenderness': 60.0, 'connection': 'Bolted'},
                    'compression': {'section': 'IS 100 x 100 x 10', 'capacity_kN': 120.3, 'efficiency': 0.14, 'slenderness': 60.0, 'connection': 'Bolted'},
                },
            },
        },

        # Design checks list (for Table 5.22)
        'design_checks': [
            {'check': 'Flexure (Midspan)', 'ur': 0.87, 'demand': '4250 kN·m', 'capacity': '4885 kN·m', 'lc': 'ULS-01'},
            {'check': 'Shear (Support)', 'ur': 0.62, 'demand': '580 kN', 'capacity': '935 kN', 'lc': 'ULS-03'},
            {'check': 'Interaction', 'ur': 0.78, 'demand': '0.78', 'capacity': '1.00', 'lc': 'ULS-01'},
            {'check': 'LTB', 'ur': 0.45, 'demand': '2200 kN·m', 'capacity': '4885 kN·m', 'lc': 'ULS-05'},
            {'check': 'Fatigue', 'ur': 0.55, 'demand': '65 MPa', 'capacity': '118 MPa', 'lc': 'SLS-01'},
        ],

        # Analysis summary
        'analysis_summary': {
            'max_bm': '4250 kN·m',
            'max_sf': '580 kN',
            'max_defl': '12.5 mm',
        },

        # Design log
        'design_log': [
            'Stage 1: Initial sizing complete — D=1200mm, tw=12mm',
            'Stage 2: Flange sizing — tf=25mm, bf=400mm',
            'Stage 3: Section properties computed',
            'Stage 4: Loading analysis complete',
            'Stage 5: ULS checks passed',
            'Stage 6: SLS checks passed',
            'Stage 7: Stiffener design complete',
            'Stage 8: Cross bracing design complete',
            'Stage 9: Deck slab design complete',
            'Stage 10: Shear connector design complete',
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
        print(f"✓ PDF generated: {result.pdf_path} ({size:,} bytes)")
    else:
        print("✗ PDF was NOT generated.")
        if result.tex_path and os.path.exists(result.tex_path):
            print(f"  .tex file saved: {result.tex_path}")
            # Show last 30 lines of pdflatex log if available
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

