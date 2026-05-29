from .records import records_bp
from .exams import exams_bp
from .prescriptions import prescriptions_bp


def register_blueprints(app):
    """注册所有蓝图"""
    app.register_blueprint(records_bp, url_prefix="/records")
    app.register_blueprint(exams_bp, url_prefix="/exams")
    app.register_blueprint(prescriptions_bp, url_prefix="/prescriptions")
