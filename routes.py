# from forms import RegistrationForm, LoginForm
from flask import redirect, url_for, render_template, flash
from project import app

posts = [
    {
        'author': 'ram',
        'title': 'Life',
        'content': 'First_post',
        'date_posted': 'April 20, 2023'

    },
    {
        'author': 'sef',
        'title': 'joy',
        'content': 'First_post',
        'date_posted': 'April 25, 2023'

    }
]


@app.route("/")
def home():
    return render_template("index.html", posts=posts)


@app.route("/<name>")
def main(name):
    return render_template('about.html', content=name, title='About')


@app.route("/Register", methods=['GET', 'POST'])
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        print('done')
        flash("Account is created for {}!".format(form.username.data), 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Registration',form=form)


@app.route("/Login", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
