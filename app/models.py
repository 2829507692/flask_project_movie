from app import mysql_db
from datetime import datetime


####用户相关
# 会员
class User(mysql_db.Model):
    __tablename__ = 'user'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    name = mysql_db.Column(mysql_db.String(64), unique=True, nullable=False)
    pwd = mysql_db.Column(mysql_db.String(128), nullable=False)
    emial = mysql_db.Column(mysql_db.String(64), unique=True)
    info = mysql_db.Column(mysql_db.Text)
    avatar = mysql_db.Column(mysql_db.String(64), unique=True)
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)
    userlogs = mysql_db.relationship('UserLog', backref='user')
    comments = mysql_db.relationship('Comment', backref='user')
    moviecol = mysql_db.relationship('Moviecol', backref='user')

    def __repr__(self):
        return '<User %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


# 会员登录日志
class UserLog(mysql_db.Model):
    __tablename__ = 'userlog'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    user_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('user.id'), onupdate=True)
    ip = mysql_db.Column(mysql_db.String(64))
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<UserLog %r>' % self.id


# 评论
class Comment(mysql_db.Model):
    __tablename__ = 'comment'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    content = mysql_db.Column(mysql_db.Text)
    user_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('user.id'))
    movie_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('movie.id'))
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Comment %r>' % self.id


# 收藏
class Moviecol(mysql_db.Model):
    __tablename__ = "moviecol"
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)  # 编号
    movie_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('movie.id'))
    user_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('user.id'))
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Moviecol %r' % self.id


###用户结束

###电影相关

# 电影分类
class Category(mysql_db.Model):
    __tablename__ = 'category'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    title = mysql_db.Column(mysql_db.String(64), unique=True)
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)
    movie = mysql_db.relationship('Movie', backref='category')

    def __repr__(self):
        return '<Category %r' % self.title


# 电影
class Movie(mysql_db.Model):
    __tablename__ = 'movie'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    name = mysql_db.Column(mysql_db.String(64), unique=True)
    url = mysql_db.Column(mysql_db.String(128), unique=True)
    info = mysql_db.Column(mysql_db.Text)
    logo = mysql_db.Column(mysql_db.String(128), unique=True)
    score = mysql_db.Column(mysql_db.BigInteger)
    playnum = mysql_db.Column(mysql_db.Integer)
    area = mysql_db.Column(mysql_db.String(64))
    release_time = mysql_db.Column(mysql_db.Date)
    length = mysql_db.Column(mysql_db.String(64))  # 播放时长
    category_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('category.id'))
    moviecol=mysql_db.relationship("Moviecol", backref='movie')
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)
    comments = mysql_db.relationship("Comment", backref='movie')

    def __repr__(self):
        return '<Movie %r' % self.name


# 上映预告
class Preview(mysql_db.Model):
    __tablename__ = "preview"
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)  # 编号
    title = mysql_db.Column(mysql_db.String(64), unique=True)  # 标题
    logo = mysql_db.Column(mysql_db.String(128), unique=True)  # 封面
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return "<Preview %r>" % self.title


###电影结束

###管理员相关

# admin
class Admin(mysql_db.Model, ):
    __tablename__ = 'admin'
    __table_args__ = {"useexisting": True}
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    name = mysql_db.Column(mysql_db.String(64), unique=True)
    pwd = mysql_db.Column(mysql_db.String(128))
    is_super = mysql_db.Column(mysql_db.SmallInteger, default=1)
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)
    adminlogs = mysql_db.relationship("AdminLog", backref='admin')
    oplogs = mysql_db.relationship("OpLog", backref='admin')
    role_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('role.id'))

    def __repr__(self):
        return '<Admin %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


# 登录记录
class AdminLog(mysql_db.Model):
    __tablename__ = 'adminlog'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    ip = mysql_db.Column(mysql_db.String(64))
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)
    admin_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('admin.id'))

    def __repr__(self):
        return '<Admin %r>' % self.id


# 操作记录
class OpLog(mysql_db.Model):
    __tablename__ = 'oplog'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    ip = mysql_db.Column(mysql_db.String(64))
    reason = mysql_db.Column(mysql_db.String(128))
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)
    admin_id = mysql_db.Column(mysql_db.Integer, mysql_db.ForeignKey('admin.id'))

    def __repr__(self):
        return '<Admin %r>' % self.id


###管理员结束

###权限开始

##权限
class Auth(mysql_db.Model):
    __tablename__ = 'auth'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    name = mysql_db.Column(mysql_db.String(64), unique=True)
    url = mysql_db.Column(mysql_db.String(128), unique=True)
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return '<Auth %r>' % self.name


# 角色
class Role(mysql_db.Model):
    __tablename__ = 'role'
    id = mysql_db.Column(mysql_db.Integer, primary_key=True)
    name = mysql_db.Column(mysql_db.String(64), unique=True)
    auths = mysql_db.Column(mysql_db.String(128))
    admins = mysql_db.relationship("Admin", backref='role')
    addtime = mysql_db.Column(mysql_db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Role %r>" % self.name


if __name__ == "__main__":
    # mysql_db.drop_all()
    # mysql_db.create_all()
    #
    # r1 = Role(
    #      name="管理员",
    #      auths=""
    #  )

    from werkzeug.security import generate_password_hash

    # a1=Admin(
    #     name='root',
    #     pwd=generate_password_hash('love2'),
    #     role_id=1
    # )
    # mysql_db.session.commit()
