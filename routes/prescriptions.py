"""处方路由"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Prescription, PrescriptionItem

prescriptions_bp = Blueprint("prescriptions", __name__, template_folder="../templates/prescriptions")


@prescriptions_bp.route("/")
def list_prescriptions():
    """处方列表"""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    search = request.args.get("search", "").strip()

    query = Prescription.query.order_by(Prescription.prescription_date.desc())

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Prescription.hospital.like(like),
                Prescription.doctor.like(like),
                Prescription.diagnosis.like(like),
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    prescriptions = pagination.items

    return render_template(
        "prescriptions/list.html",
        prescriptions=prescriptions,
        pagination=pagination,
        search=search,
    )


@prescriptions_bp.route("/create", methods=["GET", "POST"])
def create_prescription():
    """新建处方"""
    medical_record_id = request.args.get("record_id", type=int)

    if request.method == "POST":
        try:
            prescription = Prescription(
                prescription_date=datetime.strptime(request.form["prescription_date"], "%Y-%m-%d").date(),
                hospital=request.form.get("hospital", ""),
                doctor=request.form.get("doctor", ""),
                diagnosis=request.form.get("diagnosis", ""),
                notes=request.form.get("notes", ""),
                medical_record_id=request.form.get("medical_record_id", type=int) or None,
            )
            db.session.add(prescription)
            db.session.flush()  # 获取 prescription.id

            # 处理处方明细
            drug_names = request.form.getlist("drug_name[]")
            dosages = request.form.getlist("dosage[]")
            frequencies = request.form.getlist("frequency[]")
            routes = request.form.getlist("route[]")
            durations = request.form.getlist("duration[]")
            quantities = request.form.getlist("quantity[]")
            item_notes = request.form.getlist("item_notes[]")

            for i, drug_name in enumerate(drug_names):
                if drug_name.strip():
                    item = PrescriptionItem(
                        prescription_id=prescription.id,
                        drug_name=drug_name.strip(),
                        dosage=dosages[i].strip() if i < len(dosages) else "",
                        frequency=frequencies[i].strip() if i < len(frequencies) else "",
                        route=routes[i].strip() if i < len(routes) else "",
                        duration=durations[i].strip() if i < len(durations) else "",
                        quantity=quantities[i].strip() if i < len(quantities) else "",
                        notes=item_notes[i].strip() if i < len(item_notes) else "",
                    )
                    db.session.add(item)

            db.session.commit()
            flash("处方已创建", "success")
            return redirect(url_for("prescriptions.view_prescription", prescription_id=prescription.id))
        except Exception as e:
            db.session.rollback()
            flash(f"创建失败: {str(e)}", "danger")

    return render_template("prescriptions/create.html", medical_record_id=medical_record_id)


@prescriptions_bp.route("/<int:prescription_id>")
def view_prescription(prescription_id):
    """查看处方详情"""
    prescription = Prescription.query.get_or_404(prescription_id)
    return render_template("prescriptions/detail.html", prescription=prescription)


@prescriptions_bp.route("/<int:prescription_id>/edit", methods=["GET", "POST"])
def edit_prescription(prescription_id):
    """编辑处方"""
    prescription = Prescription.query.get_or_404(prescription_id)

    if request.method == "POST":
        try:
            prescription.prescription_date = datetime.strptime(request.form["prescription_date"], "%Y-%m-%d").date()
            prescription.hospital = request.form.get("hospital", "")
            prescription.doctor = request.form.get("doctor", "")
            prescription.diagnosis = request.form.get("diagnosis", "")
            prescription.notes = request.form.get("notes", "")
            prescription.medical_record_id = request.form.get("medical_record_id", type=int) or None

            # 删除旧明细，重新添加
            PrescriptionItem.query.filter_by(prescription_id=prescription.id).delete()

            drug_names = request.form.getlist("drug_name[]")
            dosages = request.form.getlist("dosage[]")
            frequencies = request.form.getlist("frequency[]")
            routes = request.form.getlist("route[]")
            durations = request.form.getlist("duration[]")
            quantities = request.form.getlist("quantity[]")
            item_notes = request.form.getlist("item_notes[]")

            for i, drug_name in enumerate(drug_names):
                if drug_name.strip():
                    item = PrescriptionItem(
                        prescription_id=prescription.id,
                        drug_name=drug_name.strip(),
                        dosage=dosages[i].strip() if i < len(dosages) else "",
                        frequency=frequencies[i].strip() if i < len(frequencies) else "",
                        route=routes[i].strip() if i < len(routes) else "",
                        duration=durations[i].strip() if i < len(durations) else "",
                        quantity=quantities[i].strip() if i < len(quantities) else "",
                        notes=item_notes[i].strip() if i < len(item_notes) else "",
                    )
                    db.session.add(item)

            db.session.commit()
            flash("处方已更新", "success")
            return redirect(url_for("prescriptions.view_prescription", prescription_id=prescription.id))
        except Exception as e:
            db.session.rollback()
            flash(f"更新失败: {str(e)}", "danger")

    return render_template("prescriptions/edit.html", prescription=prescription)


@prescriptions_bp.route("/<int:prescription_id>/delete", methods=["POST"])
def delete_prescription(prescription_id):
    """删除处方"""
    prescription = Prescription.query.get_or_404(prescription_id)
    try:
        db.session.delete(prescription)
        db.session.commit()
        flash("处方已删除", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"删除失败: {str(e)}", "danger")
    return redirect(url_for("prescriptions.list_prescriptions"))
