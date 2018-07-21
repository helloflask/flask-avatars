# -*- coding: utf-8 -*-
""" 
    crop.app
    ~~~~
    Example application that demonstrate how to crop avatar.

    :author: Grey Li <withlihui@gmail.com>
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os

from flask import Flask, render_template, url_for, send_from_directory, request, session, redirect
from flask_avatars import Avatars

basedir = os.path.abspath(os.path.dirname(__name__))

app = Flask(__name__)
app.secret_key = 'dev'
app.config['AVATARS_SAVE_PATH'] = os.path.join(basedir, 'avatars')

avatars = Avatars(app)


# In reality, you can use Flask-WTF/WTForms to handle file upload and form validation.

# serve avatar image
@app.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        raw_filename = avatars.save_avatar(f)
        session['raw_filename'] = raw_filename  # you will need to store this filename in database in reality
        return redirect(url_for('crop'))
    return render_template('upload.html')


@app.route('/crop', methods=['GET', 'POST'])
def crop():
    if request.method == 'POST':
        x = request.form.get('x')
        y = request.form.get('y')
        w = request.form.get('w')
        h = request.form.get('h')
        filenames = avatars.crop_avatar(session['raw_filename'], x, y, w, h)
        url_s = url_for('get_avatar', filename=filenames[0])
        url_m = url_for('get_avatar', filename=filenames[1])
        url_l = url_for('get_avatar', filename=filenames[2])
        return render_template('done.html', url_s=url_s, url_m=url_m, url_l=url_l)
    return render_template('crop.html')
