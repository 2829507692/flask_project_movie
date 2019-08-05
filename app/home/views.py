from . import home
from flask import render_template, redirect, url_for, request, session, flash, jsonify
from app.home import forms
from app import mysql_db
from app import models
from werkzeug.security import generate_password_hash
from app.utils.add_log import AddLog
from functools import wraps
from app import app
from app.utils.file_genarate import File


def login_requried(func):
    @wraps(func)
    def inner(*args, **kwargs):
        path = request.full_path
        use = models.User.query.filter_by(name=session.get('user', None)).first()
        if use:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('home.login', next=path))

    return inner


# 首页
@home.route('/')
@home.route('/<int:page>')
def index(page=1):
    tags = models.Category.query.all()
    page_data = models.Movie.query
    # 标签
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(category_id=int(tid))
    # 星级
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(score=int(star))
    # 时间
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                models.Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                models.Movie.addtime.asc()
            )
    # 播放量
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                models.Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                models.Movie.playnum.asc()
            )
    # 评论量
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                models.Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                models.Movie.commentnum.asc()
            )
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=9)
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )
    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


# 搜索页面
@home.route('/search')
def search():
    key = request.args.get('key')
    obj = models.Movie.query.filter(models.Movie.name.ilike("%{}%".format(key))).all()
    return render_template('home/search.html', obj=obj, key=key)


##播放页面
@home.route('/play')
def play():
    id = request.args.get('id', None)
    if id is None:
        return redirect('home.index')
    movie = models.Movie.query.filter_by(id=id).first_or_404()
    movie.playnum += 1
    mysql_db.session.add(movie)
    mysql_db.session.commit()
    return render_template('home/play.html', movie=movie)


##添加评论
@home.route('/add_coments', methods=['post', 'get'])
@login_requried
def add_comment():
    if request.form.get("comment"):
        com_obj = models.Comment(
            user_id=session['id'],
            content=request.form.get("comment"),
            movie_id=request.args.get('movie_id')
        )
        mysql_db.session.add(com_obj)
        mysql_db.session.commit()
    else:
        flash('请填写评论！！',category='add')
    return redirect(url_for('home.play') + '?id={}'.format(request.args.get('movie_id')))


##轮播图
@home.route('/banner')
def banner():
    pre = models.Preview.query.all()
    return render_template('home/animation.html', pre=pre)


# 登录
@home.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.User()
    if form.validate_on_submit():
        user = models.User.query.filter_by(name=form.user.data).first()
        if not user.check_pwd(form.pwd.data):
            flash('密码错误')
            return redirect(url_for('home.login'))
        session['user'] = form.data['user']
        session['id'] = user.id
        AddLog.add_user_log()
        ##跳转判断
        next = request.args.get('next')
        if next:
            return redirect(next)
        return redirect(url_for('home.index'))
    return render_template('home/login.html', form=form)


# 用户注册页面
@home.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.Register()
    if form.validate_on_submit():
        user_obj = models.User(
            name=form.name.data,
            emial=form.email.data,
            pwd=generate_password_hash(form.pwd.data)
        )
        mysql_db.session.add(user_obj)
        mysql_db.session.commit()
        return redirect(url_for('home.user'))
    return render_template('home/register.html', form=form)


# 用户中心
@home.route('/user', methods=['GET', 'POST'])
@login_requried
def user():
    form = forms.Info()
    path = app.config["UP_DIR"]
    user_obj = models.User.query.filter_by(id=session['id']).first_or_404()
    if form.validate_on_submit():
        user_obj.name = form.name.data
        user_obj.emial = form.email.data
        avatar_path = File(form.avatar.data, path).save_user_logo(user_obj.avatar)
        user_obj.avatar = avatar_path
        user_obj.info = form.info.data
        mysql_db.session.add(user_obj)
        mysql_db.session.commit()
    form.name.data = user_obj.name
    form.email.data = user_obj.emial
    form.avatar.data = user_obj.avatar
    form.info.data = user_obj.info
    return render_template('home/user.html', form=form)


# 密码修改
@home.route('/pwd', methods=['GET', 'POST'])
@login_requried
def pwd():
    form = forms.Pwd()
    if form.validate_on_submit():
        user_obj = models.User.query.filter_by(id=session['id']).first_or_404()
        if user_obj.check_pwd(form.old_pwd.data):
            user_obj.pwd = generate_password_hash(form.new_pwd.data)
            mysql_db.session.add(user_obj)
            mysql_db.session.commit()
            return redirect(url_for('home.logout'))
        flash('原密码错误')
        return redirect(url_for('home.pwd'))
    return render_template('home/pwd.html', form=form)


##评论列表
@home.route('/comments/<int:page>')
@login_requried
def comments(page=1):
    con = models.Comment.query.filter(models.Comment.user_id == session['id']).order_by(
        models.Comment.addtime.desc()).paginate(page=page, per_page=8)
    return render_template('home/comments.html', con=con)


##登录日志
@home.route('/loginlog/<int:page>')
@login_requried
def loginlog(page=1):
    log = models.UserLog.query.filter(models.UserLog.user_id == session['id']).order_by(
        models.UserLog.addtime.desc()).paginate(page=page, per_page=8)
    return render_template('home/loginlog.html', log=log)


##收藏列表
@home.route('/moviecol/<int:page>')
@login_requried
def moviecol(page=1):
    col = models.Moviecol.query.filter(models.Moviecol.user_id == session['id']).order_by(
        models.Moviecol.addtime.desc()).paginate(page=page, per_page=8)
    return render_template('home/moviecol.html', col=col)


##添加收藏
@home.route('/moviecol_add')
@login_requried
def moviecol_add():
    res = request.args.to_dict()
    q = models.Moviecol.query.filter(
        models.Moviecol.user_id == int(res['uid']) and models.Moviecol.movie_id == int(res['mid'])).first()
    if not q:
        col = models.Moviecol(
            user_id=int(res['uid']),
            movie_id=int(res['mid']),
        )
        mysql_db.session.add(col)
        mysql_db.session.commit()
        return jsonify({'code': 1})
    else:
        return jsonify({'code': 0})


##退出登录
@home.route('/logout')
@login_requried
def logout():
    session.pop('user', None)
    session.pop('id', None)
    return redirect(url_for('home.index'))
