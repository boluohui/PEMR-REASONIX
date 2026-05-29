"""个人电子病历档案系统 — 应用入口"""

import markupsafe
from flask import Flask, render_template
from config import Config
from models import db, MedicalRecord, ExamResult, Prescription
from routes import register_blueprints


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册自定义 Jinja2 过滤器 - 换行转 <br>
    @app.template_filter("nl2br")
    def nl2br_filter(text):
        if not text:
            return ""
        return markupsafe.Markup(text.replace("\n", "<br>\n"))

    # 首页
    @app.route("/")
    def index():
        stats = {
            "records_count": MedicalRecord.query.count(),
            "exams_count": ExamResult.query.count(),
            "prescriptions_count": Prescription.query.count(),
        }
        return render_template("index.html", stats=stats)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",  # 允许远程访问
        port=Config.PORT,
        debug=False,     # 生产环境关闭 debug 模式
    )
