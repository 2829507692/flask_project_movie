from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, ValidationError, \
    FileField, TextAreaField, SelectField, SelectMultipleField, RadioField
from app import models


##管理员登录表单
class Admin(FlaskForm):
    user = StringField(label='账号',
                       validators=[validators.data_required(message='不能为空！')],
                       render_kw={'class': 'form-control input-lg', 'placeholder': '请输入账号！'}
                       )

    pwd = PasswordField(label='密码',
                        validators=[validators.data_required(message='不能为空！'),
                                    validators.length(min=5, message='密码长度不能小于8位')],
                        render_kw={'class': 'form-control input-lg', 'placeholder': '请输入密码！'}
                        )
    login = SubmitField(label='登录',
                        render_kw={'class': 'btn btn-primary btn-block btn-flat'})

    # 自定义校验器,validate+字段名
    def validate_user(self, field):
        user = field.data
        admin = models.Admin.query.filter_by(name=user).first()
        if not admin:
            raise ValidationError("账号不存在！")


##添加标签表单
class Add_Tag(FlaskForm):
    title = StringField(label='标签', validators=[validators.required('请填写标签')],
                        render_kw={
                            "class": "form-control",
                            "id": "input_name",
                            "placeholder": "请输入标签名称！"
                        })
    login = SubmitField(label='提交',
                        render_kw={'class': 'btn btn-success'})

    def validate_title(self, field):
        title = field.data
        title_obj = models.Category.query.filter_by(title=title).first()
        if title_obj:
            raise ValidationError('标签已经存在')


# 添加电影表单
class Add_Movie(FlaskForm):
    name = StringField(label='片名',
                       validators=[validators.data_required(message='请填写片名')],
                       render_kw={"class": "form-control", "id": "input_title", "placeholder": "请输入片名！"})

    url = FileField(label='文件',
                    validators=[validators.data_required(message='请选择文件')],
                    render_kw={"id": "input_url"})

    info = TextAreaField(label='简介',
                         validators=[validators.data_required(message='请填写影片信息')],
                         render_kw={"class": "form-control", "id": "input_info"})

    logo = FileField(label='封面',
                     validators=[validators.data_required(message='请选择文件')],
                     render_kw={"id": "input_logo"})

    score = SelectField(label='星级',
                        render_kw={"class": "form-control", "id": "input_star"},
                        coerce=int,
                        choices=[(1, '1星'), (2, '2星'), (3, '3星'), (4, '4星'), (5, '5星')])

    tag_obj = models.Category.query.all()
    tag = SelectField(label='标签',
                      render_kw={"class": "form-control", "id": "input_tag_id"},
                      coerce=int,
                      choices=[(t.id, t.title) for t in tag_obj])

    area = StringField(label='地区',
                       validators=[validators.data_required(message='请填写地区')],
                       render_kw={"class": "form-control", "id": "input_area", "placeholder": "请输入地区！"})

    length = StringField(label='时长',
                         validators=[validators.data_required(message='请填写时长')],
                         render_kw={"class": "form-control", "id": "input_area", "placeholder": "请输入时长！"})

    release_time = StringField(label='上映日期',
                               validators=[validators.data_required(message='请选择上映日期')],
                               render_kw={"class": "form-control", "id": "input_release_time", "placeholder": "请上映时间！"}
                               )

    submit = SubmitField(label='提交',
                         render_kw={"class": "btn btn-primary"})

    def validate_movie(self, filed):
        name = filed.data
        movie_obj = models.Movie.query.filter_by(name=name).first()
        if movie_obj:
            raise ValidationError('电影名字已经存在')


class Priview(FlaskForm):
    title = StringField(label='片名',
                        validators=[validators.data_required(message='请填写片名')],
                        render_kw={"class": "form-control", "id": "input_title", "placeholder": "请输入预告标题！"})
    logo = FileField(label='封面',
                     validators=[validators.data_required(message='请选择文件')],
                     render_kw={"id": "input_logo"})

    submit = SubmitField(label='提交',
                         render_kw={"class": "btn btn-primary"})

    def validate_title(self, filed):
        title = filed.data
        movie_obj = models.Preview.query.filter_by(title=title).first()
        if movie_obj:
            raise ValidationError('预告名字已经存在')


class Pwd(FlaskForm):
    old_pwd = PasswordField(label='旧密码',
                            validators=[validators.data_required('请输入旧密码')],
                            render_kw={"class": "form-control", "id": "input_pwd", "placeholder": "请输入旧密码！"})
    new_pwd = PasswordField(label='新密码',
                            validators=[validators.data_required('请输入新密码'), validators.length(min=8)],
                            render_kw={"class": "form-control", "id": "input_newpwd", "placeholder": "请输入新密码！"})

    submit = SubmitField(label='提交',
                         render_kw={"class": "btn btn-primary"})


# 添加权限

class Auth(FlaskForm):
    name = StringField(label='权限名称',
                       validators=[validators.data_required('请输入权限名称')],
                       render_kw={"class": "form-control", "id": "input_name", "placeholder": "请输入权限名称"})
    addr = StringField(label='权限地址',
                       validators=[validators.data_required('请输入权限名称')],
                       render_kw={"class": "form-control", "id": "input_name", "placeholder": "请输入权限地址"})
    submit = SubmitField(label='提交',
                         render_kw={"class": "btn btn-primary"})

    def validate_name(self, field):
        name = field.data
        data = models.Auth.query.filter_by(name=name).first()
        if data:
            raise ValidationError('权限名称已经存在')


class Role(FlaskForm):
    name = StringField(label='权限名称',
                       validators=[validators.data_required('请输入角色名称')],
                       render_kw={"class": "form-control", "id": "input_name", "placeholder": "请输入角色名称"})
    data = models.Auth.query.all()

    auths = SelectMultipleField(label='选择权限',
                                choices=[(str(v.id), v.url) for v in data],
                                validators=[validators.data_required('请选择权限')],
                                render_kw={"class": "form-control", "id": "input_url", "placeholder": "请选择权限"})

    submit = SubmitField(label='提交',
                         render_kw={"class": "btn btn-primary"})

    def validate_name(self, field):
        name = field.data
        data = models.Role.query.filter_by(name=name).first()
        if data:
            raise ValidationError('角色名称已经存在')


class Admin_add(FlaskForm):
    name = StringField(label='管理员名字',
                       validators=[validators.data_required('请输入管理员名称')],
                       render_kw={"class": "form-control", "id": "input_name", "placeholder": "请输入角色名称"})
    pwd = PasswordField(label='请输入密码',
                        validators=[validators.data_required('请输入密码'), validators.length(min=8)],
                        render_kw={"class": "form-control", "id": "input_pwd", "placeholder": "请输入密码！"})
    re_pwd = PasswordField(label='请确认密码',
                           validators=[validators.data_required('请确认密码'), validators.length(min=8),
                                       validators.equal_to('pwd')],
                           render_kw={"class": "form-control", "id": "input_re_pwd", "placeholder": "请确认密码！"})
    #
    # super = SelectField(label='选择管理员身份',
    #                    choices=[(0, '普通管理员'),(1, '超级管理员')],
    #                    validators=[validators.data_required('请选择身份')],
    #                    render_kw={"class": "form-control", "id": "is_super", "placeholder": "请选择身份"})


    datas = models.Role.query.all()
    role = SelectField(label='选择角色',
                       choices=[(str(v.id), v.name) for v in datas],
                       validators=[validators.data_required('请选择角色')],
                       render_kw={"class": "form-control", "id": "input_role_id", "placeholder": "请选择角色"})

    submit = SubmitField(label='提交',
                         render_kw={"class": "btn btn-primary"})

    def validate_name(self, field):
        name = field.data
        data = models.Admin.query.filter_by(name=name).first()
        if data:
            raise ValidationError('管理员名字重复')
