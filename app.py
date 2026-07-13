from flask import Flask, Blueprint, request, jsonify, render_template, make_response
from database import init_db, save_interview, get_interview, get_all_interviews
from evaluation import evaluate_step
from question_engine import get_role_questions
from fpdf import FPDF
import json

app = Flask(__name__)

# Blueprints
main_bp = Blueprint('main', __name__)
interview_bp = Blueprint('interview', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
report_bp = Blueprint('report', __name__)
history_bp = Blueprint('history', __name__)

# Main Routes
@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

# API Routes
@interview_bp.route('/interview')
def interview_page():
    return render_template('interview.html')

@interview_bp.route('/api/get_questions', methods=['GET'])
def get_questions():
    role = request.args.get('role')
    questions = get_role_questions(role)
    return jsonify({"questions": questions})

@interview_bp.route('/api/evaluate_step', methods=['POST'])
def evaluate_step_api():
    data = request.json
    answer = data.get('answer', '')
    q_id = data.get('question_id')
    role = data.get('role')
    
    questions = get_role_questions(role)
    q_data = next((q for q in questions if q['id'] == q_id), None)
    
    if not q_data:
        return jsonify({"error": "Question not found"}), 404
        
    result = evaluate_step(answer, q_data)
    return jsonify(result)

@interview_bp.route('/api/submit_interview', methods=['POST'])
def submit_interview():
    data = request.json
    interview_id = save_interview(data)
    return jsonify({"success": True, "id": interview_id})

# Dashboard Route
@dashboard_bp.route('/dashboard/<int:id>', methods=['GET'])
def dashboard(id):
    row = get_interview(id)
    if not row:
        return "Interview not found", 404
    return render_template('dashboard.html', interview=row)

# Report Route
@report_bp.route('/report/<int:id>', methods=['GET'])
def generate_report(id):
    row = get_interview(id)
    if not row:
        return "Interview not found", 404
        
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="AI Interview Coach Pro - Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Candidate: {row['name']}", ln=True)
    pdf.cell(200, 10, txt=f"Role: {row['role']}", ln=True)
    pdf.cell(200, 10, txt=f"Overall Score: {row['overall_score']}%", ln=True)
    pdf.cell(200, 10, txt=f"Date: {row['timestamp']}", ln=True)
    
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', f'attachment; filename=report_{id}.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response

# History Route
@history_bp.route('/history', methods=['GET'])
def history():
    rows = get_all_interviews()
    return render_template('history.html', interviews=rows)

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(interview_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(report_bp)
app.register_blueprint(history_bp)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)