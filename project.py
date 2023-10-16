import os
import secrets

from PIL.Image import Image
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import EqualTo, Email, Length, DataRequired, ValidationError
from flask import Flask, redirect, url_for, render_template, flash, request, abort
from flask_login import current_user, UserMixin, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from typing_extensions import final
from flask_login import LoginManager

app = Flask('__name__', template_folder='template')
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# from project import User, db

# FORMS


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Conform_Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign up')

    def validate_username(self, username):
        x = User.query.filter_by(username=username.data).first()
        if x:
            raise ValidationError('username taken!!, try another')

    def validate_email(self, email):
        x = User.query.filter_by(email=email.data).first()
        if x:
            raise ValidationError('this email exist!!, try another')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            x = User.query.filter_by(username=username.data).first()
            if x:
                raise ValidationError('username taken!!, try another')

    def validate_email(self, email):
        if email.data != current_user.email:
            x = User.query.filter_by(email=email.data).first()
            if x:
                raise ValidationError('this email exist!!, try another')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Email', validators=[DataRequired()])
    submit = SubmitField('Post')


# posts = [
#     {
#         'author': 'ram',
#         'title': 'Life',
#         'content': 'First_post',
#         'date_posted': 'April 20, 2023'
#
#     },
#     {
#         'author': 'sef',
#         'title': 'joy',
#         'content': 'First_post',
#         'date_posted': 'April 25, 2023'
#
#     }
# ]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# MODELS.........


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(50), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f' User({self.username}, {self.email}, {self.image_file})'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.String(), nullable=False, default='2018-02-11 00:52:12.553421')
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f' Post({self.title}, {self.date_posted})'

# ROUTES........


@app.route("/")
def home():
    return render_template("index.html", posts=Post.query.all())


@app.route("/about")
def about():
    return render_template('about.html', title='About')

# @app.route("/<name>")
# def main(name):
#     return render_template('about.html', content=name, title='About')

# from forms import RegistrationForm, LoginForm


# noinspection PyArgumentList
@app.route("/Register", methods=['GET', 'POST'])
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        print('done')
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash("Account is created for {}!".format(form.username.data), 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registration', form=form)


@app.route("/Login", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash('You have been logged in!', 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect('next_page') if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
@app.route("/Logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/Account", methods=['GET', 'POST'])
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account info has been updated!!", 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' +  current_user.image_file)
    return render_template('account.html', title="Account", form=form, image_file=image_file)


@app.route("/New Post", methods=['GET', 'POST'])
@app.route("/new post", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post has been Created!!', "success")
        return redirect(url_for('home'))
    return render_template('create_post.html', title="New Post", form=form, legend='New Post')


@app.route("/post/<int:post_id>")
@app.route("/Post/<int:post_id>")
def post(post_id):
    post1 = Post.query.get_or_404(post_id)
    return render_template('post.html', title='post', post=post1)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@app.route("/Post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    post1 = Post.query.get_or_404(post_id)
    if post1.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post1.title = form.title.data
        post1.content = form.content.data
        db.session.commit()
        flash('Your post has been Updated!!', 'success')
        return redirect(url_for('post', post_id=post1.id))
    elif request.method == 'GET':
        form.title.data = post1.title
        form.content.data = post1.content
    return render_template('create_post.html', title='Update post', post=post1, form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post2 = Post.query.get_or_404(post_id)
    if post2.author != current_user:
        abort(403)
    db.session.delete(post2)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
