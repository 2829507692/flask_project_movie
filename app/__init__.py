from flask import Flask, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
import os

# 连接数据库
app = Flask(__name__, static_url_path='/static/')

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:123456@127.0.0.1:3306/movie"
##保持数据一致
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config["SECRET_KEY"] = b'dnao.,.v/asdfl,pcaspo,.calfdda'
app.config["DEBUG"] = True

app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files')

mysql_db = SQLAlchemy(app)

# 导入蓝图
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

# 注册蓝图
app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")


@app.errorhandler(404)
def errorpage(error):
    return render_template('404/404.html'), 404


@app.route('/files/<string:filename>')
def files(filename=None):
    try:
        file = os.path.join(app.config["UP_DIR"], filename)
        if not os.path.exists(file):
            return '文件不存在'
        return send_file(file)
    except FileNotFoundError as e:
        pass


if __name__ == '__main__':
    print(app.url_map)
