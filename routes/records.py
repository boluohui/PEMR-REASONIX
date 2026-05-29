"""就医记录路由"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import db, MedicalRecord
import io
import re

records_bp = Blueprint("records", __name__, template_folder="../templates/records")


@records_bp.route("/")
def list_records():
    """就医记录列表"""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    # 搜索过滤
    search = request.args.get("search", "").strip()
    query = MedicalRecord.query.order_by(MedicalRecord.visit_date.desc())

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                MedicalRecord.hospital.like(like),
                MedicalRecord.department.like(like),
                MedicalRecord.doctor.like(like),
                MedicalRecord.diagnosis.like(like),
                MedicalRecord.chief_complaint.like(like),
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items

    return render_template(
        "records/list.html",
        records=records,
        pagination=pagination,
        search=search,
    )


@records_bp.route("/create", methods=["GET", "POST"])
def create_record():
    """新建就医记录"""
    if request.method == "POST":
        try:
            record = MedicalRecord(
                visit_date=datetime.strptime(request.form["visit_date"], "%Y-%m-%d").date(),
                hospital=request.form["hospital"],
                department=request.form.get("department", ""),
                doctor=request.form.get("doctor", ""),
                chief_complaint=request.form.get("chief_complaint", ""),
                present_illness=request.form.get("present_illness", ""),
                diagnosis=request.form.get("diagnosis", ""),
                notes=request.form.get("notes", ""),
            )
            db.session.add(record)
            db.session.commit()
            flash("就医记录已创建", "success")
            return redirect(url_for("records.view_record", record_id=record.id))
        except Exception as e:
            db.session.rollback()
            flash(f"创建失败: {str(e)}", "danger")

    return render_template("records/create.html")


@records_bp.route("/<int:record_id>")
def view_record(record_id):
    """查看就医记录详情"""
    record = MedicalRecord.query.get_or_404(record_id)
    return render_template("records/detail.html", record=record)


@records_bp.route("/<int:record_id>/edit", methods=["GET", "POST"])
def edit_record(record_id):
    """编辑就医记录"""
    record = MedicalRecord.query.get_or_404(record_id)

    if request.method == "POST":
        try:
            record.visit_date = datetime.strptime(request.form["visit_date"], "%Y-%m-%d").date()
            record.hospital = request.form["hospital"]
            record.department = request.form.get("department", "")
            record.doctor = request.form.get("doctor", "")
            record.chief_complaint = request.form.get("chief_complaint", "")
            record.present_illness = request.form.get("present_illness", "")
            record.diagnosis = request.form.get("diagnosis", "")
            record.notes = request.form.get("notes", "")
            db.session.commit()
            flash("就医记录已更新", "success")
            return redirect(url_for("records.view_record", record_id=record.id))
        except Exception as e:
            db.session.rollback()
            flash(f"更新失败: {str(e)}", "danger")

    return render_template("records/edit.html", record=record)


@records_bp.route("/<int:record_id>/export")
def export_record(record_id):
    """导出完整就医记录为 HTML 文件"""
    record = MedicalRecord.query.get_or_404(record_id)
    html = render_template("records/export.html", record=record, datetime=datetime)

    # 清理多余空白，压缩体积
    html = re.sub(r"\n\s*\n", "\n", html)

    # 生成文件名
    filename = f"就医记录_{record.visit_date}_{record.hospital}.html"
    filename = re.sub(r"[^\w\-_. ]", "_", filename)

    buf = io.BytesIO(html.encode("utf-8"))
    return send_file(
        buf,
        mimetype="text/html; charset=utf-8",
        as_attachment=True,
        download_name=filename,
    )


@records_bp.route("/<int:record_id>/delete", methods=["POST"])
def delete_record(record_id):
    """删除就医记录"""
    record = MedicalRecord.query.get_or_404(record_id)
    try:
        db.session.delete(record)
        db.session.commit()
        flash("就医记录已删除", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"删除失败: {str(e)}", "danger")
    return redirect(url_for("records.list_records"))
