import os
import json
from fpdf import FPDF
import database as db

class InterviewReportPDF(FPDF):
    def header(self):
        # Draw decorative top background accent
        self.set_fill_color(99, 102, 241) # Brand Indigo
        self.rect(0, 0, 210, 12, "F")
        
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(148, 163, 184)
        self.set_y(20)
        self.cell(0, 5, "AI INTERVIEW COACH PRO - ENTERPRISE DIAGNOSTIC EVALUATION REPORT", 0, 1, "R")
        self.set_draw_color(226, 232, 240)
        self.line(10, 27, 200, 27)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(100, 10, "CONFIDENTIAL - AUTOMATED SYSTEM EVALUATION ENGINE", 0, 0, "L")
        self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", 0, 0, "R")

def generate_pdf_report(interview_id, output_directory=None):
    """
    Reads interview telemetry from SQLite storage, processes historical evaluation logs, 
    and outputs a formal evaluation document using fpdf2.
    """
    record = db.get_interview(interview_id)
    if not record:
        return None

    try:
        history = json.loads(record["history_json"])
    except Exception:
        history = []

    pdf = InterviewReportPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- REPORT HEADER METADATA BLOCK ---
    pdf.set_y(35)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(15, 23, 42) # Dark Slate
    pdf.cell(0, 10, "Interview Performance Audit", 0, 1, "L")
    
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 8, f"Target Track: {record['role']}", 0, 1, "L")
    pdf.ln(4)

    # --- METADATA TWO-COLUMN SUMMARY BOX ---
    pdf.set_fill_color(248, 250, 252) # Light Grey Surface
    pdf.rect(10, pdf.get_y(), 190, 32, "F")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 116, 139)
    
    current_y = pdf.get_y() + 4
    pdf.set_xy(14, current_y)
    pdf.cell(40, 6, "CANDIDATE NAME:", 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(60, 6, str(record["candidate_name"]), 0, 0)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(35, 6, "SESSION TIMESTAMP:", 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, str(record["date"]), 0, 1)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.set_x(14)
    pdf.cell(40, 6, "EVALUATION ID:", 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(60, 6, f"ACC-EVAL-{record['id']:06d}", 0, 0)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(35, 6, "TOTAL DURATION:", 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(15, 23, 42)
    
    minutes = record["duration"] // 60
    seconds = record["duration"] % 60
    pdf.cell(0, 6, f"{minutes:02d}m {seconds:02d}s", 0, 1)
    
    pdf.ln(16)

    # --- CORE KPI SCOREBOARD MATRIX ---
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "Global Index Score Summary", 0, 1, "L")
    pdf.ln(2)
    
    # Multi-pills score block layout simulation
    scores = [
        ("OVERALL SCORE", record["overall_score"], 99, 102, 241),
        ("TECHNICAL KNOWLEDGE", record["technical_score"], 16, 185, 129),
        ("COMMUNICATION CAPACITY", record["communication_score"], 245, 158, 11)
    ]
    
    for title, val, r, g, b in scores:
        start_x = pdf.get_x()
        start_y = pdf.get_y()
        
        pdf.set_fill_color(241, 245, 249)
        pdf.rect(start_x, start_y, 190, 12, "F")
        pdf.set_fill_color(r, g, b)
        pdf.rect(start_x, start_y, 6, 12, "F")
        
        pdf.set_xy(start_x + 10, start_y + 3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(80, 6, title, 0, 0)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 6, f"{val}%", 0, 1, "R")
        pdf.set_xy(10, start_y + 14)
        
    pdf.ln(6)

    # --- CONSOLIDATED PERFORMANCE SYNTHESIS ---
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "Comprehensive Performance Diagnosis", 0, 1, "L")
    pdf.ln(2)

    # Accumulate and organize structural evaluation data from all segments
    all_strengths = []
    all_weaknesses = []
    all_missing_keywords = []
    all_suggestions = []

    for item in history:
        eval_obj = item.get("evaluation", {})
        if eval_obj.get("strengths"): all_strengths.append(eval_obj["strengths"])
        if eval_obj.get("weaknesses"): all_weaknesses.append(eval_obj["weaknesses"])
        if eval_obj.get("suggestions"): all_suggestions.append(eval_obj["suggestions"])
        for kw in eval_obj.get("missing_keywords", []):
            if kw not in all_missing_keywords:
                all_missing_keywords.append(kw)

    sections = [
        ("Identified Core Strengths", ". ".join(all_strengths[:3]) if all_strengths else "Demonstrated standard functional baseline answers.", 16, 185, 129),
        ("Observed Skill Gaps & Weaknesses", ". ".join(all_weaknesses[:3]) if all_weaknesses else "No critical conceptual gaps flagged.", 239, 68, 68),
        ("Strategic Upgrade Action Plans", ". ".join(all_suggestions[:3]) if all_suggestions else "Continue refining technical vocabulary alignment.", 99, 102, 241)
    ]

    for sec_title, sec_text, r, g, b in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 6, sec_title, 0, 1)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 5, sec_text, 0, "L")
        pdf.ln(4)

    if all_missing_keywords:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 6, "Key Vocabulary Gaps Identified:", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(220, 38, 38)
        pdf.multi_cell(0, 5, ", ".join(all_missing_keywords), 0, "L")
        pdf.ln(4)

    # --- ITEMISED RECORD QUESTION-BY-QUESTION CHRONOLOGY ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "Granular Itemized Evaluation Log", 0, 1, "L")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    for idx, item in enumerate(history):
        # Prevent row breaks at page margins by calculating available height
        if pdf.get_y() > 240:
            pdf.add_page()
            
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(99, 102, 241)
        pdf.cell(0, 6, f"Question {idx + 1}: {item.get('category', 'Technical Validation')}", 0, 1)
        
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(0, 5, f"\"{item.get('question_text', '')}\"", 0, "L")
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(40, 5, "Candidate Response:", 0, 1)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(51, 65, 85)
        
        user_ans = item.get('user_answer', '').strip()
        pdf.multi_cell(0, 5, f" {user_ans}" if user_ans else " [No response logged or timeout registered]", 0, "L")
        pdf.ln(2)

        eval_data = item.get("evaluation", {})
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(50, 5, f"Confidence Index: {eval_data.get('confidence_score', 0)}%  |  Tech: {eval_data.get('technical_score', 0)}%  |  Comm: {eval_data.get('communication_score', 0)}%", 0, 1)
        
        pdf.set_draw_color(241, 245, 249)
        pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
        pdf.ln(4)

    # Determine structural write path locations safely
    filename = f"Interview_Report_{interview_id}.pdf"
    if output_directory:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        filepath = os.path.join(output_directory, filename)
    else:
        filepath = os.path.join(os.path.dirname(__file__), filename)

    pdf.output(filepath)
    return filepath

# Inject explicit download route wrapper directly into app infrastructure to resolve missing links
import app
from flask import send_file, abort

@app.app.route("/download_pdf/<int:interview_id>")
def download_pdf_endpoint(interview_id):
    """
    Constructs the requested PDF report and serves the generated document 
    binary directly to the client browser.
    """
    try:
        report_directory = os.path.join(os.path.dirname(__file__), "database")
        file_path = generate_pdf_report(interview_id, output_directory=report_directory)
        if file_path and os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=f"Interview_Report_{interview_id}.pdf")
        else:
            return abort(404, "Target PDF build criteria missing row associations.")
    except Exception as ex:
        return abort(500, f"Internal report execution pipeline fault: {str(ex)}")