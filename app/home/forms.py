from flask_wtf import FlaskForm
from app import models
from wtforms import ValidationError, PasswordField, StringField, SubmitField, validators, FileField, TextAreaField


class Register(FlaskForm):
    name = StringField(label='用户名',
                       validators=[validators.data_required('请输入用户名')],
                       render_kw={"id": "input_name", "class": "form-control input-lg", "placeholder": "请输入用户名",
                                  })

    email = StringField(label='邮箱',
                        validators=[validators.data_required('请输入邮箱'),
                                    validators.regexp(
                                        regex=r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$',
                                        message='请输入正确的邮箱')],
                        render_kw={"id": "input_email", "class": "form-control input-lg", "placeholder": "请输入邮箱",
                                   })

    pwd = PasswordField(label='密码',
                        validators=[validators.data_required('请输入密码'), validators.length(min=8)],
                        render_kw={"id": "input_password", "class": "form-control input-lg", "placeholder": "请输入密码",
                                   })
    re_pwd = PasswordField(label='确认密码',
                           validators=[validators.data_required('请再输入一次密码'), validators.length(min=8),
                                       validators.equal_to('pwd')],
                           render_kw=
                           {"id": "input_repassword", "class": "form-control input-lg", "placeholder": "请确认密码",
                            })
    submit = SubmitField(label='注册',
                         render_kw={'class': 'btn btn-primary btn-block btn-flat'})

    def validate_name(self, filed):
        name = filed.data
        movie_obj = models.User.query.filter_by(name=name).first()
        if movie_obj:
            raise ValidationError('用户名已经存在')

    def validate_email(self, filed):
        email = filed.data
        user_obj = models.User.query.filter_by(emial=email).first()
        if user_obj:
            raise ValidationError('邮箱已经被使用')


class User(FlaskForm):
    user = StringField(label='账号',
                       validators=[validators.data_required(message='不能为空！')],
                       render_kw={'class': 'form-control', 'placeholder': '请输入账号！'}
                       )

    pwd = PasswordField(label='密码',
                        validators=[validators.data_required(message='不能为空！'),
                                    validators.length(min=5, message='密码长度不能小于8位')],
                        render_kw={'class': 'form-control', 'placeholder': '请输入密码！'}
                        )
    login = SubmitField(label='登录',
                        render_kw={'class': 'btn btn-primary btn-block btn-flat'})

    # 自定义校验器,validate+字段名
    def validate_user(self, field):
        user = field.data
        admin = models.User.query.filter_by(name=user).first()
        if not admin:
            raise ValidationError("账号不存在！")


class Info(FlaskForm):
    name = StringField(label='用户名',
                       validators=[validators.data_required('请输入用户名')],
                       render_kw={"id": "input_name", "class": "form-control", "placeholder": "请输入用户名",
                                  })

    email = StringField(label='邮箱',
                        validators=[validators.data_required('请输入邮箱'),
                                    validators.regexp(
                                        regex=r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$',
                                        message='请输入正确的邮箱')],
                        render_kw={"id": "input_email", "class": "form-control", "placeholder": "请输入邮箱",
                                   })

    avatar = FileField(label='头像',
                       render_kw={"id": "input_logo"})

    info = TextAreaField(label='简介',
                         render_kw={"id": "input_info", "rows": "10", "class": "form-control",
                                    })
    submit = SubmitField(label='保存修改',
                         render_kw={'class': 'btn btn-success'})


class Pwd(FlaskForm):
    old_pwd = PasswordField(label='旧密码',
                            validators=[validators.data_required('请输入旧密码')],
                            render_kw={"class": "form-control", "id":"input_oldpwd", "placeholder": "请输入旧密码！"})
    new_pwd = PasswordField(label='新密码',
                            validators=[validators.data_required('请输入新密码'), validators.length(min=8,message='密码长度至少为8位')],
                            render_kw={"class": "form-control", "id": "input_newpwd", "placeholder": "请输入新密码！"})

    submit = SubmitField(label='提交',
                         render_kw={"class": "btn btn-success"})