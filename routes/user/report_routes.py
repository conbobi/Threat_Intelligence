from venv import logger

from flask import Blueprint, render_template, request, jsonify, session
from services.report_service import create_report
import logging
report_bp = Blueprint('user_report', __name__, url_prefix='/report')

@report_bp.route('/')
def report_page():
    """Trang báo cáo của người dùng."""
    return render_template('user/report/report.html', active_page='report')
@report_bp.route('/api/scam', methods=['POST'])
def submit_report():
    """API nhận báo cáo."""
    data = request.json
    user_id = session.get('user_id')
    try:
        # Gọi service tạo báo cáo
        report = create_report(
            user_id=user_id,
            report_type=data.get('report_type'),
            target=data.get('target'),
            reason=data.get('reason'),
            note=data.get('note')
        )
        return jsonify({"success": True, "report_id": report['id']})
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        return jsonify({"success": False, "error": str(e)}), 500