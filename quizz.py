# app.py - Manufacturing Technology Quiz System

import streamlit as st
import json
import random
import datetime
import pandas as pd
from io import BytesIO
import time

# --- Third-party libraries ---
import gspread
from streamlit_js_eval import streamlit_js_eval
from streamlit_autorefresh import st_autorefresh

# --- PDF Generation Libraries ---
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# =====================================================================================
# --- 📝 CONFIGURATION & CONSTANTS ---
# =====================================================================================
APP_TITLE = "Department of Mechanical Quiz System"
COURSE_NAME = "Unconventional Machining Process for Third year and 20MEP36 Design of Jigs, Fixture and Press Tools for final"
QUESTIONS_PER_QUIZ = 20
QUIZ_DURATION_MINUTES = 7
QUIZ_DURATION_SECONDS = QUIZ_DURATION_MINUTES * 60
ADMIN_USERNAME = "immangwu"
ADMIN_PASSWORD = "jesus"

# =====================================================================================
# --- 🧠 QUESTION BANKS ---
# =====================================================================================

# THIRD YEAR QUIZZES
# Quiz 2: Chemical and Electrochemical Processes
THIRD_YEAR_QUIZ2_BANK = [
    {"id": 1, "question": "Chemical machining (CHM) removes material by:", "options": ["Mechanical cutting action", "Chemical dissolution", "Thermal melting", "Electrical discharge"], "correct": 1},
    {"id": 2, "question": "The most commonly used etchant for steel in chemical machining is:", "options": ["Hydrochloric acid", "Nitric acid", "Ferric chloride", "Sodium hydroxide"], "correct": 2},
    {"id": 3, "question": "The maskant in chemical machining is used to:", "options": ["Accelerate etching", "Protect areas from etching", "Control temperature", "Neutralize the etchant"], "correct": 1},
    {"id": 4, "question": "Photo-chemical machining (PCM) is particularly suitable for:", "options": ["Thick plates only", "Thin sheets with complex patterns", "Large components", "Hard materials only"], "correct": 1},
    {"id": 5, "question": "The typical thickness range for chemical machining is:", "options": ["10-100 mm", "5-25 mm", "0.025-6 mm", "0.001-0.01 mm"], "correct": 2},
    {"id": 6, "question": "Which factor does NOT affect the etching rate in chemical machining?", "options": ["Etchant concentration", "Temperature", "Material hardness", "Agitation"], "correct": 2},
    {"id": 7, "question": "The main advantage of chemical machining is:", "options": ["High material removal rate", "No tool wear", "High surface finish", "Low cost setup"], "correct": 1},
    {"id": 8, "question": "Undercut in chemical machining refers to:", "options": ["Deep etching", "Lateral etching under the mask", "Incomplete etching", "Surface roughness"], "correct": 1},
    {"id": 9, "question": "Chemical blanking is used for:", "options": ["Surface texturing", "Cutting complex shapes from thin sheets", "Deep hole drilling", "Surface hardening"], "correct": 1},
    {"id": 10, "question": "The main limitation of chemical machining is:", "options": ["High tooling cost", "Limited to soft materials", "Disposal of chemical waste", "Low accuracy"], "correct": 2},
    {"id": 11, "question": "Electrochemical machining works on the principle of:", "options": ["Faraday's law of electrolysis", "Ohm's law", "Newton's law", "Hooke's law"], "correct": 0},
    {"id": 12, "question": "In ECM, the workpiece acts as:", "options": ["Cathode (negative electrode)", "Anode (positive electrode)", "Neutral electrode", "Ground electrode"], "correct": 1},
    {"id": 13, "question": "The tool electrode in ECM is typically made of:", "options": ["High-speed steel", "Carbide", "Copper or brass", "Aluminum"], "correct": 2},
    {"id": 14, "question": "The electrolyte commonly used in ECM of steel is:", "options": ["Sulfuric acid", "Sodium chloride solution", "Hydrochloric acid", "Distilled water"], "correct": 1},
    {"id": 15, "question": "The typical current density in ECM ranges from:", "options": ["1-5 A/cm²", "10-100 A/cm²", "200-500 A/cm²", "1000-2000 A/cm²"], "correct": 1},
    {"id": 16, "question": "The gap between tool and workpiece in ECM is typically:", "options": ["0.1-0.5 mm", "1-5 mm", "10-20 mm", "25-50 mm"], "correct": 0},
    {"id": 17, "question": "The main function of electrolyte flow in ECM is to:", "options": ["Provide electrical conductivity only", "Remove heat and reaction products", "Lubricate the process", "Increase current density"], "correct": 1},
    {"id": 18, "question": "ECM produces:", "options": ["High surface roughness", "Smooth, stress-free surfaces", "Work-hardened surfaces", "Thermally affected zones"], "correct": 1},
    {"id": 19, "question": "The material removal rate in ECM is proportional to:", "options": ["Voltage only", "Current only", "Current and time", "Temperature only"], "correct": 2},
    {"id": 20, "question": "ECM is particularly suitable for:", "options": ["Soft materials only", "Hard, difficult-to-machine materials", "Non-conductive materials", "Brittle materials only"], "correct": 1},
    {"id": 21, "question": "Increasing the voltage in ECM results in:", "options": ["Decreased material removal rate", "Increased material removal rate", "No effect on removal rate", "Better surface finish only"], "correct": 1},
    {"id": 22, "question": "The feed rate in ECM must be controlled to:", "options": ["Maximize cutting forces", "Maintain constant gap", "Minimize current", "Increase tool wear"], "correct": 1},
    {"id": 23, "question": "ECM is commonly used for machining:", "options": ["Turbine blades", "Die cavities", "Forging dies", "All of the above"], "correct": 3},
    {"id": 24, "question": "The accuracy achievable in ECM is typically:", "options": ["±0.001 mm", "±0.025 mm", "±0.1 mm", "±1.0 mm"], "correct": 1},
    {"id": 25, "question": "Electrochemical honing combines:", "options": ["ECM and grinding", "ECM and honing", "Chemical machining and honing", "EDM and honing"], "correct": 1},
    {"id": 26, "question": "In electrochemical grinding, material removal occurs by:", "options": ["Grinding action only", "Electrochemical dissolution only", "Combined grinding and electrochemical action", "Chemical dissolution only"], "correct": 2},
    {"id": 27, "question": "The grinding wheel in ECG is:", "options": ["Conventional abrasive wheel", "Conductive abrasive wheel", "Diamond wheel only", "CBN wheel only"], "correct": 1},
    {"id": 28, "question": "The typical percentage of material removal by electrochemical action in ECG is:", "options": ["10-20%", "50-70%", "80-95%", "100%"], "correct": 2},
    {"id": 29, "question": "Electrochemical deburring is used to:", "options": ["Create burrs", "Remove burrs selectively", "Harden edges", "Create sharp edges"], "correct": 1},
    {"id": 30, "question": "The main limitation of electrochemical processes is:", "options": ["Limited to conductive materials", "High tooling cost", "Low accuracy", "High surface roughness"], "correct": 0}
]

# Quiz 3: Nano Finishing Processes
THIRD_YEAR_QUIZ3_BANK = [
    {"id": 1, "question": "Abrasive Flow Machining (AFM) uses:", "options": ["Solid abrasive tools", "Liquid abrasive medium", "Viscoelastic abrasive medium", "Gaseous abrasive medium"], "correct": 2},
    {"id": 2, "question": "The abrasive medium in AFM typically consists of:", "options": ["Polymer base with abrasive particles", "Water with suspended abrasives", "Oil with metallic particles", "Air with abrasive powder"], "correct": 0},
    {"id": 3, "question": "In AFM, material removal occurs due to:", "options": ["Impact of abrasive particles", "Rubbing action of flowing abrasive medium", "Chemical reaction", "Electrical discharge"], "correct": 1},
    {"id": 4, "question": "The typical abrasive particle size used in AFM ranges from:", "options": ["1-10 mm", "100-500 μm", "5-200 μm", "0.1-1 μm"], "correct": 2},
    {"id": 5, "question": "AFM is particularly suitable for finishing:", "options": ["External flat surfaces", "Internal complex passages and cavities", "Large flat components", "Soft materials only"], "correct": 1},
    {"id": 6, "question": "The flow pressure in AFM typically ranges from:", "options": ["0.1-0.5 MPa", "1-7 MPa", "10-50 MPa", "100-200 MPa"], "correct": 1},
    {"id": 7, "question": "Two-way AFM involves:", "options": ["Using two different abrasives", "Processing two workpieces simultaneously", "Flow in both directions through the workpiece", "Two-stage finishing process"], "correct": 2},
    {"id": 8, "question": "AFM can achieve surface finish of:", "options": ["Ra 5-10 μm", "Ra 1-5 μm", "Ra 0.1-1 μm", "Ra 0.01-0.1 μm"], "correct": 3},
    {"id": 9, "question": "The main advantage of AFM over conventional finishing is:", "options": ["Higher material removal rate", "Lower cost", "Ability to finish complex internal geometries", "No need for skilled operators"], "correct": 2},
    {"id": 10, "question": "Chemical Mechanical Polishing combines:", "options": ["Chemical etching and grinding", "Chemical reaction and mechanical abrasion", "Electrochemical action and polishing", "Thermal treatment and polishing"], "correct": 1},
    {"id": 11, "question": "CMP is extensively used in:", "options": ["Automotive industry", "Semiconductor wafer processing", "Aerospace industry", "Medical device manufacturing"], "correct": 1},
    {"id": 12, "question": "The polishing pad in CMP is typically made of:", "options": ["Metal", "Ceramic", "Polyurethane", "Diamond"], "correct": 2},
    {"id": 13, "question": "The slurry in CMP contains:", "options": ["Abrasive particles only", "Chemical etchants only", "Both abrasive particles and chemicals", "Water only"], "correct": 2},
    {"id": 14, "question": "The typical abrasive used in silicon CMP is:", "options": ["Aluminum oxide", "Silicon carbide", "Silica (SiO₂)", "Diamond"], "correct": 2},
    {"id": 15, "question": "The main advantage of CMP is:", "options": ["High material removal rate", "Global planarization capability", "Low cost", "Simple equipment"], "correct": 1},
    {"id": 16, "question": "In Magnetic Abrasive Finishing, the abrasive particles are:", "options": ["Non-magnetic particles only", "Magnetic particles only", "Ferromagnetic abrasive particles", "Diamagnetic particles"], "correct": 2},
    {"id": 17, "question": "The magnetic field in MAF is used to:", "options": ["Heat the workpiece", "Control abrasive particle motion and pressure", "Generate electric current", "Magnetize the workpiece"], "correct": 1},
    {"id": 18, "question": "MAF can achieve surface roughness of:", "options": ["Ra 1-5 μm", "Ra 0.1-1 μm", "Ra 0.01-0.1 μm", "Ra < 0.01 μm"], "correct": 3},
    {"id": 19, "question": "Magnetorheological fluid consists of:", "options": ["Magnetic particles in water", "Magnetic particles in carrier fluid", "Non-magnetic abrasives only", "Ferrofluid without abrasives"], "correct": 1},
    {"id": 20, "question": "In MRF, the rheological properties change due to:", "options": ["Temperature variation", "Pressure changes", "Applied magnetic field", "Chemical reactions"], "correct": 2},
    {"id": 21, "question": "MRF is extensively used for finishing:", "options": ["Automotive parts", "Optical components and precision surfaces", "Large structural components", "Textile machinery"], "correct": 1},
    {"id": 22, "question": "MRF can achieve surface finish of:", "options": ["Ra 1-10 nm", "Ra 100-500 nm", "Ra 1-5 μm", "Ra 10-50 μm"], "correct": 0},
    {"id": 23, "question": "The main application of MRF is in:", "options": ["Mass production finishing", "Precision finishing of optical surfaces", "Rough machining operations", "Heavy material removal"], "correct": 1},
    {"id": 24, "question": "MRAFF combines the principles of:", "options": ["AFM and electrochemical machining", "AFM and magnetorheological effect", "Chemical machining and magnetic finishing", "Ultrasonic machining and magnetic fields"], "correct": 1},
    {"id": 25, "question": "In MRAFF, the abrasive medium contains:", "options": ["Only magnetic particles", "Only abrasive particles", "Both magnetic and abrasive particles", "Chemical etchants only"], "correct": 2},
    {"id": 26, "question": "The magnetic field in MRAFF is used to:", "options": ["Heat the abrasive medium", "Control the flow characteristics and finishing pressure", "Magnetize the workpiece", "Generate electric current"], "correct": 1},
    {"id": 27, "question": "MRAFF is particularly suitable for:", "options": ["External surface finishing", "Complex internal passages with variable geometry", "Large flat surfaces", "Non-metallic materials only"], "correct": 1},
    {"id": 28, "question": "The main advantage of MRAFF over conventional AFM is:", "options": ["Lower cost", "Better control over finishing process", "Higher material removal rate", "Simpler equipment"], "correct": 1},
    {"id": 29, "question": "MRAFF can be applied to finish:", "options": ["Straight holes only", "Curved passages only", "Both straight and curved internal passages", "External surfaces only"], "correct": 2},
    {"id": 30, "question": "The surface finish achievable by MRAFF is:", "options": ["Ra 1-5 μm", "Ra 0.1-1 μm", "Ra 0.01-0.1 μm", "Ra < 0.01 μm"], "correct": 3}
]

# Quiz 4: Hybrid Non-Traditional Machining
THIRD_YEAR_QUIZ4_BANK = [
    {"id": 1, "question": "Hybrid non-traditional machining processes combine:", "options": ["Two conventional machining methods", "Two or more different energy sources for material removal", "Traditional and conventional machining only", "Multiple cutting tools"], "correct": 1},
    {"id": 2, "question": "The main advantage of hybrid machining processes is:", "options": ["Lower cost", "Simpler equipment", "Synergistic effects leading to improved performance", "Reduced power consumption"], "correct": 2},
    {"id": 3, "question": "Which of the following is NOT a hybrid machining process?", "options": ["EDM + USM", "ECM + USM", "Laser + EDM", "Conventional turning"], "correct": 3},
    {"id": 4, "question": "Hybrid processes are developed to overcome:", "options": ["High cost of single processes", "Limitations of individual processes", "Complexity of equipment", "Operator skill requirements"], "correct": 1},
    {"id": 5, "question": "The selection of hybrid processes depends on:", "options": ["Material properties only", "Required surface finish only", "Material properties, geometry, and quality requirements", "Cost considerations only"], "correct": 2},
    {"id": 6, "question": "Hybrid machining processes typically result in:", "options": ["Higher material removal rates", "Better surface finish", "Improved accuracy", "All of the above"], "correct": 3},
    {"id": 7, "question": "Ultrasonic-assisted EDM (US-EDM) combines:", "options": ["Ultrasonic and electrical discharge", "Ultrasonic and electrochemical action", "Ultrasonic and laser energy", "Ultrasonic and plasma cutting"], "correct": 0},
    {"id": 8, "question": "The typical frequency used in ultrasonic-assisted machining is:", "options": ["50-100 Hz", "1-5 kHz", "20-40 kHz", "100-200 kHz"], "correct": 2},
    {"id": 9, "question": "In US-EDM, ultrasonic vibration helps in:", "options": ["Increasing discharge energy", "Better debris removal and reduced tool wear", "Generating more heat", "Increasing electrical resistance"], "correct": 1},
    {"id": 10, "question": "Ultrasonic-assisted ECM (US-ECM) improves:", "options": ["Current density distribution", "Electrolyte circulation", "Surface finish and accuracy", "All of the above"], "correct": 3},
    {"id": 11, "question": "The amplitude of ultrasonic vibration in hybrid processes is typically:", "options": ["1-5 μm", "10-50 μm", "100-500 μm", "1-5 mm"], "correct": 1},
    {"id": 12, "question": "Laser-assisted machining (LAM) preheats the material to:", "options": ["Melt the entire workpiece", "Reduce cutting forces and tool wear", "Increase hardness", "Create thermal stresses"], "correct": 1},
    {"id": 13, "question": "In laser-assisted turning, the laser beam is positioned:", "options": ["Behind the cutting tool", "Ahead of the cutting tool", "Perpendicular to cutting direction", "Away from the cutting zone"], "correct": 1},
    {"id": 14, "question": "LAM is particularly beneficial for machining:", "options": ["Soft metals", "Hard-to-machine materials like ceramics", "Plastics", "Wood materials"], "correct": 1},
    {"id": 15, "question": "The typical temperature rise in LAM ranges from:", "options": ["50-100°C", "200-500°C", "800-1200°C", "2000-3000°C"], "correct": 2},
    {"id": 16, "question": "Vibration-assisted machining introduces:", "options": ["Random vibrations only", "Controlled oscillatory motion to tool or workpiece", "High-frequency noise", "Thermal vibrations"], "correct": 1},
    {"id": 17, "question": "In vibration-assisted EDM, the electrode vibration:", "options": ["Increases discharge gap", "Improves debris removal and surface finish", "Reduces electrical conductivity", "Increases tool wear"], "correct": 1},
    {"id": 18, "question": "The typical frequency range for vibration-assisted machining is:", "options": ["0.1-1 Hz", "50-500 Hz", "1-50 kHz", "100-500 kHz"], "correct": 1},
    {"id": 19, "question": "Vibration-assisted turning results in:", "options": ["Increased cutting forces", "Reduced cutting forces and better chip formation", "Poor surface finish", "Increased tool wear"], "correct": 1},
    {"id": 20, "question": "EDM + ECM process combines:", "options": ["Electrical discharge and electrochemical dissolution", "Two different electrical processes", "Mechanical and thermal energy", "Chemical and thermal energy"], "correct": 0},
    {"id": 21, "question": "In combined EDM-ECM, material removal occurs by:", "options": ["EDM action only during discharge", "ECM action only during off-time", "Both EDM and ECM actions simultaneously", "Sequential EDM followed by ECM"], "correct": 2},
    {"id": 22, "question": "The main advantage of combined EDM-ECM is:", "options": ["Lower power consumption", "Reduced electrode wear and better surface finish", "Simpler equipment", "Lower processing time only"], "correct": 1},
    {"id": 23, "question": "Water-jet assisted laser cutting helps in:", "options": ["Increasing laser power", "Cooling and debris removal", "Focusing laser beam", "Generating laser"], "correct": 1},
    {"id": 24, "question": "In hybrid processes, the primary challenge is:", "options": ["High cost", "Controlling multiple process parameters simultaneously", "Equipment complexity", "Operator training"], "correct": 1},
    {"id": 25, "question": "The material removal rate in hybrid processes is typically:", "options": ["Lower than individual processes", "Same as individual processes", "Higher than individual processes", "Unpredictable"], "correct": 2},
    {"id": 26, "question": "Surface finish in hybrid processes is generally:", "options": ["Poorer than individual processes", "Same as individual processes", "Better than individual processes", "Variable and unpredictable"], "correct": 2},
    {"id": 27, "question": "The key to successful hybrid machining is:", "options": ["Using maximum energy levels", "Proper synchronization of different energy sources", "Operating at highest speeds", "Minimizing process parameters"], "correct": 1},
    {"id": 28, "question": "Hybrid machining processes are most suitable for:", "options": ["Mass production of simple parts", "Precision machining of advanced materials", "Rough machining operations", "Low-cost manufacturing"], "correct": 1},
    {"id": 29, "question": "The selection of a hybrid process depends on:", "options": ["Material properties", "Required accuracy and surface finish", "Production volume and cost", "All of the above"], "correct": 3},
    {"id": 30, "question": "The main limitation of hybrid processes is:", "options": ["Poor performance", "High equipment cost and complexity", "Limited applications", "Low accuracy"], "correct": 1}
]

# FINAL YEAR QUIZZES (Design of Jigs, Fixtures and Press Tools)
# Quiz 1
FINAL_YEAR_QUIZ1_BANK = [
    {"id": 1, "question": "Process of developing tools, methods and techniques to improve productivity is known as", "options": ["Machine design", "Engine design", "Tool design", "Pump design"], "correct": 2},
    {"id": 2, "question": "The device in which a component is held, located for a specific operation and guides one or more cutting tools during machining is known as", "options": ["Fixture", "Gauge", "Template", "Jig"], "correct": 3},
    {"id": 3, "question": "The device in which a component is held, located for a specific operation and does not guide cutting tools during machining is known as", "options": ["Fixture", "Gauge", "Template", "Jig"], "correct": 0},
    {"id": 4, "question": "The locator used to locate cylindrical components is", "options": ["V blocks", "Jig bushes", "Pins", "Surface plates"], "correct": 0},
    {"id": 5, "question": "Location and guiding of cutting tools such as twist drills and reamers were done by", "options": ["V blocks", "Jig bushes", "Pins", "Surface plates"], "correct": 1},
    {"id": 6, "question": "Clamping should always be arranged", "options": ["Directly above the points of supporting the work", "Directly below the points of supporting the work", "Directly above the points of supporting the tool", "Directly on the cutting tool"], "correct": 0},
    {"id": 7, "question": "The location which is to be used if the diameter of hole is in considerable variation is", "options": ["Cylindrical location", "V block location", "Pin location", "Conical location"], "correct": 3},
    {"id": 8, "question": "The application of jigs and fixtures", "options": ["Decreases the production", "Increases the production", "Requires skilled labour", "Decrease the accuracy in the components"], "correct": 1},
    {"id": 9, "question": "The main required property in the selection of material for locating pins used in the jigs and fixture is", "options": ["Shear strength", "Tensile strength", "Wear resistance", "Brittleness"], "correct": 2},
    {"id": 10, "question": "Devices designed for locating and holding cutting tools are called as", "options": ["Fixtures", "Tool holders", "Jigs", "Gauges"], "correct": 1},
    {"id": 11, "question": "In jigs and fixtures, holding and securing the work piece in the located position was done by", "options": ["Clamping elements", "Bush", "Locating elements", "Button"], "correct": 2},
    {"id": 12, "question": "In milling fixtures, position of the base on the table is accurately located by means of", "options": ["Clamp", "Bush", "Tenon strips", "Button"], "correct": 2},
    {"id": 13, "question": "Length of the tenon strip is", "options": ["Twice its depth", "Twice its width", "Thrice its width", "Thrice its depth"], "correct": 1},
    {"id": 14, "question": "Tenon strips are made of", "options": ["Cast iron, case hardened and ground", "Stainless steel, case hardened and ground", "Carbon steel, case hardened and ground", "Aluminum, case hardened and ground"], "correct": 2},
    {"id": 15, "question": "Two tenons should be kept", "options": ["As close as each other", "As apart as each other", "Touching each other", "Overlapping each other"], "correct": 1},
    {"id": 16, "question": "Jig is used for", "options": ["Drilling, reaming and tapping", "Milling and grinding", "Shaping and turning", "Honing and lapping"], "correct": 0},
    {"id": 17, "question": "Fixture is used for", "options": ["Drilling", "Reaming", "Tapping", "Broaching"], "correct": 3},
    {"id": 18, "question": "Clamp which holds the blank during machining need to be", "options": ["Loose", "Strong and rigid", "Weak", "Flexible"], "correct": 1},
    {"id": 19, "question": "The number of degrees of freedom for any work piece in space are", "options": ["12", "3", "6", "1"], "correct": 2},
    {"id": 20, "question": "The minimum number of locators required to locate the workpiece are", "options": ["2", "3", "6", "1"], "correct": 1}
]

# Quiz 2
FINAL_YEAR_QUIZ2_BANK = [
    {"id": 1, "question": "Locating pins of longer length are called", "options": ["Shaft", "Set screws", "Plugs", "Bush"], "correct": 2},
    {"id": 2, "question": "Buttons are used for", "options": ["Vertical location", "Horizontal location", "Inclined location", "Semi angular location"], "correct": 1},
    {"id": 3, "question": "Locating pins are generally used in fixtures for", "options": ["Vertical location", "Horizontal location", "Inclined location", "Semi angular location"], "correct": 0},
    {"id": 4, "question": "The best method to locate a rough surface is to use", "options": ["Angular locators", "Horizontal locators", "Relieved locators", "Edge locators"], "correct": 2},
    {"id": 5, "question": "Drill bushes are made of", "options": ["High speed steel", "Low carbon steel", "High carbon steel, hardened and ground", "Aluminium"], "correct": 2},
    {"id": 6, "question": "Tenon strips are mounted to the base of milling fixture for the purpose of", "options": ["Locating the work piece", "Clamping the work piece", "Guiding the cutting tool", "Aligning the fixture on the machine table"], "correct": 3},
    {"id": 7, "question": "For stable location of a flat surface, the number of rest buttons required is", "options": ["2", "3", "5", "7"], "correct": 1},
    {"id": 8, "question": "The 3-2-1 scheme of location using rest pads is applicable to the location of", "options": ["Solid cylindrical parts", "Cylindrical parts with through hole", "Cylindrical parts with center hole", "Prismatic parts"], "correct": 3},
    {"id": 9, "question": "When a cylindrical work piece is placed on a V block, it is deprived of the following number of degrees of freedom", "options": ["2", "3", "5", "4"], "correct": 3},
    {"id": 10, "question": "A V block with 4 rest pins are used for location of", "options": ["Short cylindrical parts", "Finish machined long cylindrical parts", "Unmachined cylindrical parts", "Prismatic parts"], "correct": 0},
    {"id": 11, "question": "In shaft-basis system, the basis shaft is one", "options": ["whose upper deviation is zero", "whose upper and lower deviations are zero", "whose lower deviation is zero", "none of the above"], "correct": 2},
    {"id": 12, "question": "According to Indian standard, 50 H8-g7 means", "options": ["upper limit is (50+8) mm and lower limit (50-7) mm", "designation of tolerance with basic size 50 mm", "designation of fit of two parts with basic size 50 mm", "none of above"], "correct": 2},
    {"id": 13, "question": "According to Indian standard, total number of tolerance grades are", "options": ["10", "2", "18", "8"], "correct": 2},
    {"id": 14, "question": "According to Indian standard, 50 H8-g7 means tolerance grade for", "options": ["hole is 8 and for shaft is 7", "shaft is 8 and for hole is 7", "designation of fit on shaft-basis system", "none of above"], "correct": 0},
    {"id": 15, "question": "Jigs and Fixtures are used for", "options": ["Mass production", "Identical parts production", "Both A and B", "None of the above"], "correct": 2},
    {"id": 16, "question": "The use of jigs and fixtures", "options": ["Facilitates the deployment of less-skilled labor", "Eliminates pre-machining operations like marking", "Reduced manual handling operations", "All of the above"], "correct": 3},
    {"id": 17, "question": "The following is (are) the function(s) of a jig", "options": ["Holding", "Locating", "Guiding", "All of the above"], "correct": 3},
    {"id": 18, "question": "A fixture does not", "options": ["Holds the workpiece", "Locate the workpiece", "Guide the tool", "All of the above"], "correct": 2},
    {"id": 19, "question": "Jigs are not used in", "options": ["Drilling", "Reaming", "Tapping", "Milling"], "correct": 3},
    {"id": 20, "question": "Fixtures are used in", "options": ["Milling", "Shaping", "Turning", "All of the above"], "correct": 3}
]

# Quiz 3
FINAL_YEAR_QUIZ3_BANK = [
    {"id": 1, "question": "Which one of the following is used to guide the tool and hold the job in mass production?", "options": ["Gauge", "Housing", "Jig", "Fixture"], "correct": 2},
    {"id": 2, "question": "Which one of the following is used to clamp the job in relation to the tool in mass production?", "options": ["Gauge", "Edge clamping", "Jig", "Fixture"], "correct": 3},
    {"id": 3, "question": "Which one of the following device is used to fabricate a job by welding which is set in this device so that it can be swiveled around 360° as per requirement?", "options": ["Turning Fixture", "Welding Fixture", "Broaching Fixture", "Boring Fixture"], "correct": 1},
    {"id": 4, "question": "Usually drill jig is not clamped to the drilling machine table. Which among the following for this reason?", "options": ["It is rigid for this operation", "It is easy for the operation", "Number of holes of various sizes are being drilled in different settings", "It is a more time consuming device"], "correct": 2},
    {"id": 5, "question": "Which among the following locators is the best location of a round shaped component?", "options": ["Pin type locator", "Wedge type locator", "Vee Locator", "Adjustable stop locator"], "correct": 2},
    {"id": 6, "question": "Which among the following is the purpose of providing bushings in a drill jig?", "options": ["For easy drilling", "For determining the size of the hole to be drilled", "For locating accurately and guiding the drill for precise drilling operation", "For getting good finished surface in the drilled holes"], "correct": 2},
    {"id": 7, "question": "Drill jig bushings are generally made of", "options": ["Mild Steel", "Cast steel", "Cast Iron", "Tool steel"], "correct": 3},
    {"id": 8, "question": "Drill bushings are normally hardened to", "options": ["Protect the jig from damage", "Ensure prolonged life without wear and tear so as to guide the tool accurately", "Guide the tool so that it does not go inclined", "Allow the chips to come out easily"], "correct": 1},
    {"id": 9, "question": "Plain drill jig bushings are generally secured in the body of the jig so that the bushings should", "options": ["Not vibrate, rotate and be withdrawn while in operation", "Rotate when the tool is rotating", "Vibrate while in operation", "Get withdrawn with the tool"], "correct": 0},
    {"id": 10, "question": "The _______ bushings are used where multiple operations, such as drilling and reaming or drilling and tapping, are to be performed on the same hole", "options": ["Slip renewable", "Fixed renewable", "Oil-groove", "Template"], "correct": 0},
    {"id": 11, "question": "A jig is used to", "options": ["drill a hole", "locate and clamp a work piece", "locate, clamp the work piece and guide the cutting tool", "set the work piece for measurement"], "correct": 2},
    {"id": 12, "question": "Common feature between jig and fixture is that both are used for", "options": ["cutting the work piece", "holding the work piece", "locating the work piece", "testing and inspection of the work piece"], "correct": 2},
    {"id": 13, "question": "Slip bush is used in jig where", "options": ["the drill bit can slip on the work piece", "holes are too close", "the bush is to be replaced every time", "a liner is used along with bush"], "correct": 2},
    {"id": 14, "question": "Liner in a bush of a jig", "options": ["saves the bush from wear", "strengthens the bush", "offers lubrication", "aligns the bush in a hole"], "correct": 0},
    {"id": 15, "question": "A cam is used in a jig to", "options": ["locate the work piece", "lift a heavy work piece", "move the work piece frequently", "to clamp the work piece"], "correct": 3},
    {"id": 16, "question": "A turning fixture is used on the lathe", "options": ["to turn a non-symmetric job", "so that the surface finish of the work piece is not spoiled", "to turn the work piece which otherwise cannot be fitted on the lathe", "to turn long jobs"], "correct": 0},
    {"id": 17, "question": "An indexing jig is used to", "options": ["plane surfaces", "one angular settings", "multi angular settings", "multi plane settings"], "correct": 2},
    {"id": 18, "question": "The jigs and fixtures can be constructed through", "options": ["Casting", "Fabrication", "Welding", "All of the above"], "correct": 3},
    {"id": 19, "question": "The quickest clamping device is a", "options": ["wing nut", "knurled nut", "cam/eccentric", "Conventional nut"], "correct": 2},
    {"id": 20, "question": "A conical locater has the advantage of", "options": ["easy location", "self centering", "easy location and self-centering", "offers good grid"], "correct": 1}
]

# Quiz 4
FINAL_YEAR_QUIZ4_BANK = [
    {"id": 1, "question": "The operation of cutting of a flat sheet to the desired shape is called", "options": ["Shearing", "Piercing", "Punching", "Blanking"], "correct": 3},
    {"id": 2, "question": "Piercing is an operation of cutting", "options": ["a cylindrical hole in a sheet of metal by the punch and the die", "a hole (other than cylindrical) in a sheet of metal by the punch and the die", "a flat sheet to the desired shape", "a number of holes evenly spaced in a regular pattern on a sheet of metal"], "correct": 0},
    {"id": 3, "question": "In blanking operation, the clearance is provided on", "options": ["punch", "die", "half on the punch and half on the die", "either on a punch or die depending upon the designer's choice"], "correct": 0},
    {"id": 4, "question": "In piercing operation, the clearance is provided on", "options": ["punch", "die", "half on the punch and half on the die", "either on a punch or die depending upon the designer's choice"], "correct": 1},
    {"id": 5, "question": "Punching a number of holes in a sheet is known as?", "options": ["Perforating", "Parting", "Notching", "Lancing"], "correct": 0},
    {"id": 6, "question": "Shearing the sheet into two or more pieces is known as?", "options": ["Perforating", "Parting", "Notching", "Lancing"], "correct": 1},
    {"id": 7, "question": "Removing the pieces from the edge in shearing operation is known as?", "options": ["Perforating", "Parting", "Notching", "Lancing"], "correct": 2},
    {"id": 8, "question": "Leaving a tab without removing any material is known as?", "options": ["Perforating", "Parting", "Notching", "Lancing"], "correct": 3},
    {"id": 9, "question": "Moving a small straight punch up and down rapidly into a die is done by a process known as?", "options": ["Perforating", "Parting", "Nibbling", "Lancing"], "correct": 2},
    {"id": 10, "question": "As the thickness of the sheet is increased the clearance needed will also?", "options": ["Increase", "Decrease", "No effect", "First decreases and then increase"], "correct": 0},
    {"id": 11, "question": "Bevelling is particularly suitable for shearing of?", "options": ["Thin blanks", "Thick blanks", "Very thin blanks", "Medium thin blanks"], "correct": 1},
    {"id": 12, "question": "As the clearance increases, the punch force required?", "options": ["Decreases", "Increases", "Remains the same", "First increases and then decreases"], "correct": 0},
    {"id": 13, "question": "Lancing is the operation of", "options": ["cutting a sheet of metal in a straight line along the length", "removal of metal to the desired shape from the edge of a plate", "cutting a sheet of metal through part of its length and then bend the cut portion", "bending a sheet of metal along a curved axis"], "correct": 2},
    {"id": 14, "question": "Notching is the operation of", "options": ["cutting a sheet of metal in a straight line along the length", "removal of metal to the desired shape from the edge of a plate", "cutting a sheet of metal through part of its length and then bending the cut portion", "bending a sheet of metal along a curved axis"], "correct": 1},
    {"id": 15, "question": "The operation of straightening a curved sheet metal is known as", "options": ["drawing", "squeezing", "coining", "planishing"], "correct": 3},
    {"id": 16, "question": "The operation of bending a sheet of metal along a curved axis is known as", "options": ["plunging", "notching", "slitting", "forming"], "correct": 3},
    {"id": 17, "question": "During drawing operation, the states of stress in cup would include", "options": ["compressive stress in the flange", "tensile stress in the wall", "both (a) and (b)", "none of these"], "correct": 2},
    {"id": 18, "question": "The operation of producing cup-shaped parts from flat sheet metal blanks by bending and plastic flow of metal is known as", "options": ["drawing", "squeezing", "coining", "planishing"], "correct": 0},
    {"id": 19, "question": "Cutting and forming operations can be performed in a single operation in a", "options": ["simple die", "compound die", "combination die", "progressive die"], "correct": 1},
    {"id": 20, "question": "Which of the following methods of manufacturing is used for the production of appliances like the fridge and the vacuum cleaner?", "options": ["Forging", "Deep drawing", "Sheet metal forming and cutting", "Rolling"], "correct": 2}
]

# Quiz Banks Dictionary
QUIZ_BANKS = {
    "Third Year": {
        "Quiz 2: Chemical & Electrochemical Processes": THIRD_YEAR_QUIZ2_BANK,
        "Quiz 3: Nano Finishing Processes": THIRD_YEAR_QUIZ3_BANK,
        "Quiz 4: Hybrid Non-Traditional Machining": THIRD_YEAR_QUIZ4_BANK
    },
    "Final Year": {
        "Quiz 1: Tool Design & Jigs Basics": FINAL_YEAR_QUIZ1_BANK,
        "Quiz 2: Locating & Tolerance": FINAL_YEAR_QUIZ2_BANK,
        "Quiz 3: Drill Jigs & Fixtures": FINAL_YEAR_QUIZ3_BANK,
        "Quiz 4: Press Tools & Sheet Metal": FINAL_YEAR_QUIZ4_BANK
    }
}

# =====================================================================================
# --- ☁️ GOOGLE SHEETS HELPER FUNCTIONS ---
# =====================================================================================

def get_gspread_client():
    """Connects to Google Sheets using credentials from Streamlit secrets."""
    try:
        return gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheets: {e}")
        return None

def initialize_spreadsheet():
    """Initializes the spreadsheet with required sheets and headers."""
    try:
        client = get_gspread_client()
        if not client:
            return False
        
        spreadsheet = client.open_by_url(st.secrets["google_sheets"]["spreadsheet_url"])
        
        # Define required sheets for both years
        sheets_config = {
            # Third Year Sheets
            "ThirdYear_Quiz2": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "ThirdYear_Quiz3": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "ThirdYear_Quiz4": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            # Final Year Sheets
            "FinalYear_Quiz1": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "FinalYear_Quiz2": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "FinalYear_Quiz3": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "FinalYear_Quiz4": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            # Malpractice Logs
            "MalpracticeLogs": ["timestamp", "student_name", "register_number", "year", "quiz_name", "event"]
        }
        
        existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
        
        for sheet_name, headers in sheets_config.items():
            if sheet_name not in existing_sheets:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                worksheet.append_row(headers)
            else:
                worksheet = spreadsheet.worksheet(sheet_name)
                existing_headers = worksheet.row_values(1)
                if not existing_headers or existing_headers != headers:
                    worksheet.clear()
                    worksheet.append_row(headers)
        
        return True
    except Exception as e:
        st.error(f"❌ Error initializing spreadsheet: {e}")
        return False

def save_to_gsheet(sheet_name, data_dict):
    """Saves a dictionary of data as a new row in the specified Google Sheet."""
    try:
        client = get_gspread_client()
        if not client:
            return False
        
        spreadsheet = client.open_by_url(st.secrets["google_sheets"]["spreadsheet_url"])
        ws = spreadsheet.worksheet(sheet_name)
        header = ws.row_values(1)
        row_to_insert = [data_dict.get(key, "N/A") for key in header]
        ws.append_row(row_to_insert, value_input_option='USER_ENTERED')
        return True
    except Exception as e:
        st.error(f"❌ Could not write to Google Sheets: {e}")
        return False

def get_sheet_data(sheet_name):
    """Retrieves all data from a specified sheet."""
    try:
        client = get_gspread_client()
        if not client:
            return None
        
        spreadsheet = client.open_by_url(st.secrets["google_sheets"]["spreadsheet_url"])
        ws = spreadsheet.worksheet(sheet_name)
        return pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"❌ Error reading from sheet {sheet_name}: {e}")
        return None

# =====================================================================================
# --- 📄 PDF GENERATION FUNCTIONS ---
# =====================================================================================

def create_results_pdf(session_data):
    """Generates a detailed PDF report for a single student."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['h1'], alignment=TA_CENTER, fontSize=18, textColor=colors.HexColor('#1f4788'))
    story.append(Paragraph(COURSE_NAME, title_style))
    story.append(Paragraph(f"{session_data.get('quiz_name', 'Quiz')} - Performance Report", styles['h2']))
    story.append(Spacer(1, 0.25 * inch))
    
    student_info = [
        ['Student Name:', session_data.get('student_name', 'N/A')],
        ['Register Number:', session_data.get('register_number', 'N/A')],
        ['Year:', session_data.get('year', 'N/A')],
        ['Quiz:', session_data.get('quiz_name', 'N/A')],
        ['Date & Time:', session_data.get('timestamp', 'N/A')],
        ['Score:', f"<b>{session_data.get('score', '0')} / {session_data.get('total_questions', 20)}</b>"],
        ['Percentage:', f"<b>{(session_data.get('score', 0) / session_data.get('total_questions', 20) * 100):.2f}%</b>"]
    ]
    
    info_table = Table(student_info, colWidths=[1.5 * inch, 4.5 * inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4 * inch))
    
    story.append(Paragraph("Detailed Answer Sheet", styles['h3']))
    story.append(Spacer(1, 0.2 * inch))
    
    results_data = [['Q#', 'Your Answer', 'Correct Answer', 'Result']]
    questions = session_data.get('questions', [])
    answers = session_data.get('answers', [])
    
    for i, q in enumerate(questions):
        user_answer_idx = answers[i]
        user_answer_text = q['options'][user_answer_idx] if user_answer_idx is not None else "Not Answered"
        correct_answer_text = q['options'][q['correct']]
        result = "✓ Correct" if user_answer_idx == q['correct'] else "✗ Wrong"
        
        results_data.append([
            str(i + 1),
            Paragraph(user_answer_text, styles['Normal']),
            Paragraph(correct_answer_text, styles['Normal']),
            result
        ])
    
    results_table = Table(results_data, colWidths=[0.4*inch, 2.4*inch, 2.4*inch, 0.8*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (2, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    for i, row in enumerate(results_data[1:], start=1):
        if row[-1] == "✓ Correct":
            results_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.lightgreen)]))
        else:
            results_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.lightpink)]))
    
    story.append(results_table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def create_question_bank_pdf(quiz_name, question_bank):
    """Generates a PDF of the question bank for a specific quiz."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['h1'], alignment=TA_CENTER, fontSize=18)
    story.append(Paragraph(f"{quiz_name} - Question Bank", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    for idx, q in enumerate(question_bank, 1):
        q_text = f"<b>Q{idx}. {q['question']}</b>"
        story.append(Paragraph(q_text, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        
        for opt_idx, option in enumerate(q['options']):
            opt_letter = chr(97 + opt_idx)
            opt_text = f"{opt_letter}) {option}"
            if opt_idx == q['correct']:
                opt_text = f"<b><font color='green'>{opt_text} ✓</font></b>"
            story.append(Paragraph(opt_text, styles['Normal']))
        
        story.append(Spacer(1, 0.2 * inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# =====================================================================================
# --- 🖥️ UI RENDERING FUNCTIONS ---
# =====================================================================================

def render_year_selection_page():
    """Displays year selection interface."""
    st.set_page_config(page_title=APP_TITLE, layout="centered", page_icon="📚")
    
    with st.spinner("🔄 Connecting to database..."):
        connection_status = initialize_spreadsheet()
    
    if connection_status:
        st.success("✅ Connected to database successfully!", icon="✅")
    else:
        st.error("❌ Failed to connect to database. Please check your configuration.", icon="🚨")
        st.stop()
    
    st.title(f"📚 {APP_TITLE}")
    st.markdown(f"**Course:** {COURSE_NAME}")
    st.markdown("---")
    
    st.subheader("👨‍🎓 Select Your Year")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎓 Third Year", use_container_width=True, type="primary"):
            st.session_state.selected_year = "Third Year"
            st.session_state.page = "quiz_selection"
            st.rerun()
    
    with col2:
        if st.button("🎓 Final Year", use_container_width=True, type="primary"):
            st.session_state.selected_year = "Final Year"
            st.session_state.page = "quiz_selection"
            st.rerun()

def render_quiz_selection_page():
    """Displays quiz selection interface based on selected year."""
    st.set_page_config(page_title=f"{st.session_state.selected_year} Quizzes", layout="centered", page_icon="📝")
    
    st.title(f"📝 {st.session_state.selected_year} Quizzes")
    st.markdown(f"**Course:** {COURSE_NAME}")
    
    if st.button("← Back to Year Selection", key="back_year"):
        st.session_state.page = "year_selection"
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("🎯 Select Your Quiz")
    
    quiz_options = list(QUIZ_BANKS[st.session_state.selected_year].keys())
    selected_quiz = st.selectbox("Choose a quiz to attempt:", [""] + quiz_options)
    
    if selected_quiz:
        st.info(f"**Duration:** {QUIZ_DURATION_MINUTES} minutes | **Questions:** {QUESTIONS_PER_QUIZ}")
        st.warning("⚠️ **Important:** Do not switch tabs or minimize the browser during the quiz. This will automatically terminate your session.", icon="🚨")
        
        if st.button("Proceed to Quiz", type="primary", use_container_width=True):
            st.session_state.selected_quiz = selected_quiz
            st.session_state.page = "student_info"
            st.rerun()

def render_student_info_page():
    """Displays student information form."""
    st.set_page_config(page_title="Student Information", layout="centered", page_icon="📝")
    
    st.title("📝 Student Information")
    st.markdown(f"**Year:** {st.session_state.selected_year}")
    st.markdown(f"**Quiz:** {st.session_state.selected_quiz}")
    st.markdown("---")
    
    with st.form("student_info_form"):
        st.subheader("Enter Your Details")
        student_name = st.text_input("Full Name *", placeholder="Enter your full name")
        register_number = st.text_input("Register Number *", placeholder="Enter your register number")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Start Quiz", type="primary", use_container_width=True)
        with col2:
            back = st.form_submit_button("← Back", use_container_width=True)
        
        if back:
            st.session_state.page = "quiz_selection"
            st.rerun()
        
        if submitted:
            if not all([student_name.strip(), register_number.strip()]):
                st.error("❌ Please fill in all required fields marked with *")
            else:
                st.session_state.student_name = student_name.strip()
                st.session_state.register_number = register_number.strip()
                st.session_state.quiz_started = True
                st.session_state.start_time = time.time()
                
                quiz_bank = QUIZ_BANKS[st.session_state.selected_year][st.session_state.selected_quiz]
                st.session_state.questions = random.sample(quiz_bank, min(QUESTIONS_PER_QUIZ, len(quiz_bank)))
                st.session_state.answers = [None] * len(st.session_state.questions)
                st.session_state.current_question_index = 0
                st.session_state.page = "quiz"
                st.rerun()

def render_quiz_page():
    """Displays the main quiz interface with timer and questions."""
    st.set_page_config(page_title="Quiz in Progress", layout="centered", page_icon="✍️")
    
    malpractice_js = """
    <script>
    const handleVisibilityChange = () => {
        if (document.hidden) {
            window.sessionStorage.setItem('malpractice', 'true');
            document.body.innerHTML = `<div style='text-align: center; padding: 40px; color: red;'><h1>🚨 Quiz Terminated</h1><p>Malpractice detected. Your session has been terminated.</p></div>`;
        }
    };
    window.addEventListener('visibilitychange', handleVisibilityChange, { once: true });
    </script>
    """
    st.components.v1.html(malpractice_js, height=0)

    if streamlit_js_eval(js_expressions="window.sessionStorage.getItem('malpractice')", key='malpractice_check') == 'true':
        if not st.session_state.get('malpractice_detected', False):
            st.session_state.malpractice_detected = True
            
            log_data = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "student_name": st.session_state.student_name,
                "register_number": st.session_state.register_number,
                "year": st.session_state.selected_year,
                "quiz_name": st.session_state.selected_quiz,
                "event": "Tab switch/Browser minimized"
            }
            save_to_gsheet("MalpracticeLogs", log_data)
            st.session_state.page = "malpractice"
        st.rerun()
        return

    st_autorefresh(interval=1000, limit=None, key="quiz_timer")
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = QUIZ_DURATION_SECONDS - elapsed_time
    
    if remaining_time <= 0:
        st.toast("⏳ Time's up! Auto-submitting your quiz...", icon="⏰")
        time.sleep(2)
        st.session_state.quiz_submitted = True
        st.session_state.page = "results"
        st.rerun()
        return

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(st.session_state.selected_quiz)
    with col2:
        mins, secs = divmod(int(remaining_time), 60)
        timer_color = "🟢" if remaining_time > 120 else "🟡" if remaining_time > 60 else "🔴"
        st.metric(f"{timer_color} Time Left", f"{mins:02d}:{secs:02d}")

    progress = (st.session_state.current_question_index + 1) / len(st.session_state.questions)
    st.progress(progress)
    
    q_index = st.session_state.current_question_index
    question_data = st.session_state.questions[q_index]
    
    st.markdown(f"### Question {q_index + 1} of {len(st.session_state.questions)}")
    st.markdown(f"**{question_data['question']}**")
    st.markdown("")
    
    saved_answer_index = st.session_state.answers[q_index]
    
    if saved_answer_index is not None:
        default_index = saved_answer_index
    else:
        default_index = 0
    
    user_choice_label = st.radio(
        "Select your answer:",
        options=question_data['options'],
        index=default_index,
        key=f"q_{q_index}_{st.session_state.start_time}"
    )
    
    st.session_state.answers[q_index] = question_data['options'].index(user_choice_label)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(q_index == 0)):
            st.session_state.current_question_index -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"<center>Question {q_index + 1}/{len(st.session_state.questions)}</center>", unsafe_allow_html=True)
    
    with col3:
        if q_index < len(st.session_state.questions) - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                st.session_state.quiz_submitted = True
                st.session_state.page = "results"
                st.rerun()
    
    st.markdown("---")
    st.markdown("**Question Overview:**")
    answered = sum(1 for ans in st.session_state.answers if ans is not None)
    st.info(f"Answered: {answered} / {len(st.session_state.questions)}")

def render_results_page():
    """Displays final results and allows PDF download."""
    st.set_page_config(page_title="Quiz Results", layout="centered", page_icon="🎉")
    
    score = sum(1 for i, q in enumerate(st.session_state.questions) 
                if st.session_state.answers[i] is not None and st.session_state.answers[i] == q['correct'])
    
    total_questions = len(st.session_state.questions)
    percentage = (score / total_questions) * 100
    
    st.balloons()
    st.title("🎉 Quiz Submitted Successfully!")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score}/{total_questions}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        grade = "Excellent" if percentage >= 80 else "Good" if percentage >= 60 else "Pass" if percentage >= 40 else "Needs Improvement"
        st.metric("Grade", grade)
    
    if not st.session_state.get('submission_saved', False):
        year_prefix = st.session_state.selected_year.replace(" ", "")
        quiz_number = st.session_state.selected_quiz.split(":")[0].replace("Quiz ", "").strip()
        sheet_name = f"{year_prefix}_Quiz{quiz_number}"
        
        submission_data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "student_name": st.session_state.student_name,
            "register_number": st.session_state.register_number,
            "score": score,
            "total_questions": total_questions,
            "answers_json": json.dumps(st.session_state.answers),
            "questions_json": json.dumps([{"question": q["question"], "options": q["options"], "correct": q["correct"]} for q in st.session_state.questions])
        }
        
        if save_to_gsheet(sheet_name, submission_data):
            st.success("✅ Your results have been saved successfully!", icon="💾")
            st.session_state.submission_saved = True
        else:
            st.warning("⚠️ Could not save results to database. Please contact administrator.")
    
    st.markdown("---")
    st.subheader("📄 Download Your Report")
    
    pdf_data = {
        'year': st.session_state.selected_year,
        'quiz_name': st.session_state.selected_quiz,
        'student_name': st.session_state.student_name,
        'register_number': st.session_state.register_number,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'score': score,
        'total_questions': total_questions,
        'questions': st.session_state.questions,
        'answers': st.session_state.answers
    }
    
    pdf_bytes = create_results_pdf(pdf_data)
    st.download_button(
        label="📥 Download Performance Report (PDF)",
        data=pdf_bytes,
        file_name=f"{st.session_state.register_number}_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    st.markdown("---")
    if st.button("🔄 Take Another Quiz", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def render_malpractice_page():
    """Displays malpractice termination screen."""
    st.set_page_config(page_title="Quiz Terminated", layout="centered", page_icon="🚫")
    
    st.title("🚨 Quiz Terminated")
    st.error("Your quiz session has been terminated due to malpractice detection (tab switching or browser minimization).", icon="🚫")
    
    st.markdown("---")
    st.markdown("### Incident Details")
    st.info(f"""
    **Student Name:** {st.session_state.get('student_name', 'N/A')}  
    **Register Number:** {st.session_state.get('register_number', 'N/A')}  
    **Year:** {st.session_state.get('selected_year', 'N/A')}  
    **Quiz:** {st.session_state.get('selected_quiz', 'N/A')}  
    **Time:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """)
    
    st.warning("This incident has been logged and reported to the administrator.")
    
    if st.button("Return to Home", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def render_admin_panel():
    """Displays admin panel in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.title("🔐 Admin Access")
    
    with st.sidebar.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")
    
    if login:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.session_state.page = "admin_dashboard"
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid credentials")

def render_admin_dashboard():
    """Displays the full admin dashboard."""
    st.set_page_config(page_title="Admin Dashboard", layout="wide", page_icon="👨‍💼")
    
    st.title("👨‍💼 Admin Dashboard")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.session_state.page = "year_selection"
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["📊 Quiz Results", "🚨 Malpractice Logs", "📚 Question Banks"])
    
    with tab1:
        st.subheader("Quiz Results")
        
        col1, col2 = st.columns(2)
        with col1:
            year_selector = st.selectbox("Select Year:", ["Third Year", "Final Year"])
        with col2:
            if year_selector == "Third Year":
                quiz_options = ["ThirdYear_Quiz2", "ThirdYear_Quiz3", "ThirdYear_Quiz4"]
            else:
                quiz_options = ["FinalYear_Quiz1", "FinalYear_Quiz2", "FinalYear_Quiz3", "FinalYear_Quiz4"]
            quiz_selector = st.selectbox("Select Quiz:", quiz_options)
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
        
        with st.spinner("Loading data..."):
            df = get_sheet_data(quiz_selector)
        
        if df is not None and not df.empty:
            st.metric("Total Submissions", len(df))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_score = df['score'].mean()
                st.metric("Average Score", f"{avg_score:.2f}")
            with col2:
                max_score = df['score'].max()
                st.metric("Highest Score", f"{max_score}")
            with col3:
                min_score = df['score'].min()
                st.metric("Lowest Score", f"{min_score}")
            
            st.markdown("### Recent Submissions")
            display_df = df[['timestamp', 'student_name', 'register_number', 'score', 'total_questions']].copy()
            display_df['percentage'] = (display_df['score'] / display_df['total_questions'] * 100).round(2)
            st.dataframe(display_df, use_container_width=True)
            
            csv_bytes = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download All Results (CSV)",
                data=csv_bytes,
                file_name=f"{quiz_selector}_results.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown("### Individual Student Reports")
            student_names = df['student_name'].tolist()
            selected_student = st.selectbox("Select Student:", student_names)
            
            if st.button("📄 Download Student Report (PDF)"):
                student_record = df[df['student_name'] == selected_student].iloc[0]
                
                pdf_data = {
                    'year': year_selector,
                    'quiz_name': quiz_selector,
                    'student_name': student_record['student_name'],
                    'register_number': student_record['register_number'],
                    'timestamp': student_record['timestamp'],
                    'score': student_record['score'],
                    'total_questions': student_record['total_questions'],
                    'questions': json.loads(student_record['questions_json']),
                    'answers': json.loads(student_record['answers_json'])
                }
                
                pdf_bytes = create_results_pdf(pdf_data)
                st.download_button(
                    label=f"📥 Download {selected_student}'s Report",
                    data=pdf_bytes,
                    file_name=f"{student_record['register_number']}_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("No submissions found for this quiz.")
    
    with tab2:
        st.subheader("Malpractice Incidents")
        
        with st.spinner("Loading malpractice logs..."):
            log_df = get_sheet_data("MalpracticeLogs")
        
        if log_df is not None and not log_df.empty:
            st.error(f"⚠️ {len(log_df)} malpractice incidents detected", icon="🚨")
            st.dataframe(log_df, use_container_width=True)
            
            csv_bytes = log_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Malpractice Logs (CSV)",
                data=csv_bytes,
                file_name="malpractice_logs.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ No malpractice incidents recorded", icon="✅")
    
    with tab3:
        st.subheader("Question Banks")
        
        col1, col2 = st.columns(2)
        with col1:
            year_qb_selector = st.selectbox("Select Year:", ["Third Year", "Final Year"], key="qb_year")
        with col2:
            quiz_qb_selector = st.selectbox("Select Quiz:", list(QUIZ_BANKS[year_qb_selector].keys()), key="qb_quiz")
        
        if quiz_qb_selector:
            selected_bank = QUIZ_BANKS[year_qb_selector][quiz_qb_selector]
            st.info(f"Total Questions: {len(selected_bank)}")
            
            with st.expander("View Questions"):
                for idx, q in enumerate(selected_bank, 1):
                    st.markdown(f"**Q{idx}. {q['question']}**")
                    for opt_idx, option in enumerate(q['options']):
                        marker = "✅" if opt_idx == q['correct'] else ""
                        st.markdown(f"   {chr(97 + opt_idx)}) {option} {marker}")
                    st.markdown("---")
            
            if st.button("📥 Download Question Bank (PDF)"):
                pdf_bytes = create_question_bank_pdf(quiz_qb_selector, selected_bank)
                st.download_button(
                    label=f"Download {quiz_qb_selector} Questions",
                    data=pdf_bytes,
                    file_name=f"{quiz_qb_selector.replace(':', '').replace(' ', '_')}_QuestionBank.pdf",
                    mime="application/pdf"
                )

# =====================================================================================
# --- 🚀 MAIN APPLICATION ROUTER ---
# =====================================================================================

def main():
    """Main function to control the app's page flow."""
    
    if 'page' not in st.session_state:
        st.session_state.page = "year_selection"
    
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if st.session_state.admin_authenticated and st.session_state.page == "admin_dashboard":
        render_admin_dashboard()
    elif st.session_state.get('malpractice_detected', False):
        render_malpractice_page()
    elif st.session_state.page == "year_selection":
        render_year_selection_page()
        if not st.session_state.admin_authenticated:
            render_admin_panel()
    elif st.session_state.page == "quiz_selection":
        render_quiz_selection_page()
        if not st.session_state.admin_authenticated:
            render_admin_panel()
    elif st.session_state.page == "student_info":
        render_student_info_page()
    elif st.session_state.page == "quiz":
        render_quiz_page()
    elif st.session_state.page == "results":
        render_results_page()
    else:
        st.session_state.page = "year_selection"
        st.rerun()

if __name__ == "__main__":
    main()
