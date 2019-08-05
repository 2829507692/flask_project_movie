from . import admin
from flask import render_template, url_for, redirect, flash, session, request
from app import mysql_db
from app import models
from app.admin import forms
import os
from app import app
from app.utils.file_genarate import File
from werkzeug.security import generate_password_hash
from app.utils.add_log import AddLog


##登录校验
@admin.before_request
def before_requeset():
    path = request.path
    use = models.Admin.query.filter_by(name=session.get('user', None)).first()
    if use:
        return
    elif path == '/admin/login':
        return
    else:
        return redirect(url_for('admin.login', next=path))

##管理员首页
@admin.route('/')
def index():
    return render_template('admin/index.html')


# 管理员登录页面
@admin.route('/login', methods=["GET", "POST"])
def login():
    form = forms.Admin()
    if form.validate_on_submit():
        user = models.Admin.query.filter_by(name=form.data['user']).first()
        if not user.check_pwd(form.data['pwd']):
            flash('密码错误')
            return redirect(url_for('admin.login'))
        session['user'] = form.data['user']
        session['id'] = user.id
        AddLog.add_admin_log()
        ##跳转判断
        next = request.args.get('next')
        if next:
            return redirect(next)
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html', form=form)


##修改密码

@admin.route('/pwd', methods=["GET", "POST"])
def pwd():
    form = forms.Pwd()
    if form.validate_on_submit():
        admin_obj = models.Admin.query.filter_by(name=session['user']).first()
        if admin_obj.check_pwd(form.old_pwd.data):
            print(form.data)
            admin_obj.pwd = generate_password_hash(form.new_pwd.data)
            mysql_db.session.add(admin_obj)
            mysql_db.session.commit()
            return redirect(url_for('admin.logout'))
        return redirect(url_for('admin.pwd'))
    return render_template('admin/pwd.html', form=form)


##退出登录
@admin.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('id', None)
    return redirect('/admin/login')


##标签列表
@admin.route('/tag_list/<int:page>')
def tag_list(page=1):
    pagination = models.Category.query.order_by(models.Category.addtime.desc()).paginate(page=page, per_page=8)
    return render_template('admin/tag_list.html', pagination=pagination)


##添加标签
@admin.route('/tag_add', methods=["GET", "POST"])
def tag_add():
    form = forms.Add_Tag()
    if form.validate_on_submit():
        Tag = models.Category(title=form.data['title'])
        mysql_db.session.add(Tag)
        mysql_db.session.commit()
        flash('添加成功', category='add')
        AddLog.add_oplog('添加标签')
        return redirect(url_for('admin.tag_add'))
    return render_template('admin/add_tag.html', form=form)


##编辑标签
@admin.route('/tag_edit/<int:id>', methods=['GET', 'POST'])
def tag_edit(id=None):
    print(request.path)
    tag_obj = models.Category.query.filter_by(id=id).first()
    if request.method == "POST":
        value = request.form.get('title')
        if value:
            tag_obj.title = value
            mysql_db.session.add(tag_obj)
            mysql_db.session.commit()
            AddLog.add_oplog('编辑标签')
            return redirect(url_for('admin.tag_list', page=1))
    return render_template('admin/tag_edit.html', tag_obj=tag_obj)


##删除标签
@admin.route('/tag_del/<int:id>')
def tag_del(id=None):
    tag_obj = models.Category.query.filter_by(id=id).first_or_404()
    mysql_db.session.delete(tag_obj)
    mysql_db.session.commit()
    AddLog.add_oplog('删除标签')
    return redirect(url_for('admin.tag_list', page=1))


##电影列表
@admin.route('/movie_list/<int:page>')
def movie_list(page=1):
    paginition = models.Movie.query.join(models.Category).order_by(models.Movie.addtime.desc()).paginate(page=page,
                                                                                                         per_page=8)
    return render_template('admin/move_list.html', paginition=paginition)


##添加电影
@admin.route('/movie_add', methods=['GET', 'POST'])
def movie_add():
    form = forms.Add_Movie()
    path = app.config["UP_DIR"]
    if form.validate_on_submit():
        url = File(form.url.data, path)
        logo = File(form.logo.data, path)

        movie_obj = models.Movie(
            name=form.data['name'],
            url=url.safe_filename_save(),
            logo=logo.safe_filename_save(),
            info=form.data['info'],
            score=int(form.data['score']),
            playnum=0,
            area=form.data['area'],
            length=form.data['length'],
            category_id=form.data['tag'],
            release_time=form.data['release_time']
        )
        mysql_db.session.add(movie_obj)
        mysql_db.session.commit()
        AddLog.add_oplog('添加电影')
        return redirect(url_for('admin.movie_list', page=1))
    return render_template('admin/movie_add.html', form=form)


##删除电影
@admin.route('/movie_del/<int:id>')
def movie_del(id=None):
    path = app.config["UP_DIR"]
    movie_obj = models.Movie.query.filter_by(id=id).first_or_404()
    mysql_db.session.delete(movie_obj)
    mysql_db.session.commit()
    AddLog.add_oplog('删除电影')
    try:
        os.remove(os.path.join(path, movie_obj.url))
        os.remove(os.path.join(path, movie_obj.logo))
    except FileNotFoundError as e:
        print(e.args)
        pass
    return redirect(url_for('admin.movie_list', page=1))


##编辑电影
@admin.route('/movie_edit/<int:id>', methods=['GET', 'POST'])
def movie_edit(id=None):
    path = app.config["UP_DIR"]
    form = forms.Add_Movie()
    movie_obj = models.Movie.query.filter_by(id=id).first_or_404()

    ##修改数据库文件
    if request.method == 'POST':
        movie_obj.name = form.name.data
        movie_obj.url = File(form.url.data, path).exit_filename(movie_obj.url)
        movie_obj.logo = File(form.logo.data, path).exit_filename(movie_obj.logo)
        movie_obj.info = form.info.data
        movie_obj.score = form.score.data
        movie_obj.area = form.area.data
        movie_obj.length = form.length.data
        movie_obj.category_id = form.tag.data
        movie_obj.release_time = form.release_time.data
        mysql_db.session.add(movie_obj)
        mysql_db.session.commit()
        AddLog.add_oplog('编辑电影')
        return redirect(url_for('admin.movie_list', page=1))

    ##显示数据页面
    form.info.data = movie_obj.info
    form.logo.data = movie_obj.logo
    form.url.data = movie_obj.url
    form.score.data = movie_obj.score
    form.tag.data = movie_obj.category_id
    return render_template('admin/movie_edit.html', movie_obj=movie_obj, form=form)


# 预告列表

@admin.route('/preview_list/<int:page>')
def preview_list(page=1):
    pres = models.Preview.query.order_by(models.Preview.addtime.desc()).paginate(page=page, per_page=4)
    return render_template('admin/movie_priview.html', pres=pres)


##删除预告
@admin.route('/preview_del/<int:id>')
def preview_del(id=None):
    path = app.config["UP_DIR"]
    pre_obj = models.Preview.query.filter_by(id=id).first_or_404()
    mysql_db.session.delete(pre_obj)
    mysql_db.session.commit()
    AddLog.add_oplog('删除预告')
    try:
        os.remove(os.path.join(path, pre_obj.logo))
    except FileNotFoundError as e:
        print(e.args)
        pass
    return redirect(url_for('admin.preview_list', page=1))


# 编辑预告
@admin.route('preview_edit/<int:id>', methods=['GET', 'POST'])
def preview_edit(id=None):
    path = app.config["UP_DIR"]
    pre_obj = models.Preview.query.filter_by(id=id).first_or_404()
    form = forms.Priview()
    if request.method == 'POST':
        pre_obj.title = form.title.data
        pre_obj.logo = File(form.logo.data, path).exit_filename(pre_obj.logo)
        mysql_db.session.add(pre_obj)
        mysql_db.session.commit()
        return redirect(url_for('admin.preview_list', page=1))
    form.title.data = pre_obj.title
    form.logo.data = pre_obj.logo
    return render_template('admin/pre_edit.html', form=form)


# 添加预告
@admin.route('/preview_add', methods=['GET', 'POST'])
def preview_add():
    path = app.config["UP_DIR"]
    form = forms.Priview()
    if form.validate_on_submit():
        pre_obj = models.Preview(
            title=form.title.data,
            logo=File(form.logo.data, path).safe_filename_save()
        )
        mysql_db.session.add(pre_obj)
        mysql_db.session.commit()
        flash('添加成功', category='add')
        return redirect(url_for('admin.preview_add'))

    return render_template('admin/movie_preview_add.html', form=form)


# 用户列表页面
@admin.route('/user_list/<int:page>')
def user_list(page=1):
    users = models.User.query.order_by(models.User.addtime.desc()).paginate(page=page, per_page=8)
    return render_template('admin/user_list.html', users=users)


# 删除用户
@admin.route('/user_del/<int:id>')
def user_del(id=None):
    user_obj = models.User.query.filter_by(id=id).first_or_404()
    mysql_db.session.delete(user_obj)
    mysql_db.session.commit()
    AddLog.add_oplog('删除用户')
    return redirect(url_for('admin.user_list', page=1))


# 查看用户
@admin.route('/user_view/<int:id>')
def user_view(id=None):
    user_obj = models.User.query.filter_by(id=id).first_or_404()
    return render_template('admin/user_view.html', user_obj=user_obj)


# 查看管理员登录日志
@admin.route('/admin_log/<int:page>')
def admin_log(page=1):
    log = models.AdminLog.query.filter(models.AdminLog.admin_id == session['id']).order_by(
        models.AdminLog.addtime.desc()).paginate(page=page, per_page=8)
    return render_template('admin/admin_log.html', log=log)


# 查看用户登录日志
@admin.route('/user_log/<int:page>')
def user_log(page):
    users = models.UserLog.query.join(models.User).order_by(models.User.id.desc(), models.User.addtime.desc()).paginate(
        page=page, per_page=8)
    return render_template('admin/user_log.html', users=users)


# 查看操作日志
@admin.route('/opration_log/<int:page>')
def opration_log(page=1):
    logs=models.OpLog.query.filter(models.OpLog.admin_id == session['id']).order_by(
        models.OpLog.addtime.desc()).paginate(page=page, per_page=8)
    return render_template('admin/opration_log.html', log=logs)


# 权限
@admin.route('/auth/<int:page>')
def auth(page=1):
    auths = models.Auth.query.order_by(models.Auth.addtime.desc()).paginate(page=page, per_page=8)
    return render_template('admin/auth.html', auths=auths)


# 添加权限
@admin.route('/auth_add', methods=["GET", "POST"])
def auth_add():
    form = forms.Auth()
    if form.validate_on_submit():
        a = models.Auth(
            name=form.name.data,
            url=form.addr.data
        )
        mysql_db.session.add(a)
        mysql_db.session.commit()
        print(url_for('admin.auth_add'))
        return redirect(url_for('admin.auth_add'))
    return render_template('admin/auth_add.html', form=form)


# 删除权限
@admin.route('/auth_del/<int:id>')
def auth_del(id=None):
    del_obj = models.Auth.query.filter_by(id=id).first_or_404()
    if del_obj:
        mysql_db.session.delete(del_obj)
        mysql_db.session.commit()
        return redirect(url_for('admin.auth', page=1))


# 编辑权限
@admin.route('/auth_edit/<int:id>')
def auth_edit(id=None):
    edit_obj = models.Auth.query.filter_by(id=id).first_or_404()
    form = forms.Auth()
    if form.validate_on_submit():
        edit_obj.name = form.name.data
        edit_obj.url = form.addr.data
        mysql_db.session.add(edit_obj)
        mysql_db.session.commit()
        return redirect(url_for('admin.auth', page=1))
    form.name.data = edit_obj.name
    form.addr.data = edit_obj.url
    return render_template('admin/auth_edit.html', form=form)


# 角色

@admin.route('/roll/<int:page>')
def roll(page=1):
    rolls = models.Role.query.paginate(page=page, per_page=8)
    return render_template('admin/roll.html', rolls=rolls)


# 添加角色
@admin.route('/roll_add', methods=['POSt', 'GET'])
def roll_add():
    form = forms.Role()
    if form.validate_on_submit():
        role_obj = models.Role(
            name=form.name.data,
            auths='|'.join(form.auths.data)
        )
        mysql_db.session.add(role_obj)
        mysql_db.session.commit()
        return redirect(url_for('admin.roll', page=1))
    return render_template('admin/roll_add.html', form=form)


# 编辑角色
@admin.route('/roll_edit/<int:id>')
def roll_edit(id=None):
    edit_obj = models.Role.query.filter_by(id=id).first_or_404()
    form = forms.Role()
    if form.validate_on_submit():
        edit_obj.name = form.name.data
        edit_obj.auths = '|'.join(form.auths.data)
        mysql_db.session.add(edit_obj)
        mysql_db.session.commit()
        return redirect(url_for('admin.roll', page=1))
    form.name.data = edit_obj.name
    form.auths.data = edit_obj.auths.split('|')
    return render_template('admin/roll_edit.html', form=form)


# 删除角色
@admin.route('/roll_del/<int:id>')
def roll_del(id=None):
    del_obj = models.Role.query.filter_by(id=id).first_or_404()
    if del_obj:
        mysql_db.session.delete(del_obj)
        mysql_db.session.commit()
        return redirect(url_for('admin.roll', page=1))


@admin.route('/admins/<int:page>')
def admins(page=1):
    admins=models.Admin.query.order_by(models.Admin.addtime.desc()).paginate(page=page,per_page=8)
    return render_template('admin/admin_list.html',admins=admins)


@admin.route('/admin_add',methods=['GET','POST'])
def admin_add():
    form =forms.Admin_add()
    if form.validate_on_submit():
        admin_obj=models.Admin(
            name=form.name.data,
            pwd=form.pwd.data,
            is_super=0,
            role_id=form.role.data)
        mysql_db.session.add(admin_obj)
        mysql_db.session.commit()
        return redirect(url_for('admin.admins',page=1))
    return render_template('admin/admin_add.html',form=form)
