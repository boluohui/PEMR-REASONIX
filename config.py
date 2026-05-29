import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """应用配置"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "med-records-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "medical_records.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 每页显示条数
    PER_PAGE = 20
    # 启动端口
    PORT = 5300
