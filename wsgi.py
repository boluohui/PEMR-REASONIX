"""Gunicorn 入口文件"""
from app import create_app

app = create_app()
