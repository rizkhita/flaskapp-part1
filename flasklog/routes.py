from flask import request, redirect, render_template, flash, url_for
from flasklog import app,db,bcrypt
import secrets
import os
# from PIL import Image
from flasklog.models import User,Post
from flask_sqlalchemy import SQLAlchemy
from flasklog.forms import FormUpdateAkun,FormLogin, FormPendaftaran
from flask_login import login_user, current_user, logout_user, login_required
# app.config['SECRET KEY'] = '7f78660f28f95d3c3be8f2841f02e05c'
# csrf = CSRFProtect(app)
postingan = [
    {
        'penulis' : 'Rizkhita',
        'judul'   : 'Rizkhita si Anak Lontong',
        'konten'  : 'First content',
        'tgl_post': 'April 20, 2010',

    },
    {
        'penulis' : 'Deden',
        'judul'   : 'Rizkhita si Anak Pindang',
        'konten'  : 'Second content',
        'tgl_post': 'April 21, 2010',
    }
]



# type to browser in different pages (a the homepage)
@app.route("/")
@app.route("/beranda")
def beranda():
    # return "Beranda"
    return render_template('beranda.html', posts=postingan)

@app.route("/tentang")
def tentang():
    return render_template('tentang.html', title = 'tentang')

@app.route("/daftar", methods=['GET','POST'])
def daftar():
    if current_user.is_authenticated:
        return redirect(url_for('beranda'))
    form = FormPendaftaran()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email= form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Hello {}, your account has been created'.format(form.username.data))
        # return redirect(url_for('beranda'))
        return redirect(url_for('login'))
    return render_template('daftar.html', title='Register', form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('beranda'))
    form = FormLogin()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if  next_page else redirect(url_for('beranda'))
        else:
            flash('Login gagal, periksa kembali email anda.')

        """if form2.email.data == 'admin@blog.com' and form2.password.data == 'admin':
            flash('Login Berhasil!','success')
            return redirect(url_for('beranda'))
        else:
            flash('Login Gagal','danger')"""
    return render_template('login.html', title='login', form= form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('beranda'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    pict_fn = random_hex + f_ext
    pict_path = os.path.join(app.root_path, 'static/prof_pics', pict_fn)
    form_picture.save(pict_path)

    # output_size = (125,125)
    # i = Image.open(form_picture)
    # i.thumbnail(output_size)
    # i.save(pict_path)

    return pict_fn

@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = FormUpdateAkun()
    if form.validate_on_submit():

        if form.pict.data:
           picture_file = save_picture(form.pict.data)
           current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Akun sudah terupdate','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='prof_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)