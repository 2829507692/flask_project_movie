from flask import Blueprint
admin=Blueprint('admin',__name__)

##导入视图函数
from app.admin import views

