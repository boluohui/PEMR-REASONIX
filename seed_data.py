"""生成测试数据"""

from datetime import date, timedelta
from app import create_app
from models import db, MedicalRecord, ExamResult, Prescription, PrescriptionItem

app = create_app()

with app.app_context():
    print("正在清空旧数据...")
    PrescriptionItem.query.delete()
    Prescription.query.delete()
    ExamResult.query.delete()
    MedicalRecord.query.delete()
    db.session.commit()

    print("正在生成测试数据...")

    # ========== 就医记录 ==========
    records = [
        MedicalRecord(
            visit_date=date(2025, 3, 15),
            hospital="北京协和医院",
            department="呼吸内科",
            doctor="李明",
            chief_complaint="咳嗽、发热3天，体温最高38.5℃",
            present_illness="患者3天前受凉后出现咳嗽，咳黄痰，伴发热，体温波动在37.8-38.5℃之间。自行服用感冒药效果不佳。",
            diagnosis="急性支气管炎",
            notes="建议多休息，多饮水，3天后复诊",
        ),
        MedicalRecord(
            visit_date=date(2025, 5, 20),
            hospital="北京大学第三医院",
            department="骨科",
            doctor="王强",
            chief_complaint="右膝关节疼痛1个月，活动后加重",
            present_illness="患者1个月前开始出现右膝关节疼痛，上下楼梯时明显，休息后缓解。无外伤史。",
            diagnosis="右膝骨关节炎（早期）",
            notes="建议控制体重，避免登山爬楼等负重活动",
        ),
        MedicalRecord(
            visit_date=date(2025, 8, 10),
            hospital="北京协和医院",
            department="消化内科",
            doctor="张丽",
            chief_complaint="上腹部隐痛2周，伴反酸烧心",
            present_illness="患者近2周无明显诱因出现上腹部隐痛，餐后明显，伴反酸、烧心。偶有嗳气。",
            diagnosis="慢性胃炎、胃食管反流",
            notes="幽门螺杆菌检测阳性，建议四联疗法根除",
        ),
        MedicalRecord(
            visit_date=date(2025, 11, 5),
            hospital="北京安贞医院",
            department="心血管内科",
            doctor="赵刚",
            chief_complaint="体检发现血压升高1周",
            present_illness="患者1周前体检发现血压145/95mmHg，无头痛头晕等不适。父母均有高血压病史。",
            diagnosis="原发性高血压（1级）",
            notes="建议低盐低脂饮食，监测血压，1个月后复诊",
        ),
        MedicalRecord(
            visit_date=date(2026, 1, 18),
            hospital="北京协和医院",
            department="眼科",
            doctor="陈静",
            chief_complaint="双眼干涩、视物模糊半年",
            present_illness="患者半年来双眼干涩感，用眼过度后加重，伴视物模糊。使用人工泪液可缓解。",
            diagnosis="干眼症、轻度近视",
            notes="建议减少电子产品使用时间，每用眼45分钟休息10分钟",
        ),
    ]
    db.session.add_all(records)
    db.session.flush()

    # ========== 检验检查结果 ==========
    exams = [
        ExamResult(
            exam_date=date(2025, 3, 15),
            hospital="北京协和医院",
            category="检验",
            exam_name="血常规",
            result="WBC 12.5×10^9/L, NEUT% 78%",
            reference_range="WBC 3.5-9.5, NEUT% 40-75",
            unit="",
            conclusion="白细胞升高，中性粒细胞比例升高，提示细菌感染",
            medical_record_id=records[0].id,
        ),
        ExamResult(
            exam_date=date(2025, 3, 15),
            hospital="北京协和医院",
            category="检验",
            exam_name="C反应蛋白(CRP)",
            result="28 mg/L",
            reference_range="<5 mg/L",
            unit="mg/L",
            conclusion="CRP升高，提示炎症反应",
            medical_record_id=records[0].id,
        ),
        ExamResult(
            exam_date=date(2025, 5, 20),
            hospital="北京大学第三医院",
            category="检查",
            exam_name="右膝关节X光",
            result="",
            reference_range="",
            unit="",
            conclusion="右膝关节间隙轻度狭窄，髁间隆突变尖，符合骨关节炎改变",
            medical_record_id=records[1].id,
        ),
        ExamResult(
            exam_date=date(2025, 8, 10),
            hospital="北京协和医院",
            category="检验",
            exam_name="幽门螺杆菌呼气试验",
            result="阳性 (dpm=1850)",
            reference_range="<100 dpm",
            unit="dpm",
            conclusion="幽门螺杆菌感染阳性",
            medical_record_id=records[2].id,
        ),
        ExamResult(
            exam_date=date(2025, 8, 10),
            hospital="北京协和医院",
            category="检查",
            exam_name="胃镜",
            result="",
            reference_range="",
            unit="",
            conclusion="慢性非萎缩性胃炎（胃窦为主），伴胆汁反流",
            medical_record_id=records[2].id,
        ),
        ExamResult(
            exam_date=date(2025, 11, 5),
            hospital="北京安贞医院",
            category="检验",
            exam_name="血脂四项",
            result="TC 5.8, TG 2.1, LDL 3.6, HDL 1.0",
            reference_range="TC<5.2, TG<1.7, LDL<3.4, HDL>1.0",
            unit="mmol/L",
            conclusion="总胆固醇、甘油三酯、低密度脂蛋白偏高",
            medical_record_id=records[3].id,
        ),
        ExamResult(
            exam_date=date(2026, 1, 18),
            hospital="北京协和医院",
            category="检查",
            exam_name="视力检查",
            result="右眼0.6, 左眼0.5",
            reference_range="≥1.0",
            unit="",
            conclusion="双眼视力下降",
            medical_record_id=records[4].id,
        ),
    ]
    db.session.add_all(exams)

    # ========== 处方 ==========
    prescriptions = [
        Prescription(
            prescription_date=date(2025, 3, 15),
            hospital="北京协和医院",
            doctor="李明",
            diagnosis="急性支气管炎",
            notes="服药期间避免饮酒",
            medical_record_id=records[0].id,
        ),
        Prescription(
            prescription_date=date(2025, 8, 10),
            hospital="北京协和医院",
            doctor="张丽",
            diagnosis="慢性胃炎、胃食管反流，幽门螺杆菌阳性",
            notes="四联疗法14天，停药1个月后复查呼气试验",
            medical_record_id=records[2].id,
        ),
        Prescription(
            prescription_date=date(2025, 11, 5),
            hospital="北京安贞医院",
            doctor="赵刚",
            diagnosis="原发性高血压（1级）",
            notes="每日早晨服用，监测血压",
            medical_record_id=records[3].id,
        ),
    ]
    db.session.add_all(prescriptions)
    db.session.flush()

    # ========== 处方明细 ==========
    items = [
        # 处方1：急性支气管炎
        PrescriptionItem(prescription_id=prescriptions[0].id, drug_name="阿莫西林胶囊", dosage="0.5g", frequency="每日3次", route="口服", duration="7天", quantity="2盒", notes="餐后服用"),
        PrescriptionItem(prescription_id=prescriptions[0].id, drug_name="氨溴索片", dosage="30mg", frequency="每日3次", route="口服", duration="7天", quantity="1盒", notes="祛痰"),
        PrescriptionItem(prescription_id=prescriptions[0].id, drug_name="布洛芬缓释胶囊", dosage="300mg", frequency="必要时", route="口服", duration="3天", quantity="1盒", notes="体温超过38.5℃时服用"),
        # 处方2：慢性胃炎四联疗法
        PrescriptionItem(prescription_id=prescriptions[1].id, drug_name="阿莫西林胶囊", dosage="1.0g", frequency="每日2次", route="口服", duration="14天", quantity="4盒", notes="抗幽门螺杆菌"),
        PrescriptionItem(prescription_id=prescriptions[1].id, drug_name="克拉霉素片", dosage="500mg", frequency="每日2次", route="口服", duration="14天", quantity="2盒", notes="抗幽门螺杆菌"),
        PrescriptionItem(prescription_id=prescriptions[1].id, drug_name="奥美拉唑肠溶胶囊", dosage="20mg", frequency="每日2次", route="口服", duration="14天", quantity="2盒", notes="餐前30分钟服用"),
        PrescriptionItem(prescription_id=prescriptions[1].id, drug_name="胶体果胶铋胶囊", dosage="200mg", frequency="每日2次", route="口服", duration="14天", quantity="2盒", notes="餐前服用，大便变黑正常"),
        # 处方3：高血压
        PrescriptionItem(prescription_id=prescriptions[2].id, drug_name="硝苯地平缓释片", dosage="30mg", frequency="每日1次", route="口服", duration="30天", quantity="1盒", notes="每日早晨服用"),
        PrescriptionItem(prescription_id=prescriptions[2].id, drug_name="厄贝沙坦片", dosage="150mg", frequency="每日1次", route="口服", duration="30天", quantity="1盒", notes="每日早晨服用"),
    ]
    db.session.add_all(items)

    db.session.commit()
    print("✅ 测试数据生成完成！")
    print(f"  - 就医记录: {MedicalRecord.query.count()} 条")
    print(f"  - 检验检查: {ExamResult.query.count()} 条")
    print(f"  - 处方: {Prescription.query.count()} 条")
    print(f"  - 药品明细: {PrescriptionItem.query.count()} 条")
