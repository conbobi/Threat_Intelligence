from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import admin_required
from services.report_service import (
    get_all_reports_for_admin,
    get_report_details,
    update_report
)
from services.admin_service import get_admin_id_by_user_id  # nếu cần lấy admin_id từ user_id

admin_report_bp = Blueprint('admin_report', __name__, url_prefix='/admin/reports')

@admin_report_bp.route('')
@admin_required
def list_reports():
    """Hiển thị danh sách báo cáo (admin)."""
    status_filter = request.args.get('status', None)
    reports = get_all_reports_for_admin(status=status_filter, limit=200)
    return render_template(
        'admin/report/reports_list.html',
        reports=reports,
        current_filter=status_filter
    )

@admin_report_bp.route('/<report_id>')
@admin_required
def detail_report(report_id):
    """Xem chi tiết một báo cáo."""
    report = get_report_details(report_id)
    if not report:
        flash('Không tìm thấy báo cáo.', 'danger')
        return redirect(url_for('admin_report.list_reports'))
    return render_template('admin/report/report_detail.html', report=report)

@admin_report_bp.route('/<report_id>/update', methods=['POST'])
@admin_required
def update_report_status(report_id):
    """Cập nhật trạng thái và ghi chú cho báo cáo."""
    status = request.form.get('status')
    admin_note = request.form.get('admin_note', '').strip()
    # Lấy user_id của admin đang đăng nhập
    reviewed_by = session.get('user_id')  # giả sử user_id của admin được lưu trong session

    if status not in ('PENDING', 'REVIEWING', 'RESOLVED', 'REJECTED'):
        flash('Trạng thái không hợp lệ.', 'danger')
        return redirect(url_for('admin_report.detail_report', report_id=report_id))

    try:
        update_report(report_id, status, admin_note, reviewed_by)
        flash('Cập nhật báo cáo thành công.', 'success')
    except Exception as e:
        flash(f'Lỗi khi cập nhật: {str(e)}', 'danger')

    return redirect(url_for('admin_report.detail_report', report_id=report_id))