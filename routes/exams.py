"""检验检查结果路由"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, ExamResult

exams_bp = Blueprint("exams", __name__, template_folder="../templates/exams")


@exams_bp.route("/")
def list_exams():
    """检验检查列表"""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    query = ExamResult.query.order_by(ExamResult.exam_date.desc())

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                ExamResult.exam_name.like(like),
                ExamResult.hospital.like(like),
                ExamResult.conclusion.like(like),
            )
        )

    if category:
        query = query.filter(ExamResult.category == category)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    exams = pagination.items

    return render_template(
        "exams/list.html",
        exams=exams,
        pagination=pagination,
        search=search,
        current_category=category,
    )


@exams_bp.route("/create", methods=["GET", "POST"])
def create_exam():
    """新建检验检查结果"""
    medical_record_id = request.args.get("record_id", type=int)

    if request.method == "POST":
        try:
            exam = ExamResult(
                exam_date=datetime.strptime(request.form["exam_date"], "%Y-%m-%d").date(),
                hospital=request.form.get("hospital", ""),
                category=request.form["category"],
                exam_name=request.form["exam_name"],
                result=request.form.get("result", ""),
                reference_range=request.form.get("reference_range", ""),
                unit=request.form.get("unit", ""),
                conclusion=request.form.get("conclusion", ""),
                notes=request.form.get("notes", ""),
                medical_record_id=request.form.get("medical_record_id", type=int) or None,
            )
            db.session.add(exam)
            db.session.commit()
            flash("检验检查结果已添加", "success")
            return redirect(url_for("exams.view_exam", exam_id=exam.id))
        except Exception as e:
            db.session.rollback()
            flash(f"添加失败: {str(e)}", "danger")

    return render_template("exams/create.html", medical_record_id=medical_record_id)


@exams_bp.route("/<int:exam_id>")
def view_exam(exam_id):
    """查看检验检查详情"""
    exam = ExamResult.query.get_or_404(exam_id)
    return render_template("exams/detail.html", exam=exam)


@exams_bp.route("/<int:exam_id>/edit", methods=["GET", "POST"])
def edit_exam(exam_id):
    """编辑检验检查结果"""
    exam = ExamResult.query.get_or_404(exam_id)

    if request.method == "POST":
        try:
            exam.exam_date = datetime.strptime(request.form["exam_date"], "%Y-%m-%d").date()
            exam.hospital = request.form.get("hospital", "")
            exam.category = request.form["category"]
            exam.exam_name = request.form["exam_name"]
            exam.result = request.form.get("result", "")
            exam.reference_range = request.form.get("reference_range", "")
            exam.unit = request.form.get("unit", "")
            exam.conclusion = request.form.get("conclusion", "")
            exam.notes = request.form.get("notes", "")
            exam.medical_record_id = request.form.get("medical_record_id", type=int) or None
            db.session.commit()
            flash("检验检查结果已更新", "success")
            return redirect(url_for("exams.view_exam", exam_id=exam.id))
        except Exception as e:
            db.session.rollback()
            flash(f"更新失败: {str(e)}", "danger")

    return render_template("exams/edit.html", exam=exam)


@exams_bp.route("/<int:exam_id>/delete", methods=["POST"])
def delete_exam(exam_id):
    """删除检验检查结果"""
    exam = ExamResult.query.get_or_404(exam_id)
    try:
        db.session.delete(exam)
        db.session.commit()
        flash("检验检查结果已删除", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"删除失败: {str(e)}", "danger")
    return redirect(url_for("exams.list_exams"))
