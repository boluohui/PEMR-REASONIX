"""数据模型 — 个人电子病历档案系统"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class MedicalRecord(db.Model):
    """就医记录"""
    __tablename__ = "medical_records"

    id = db.Column(db.Integer, primary_key=True)
    visit_date = db.Column(db.Date, nullable=False, index=True, comment="就诊日期")
    hospital = db.Column(db.String(200), nullable=False, comment="医院名称")
    department = db.Column(db.String(100), comment="科室")
    doctor = db.Column(db.String(50), comment="医生")
    chief_complaint = db.Column(db.Text, comment="主诉")
    present_illness = db.Column(db.Text, comment="现病史")
    diagnosis = db.Column(db.Text, comment="诊断")
    notes = db.Column(db.Text, comment="备注")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联
    exam_results = db.relationship("ExamResult", backref="medical_record", lazy="dynamic",
                                   cascade="all, delete-orphan")
    prescriptions = db.relationship("Prescription", backref="medical_record", lazy="dynamic",
                                    cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MedicalRecord {self.id}: {self.visit_date} @ {self.hospital}>"

    def to_dict(self):
        return {
            "id": self.id,
            "visit_date": self.visit_date.strftime("%Y-%m-%d") if self.visit_date else "",
            "hospital": self.hospital,
            "department": self.department,
            "doctor": self.doctor,
            "diagnosis": self.diagnosis,
        }


class ExamResult(db.Model):
    """检验检查结果"""
    __tablename__ = "exam_results"

    id = db.Column(db.Integer, primary_key=True)
    exam_date = db.Column(db.Date, nullable=False, index=True, comment="检查日期")
    hospital = db.Column(db.String(200), comment="医院名称")
    category = db.Column(db.String(50), nullable=False, comment="分类: 检验/检查")
    exam_name = db.Column(db.String(200), nullable=False, comment="项目名称")
    result = db.Column(db.Text, comment="结果")
    reference_range = db.Column(db.String(200), comment="参考范围")
    unit = db.Column(db.String(50), comment="单位")
    conclusion = db.Column(db.Text, comment="结论/描述")
    notes = db.Column(db.Text, comment="备注")
    image_path = db.Column(db.String(500), comment="报告图片路径(可选)")
    medical_record_id = db.Column(db.Integer, db.ForeignKey("medical_records.id"), comment="关联就医记录")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<ExamResult {self.id}: {self.exam_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "exam_date": self.exam_date.strftime("%Y-%m-%d") if self.exam_date else "",
            "hospital": self.hospital,
            "category": self.category,
            "exam_name": self.exam_name,
            "result": self.result,
        }


class Prescription(db.Model):
    """处方"""
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    prescription_date = db.Column(db.Date, nullable=False, index=True, comment="开药日期")
    hospital = db.Column(db.String(200), comment="医院名称")
    doctor = db.Column(db.String(50), comment="医生")
    diagnosis = db.Column(db.Text, comment="诊断")
    notes = db.Column(db.Text, comment="备注")
    medical_record_id = db.Column(db.Integer, db.ForeignKey("medical_records.id"), comment="关联就医记录")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    # 处方明细
    items = db.relationship("PrescriptionItem", backref="prescription", lazy="dynamic",
                            cascade="all, delete-orphan", order_by="PrescriptionItem.id")

    def __repr__(self):
        return f"<Prescription {self.id}: {self.prescription_date}>"

    def to_dict(self):
        return {
            "id": self.id,
            "prescription_date": self.prescription_date.strftime("%Y-%m-%d") if self.prescription_date else "",
            "hospital": self.hospital,
            "doctor": self.doctor,
            "diagnosis": self.diagnosis,
        }


class PrescriptionItem(db.Model):
    """处方明细 — 具体药品"""
    __tablename__ = "prescription_items"

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey("prescriptions.id"), nullable=False, comment="所属处方")
    drug_name = db.Column(db.String(200), nullable=False, comment="药品名称")
    dosage = db.Column(db.String(100), comment="单次剂量")
    frequency = db.Column(db.String(100), comment="用药频次")
    route = db.Column(db.String(50), comment="给药途径")
    duration = db.Column(db.String(100), comment="疗程")
    quantity = db.Column(db.String(100), comment="数量")
    notes = db.Column(db.Text, comment="备注")

    def __repr__(self):
        return f"<PrescriptionItem {self.id}: {self.drug_name}>"
