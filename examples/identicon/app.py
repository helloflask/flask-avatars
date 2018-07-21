# -*- coding: utf-8 -*-
""" 
    identicon.app
    ~~~~~~~~~~~~~
    Example application that demonstrate how to generate identicon.

    :author: Grey Li <withlihui@gmail.com>
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
import uuid

from flask import Flask, render_template, url_for, send_from_directory
from flask_avatars import Avatars, Identicon

basedir = os.path.abspath(os.path.dirname(__name__))

app = Flask(__name__)
app.config['AVATARS_SAVE_PATH'] = os.path.join(basedir, 'avatars')

avatars = Avatars(app)


# serve avatar image
@app.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


@app.route('/')
def index():
    avatar = Identicon()
    random_text = uuid.uuid4().hex
    filenames = avatar.generate(text=random_text)
    url_s = url_for('get_avatar', filename=filenames[0])
    url_m = url_for('get_avatar', filename=filenames[1])
    url_l = url_for('get_avatar', filename=filenames[2])
    return render_template('index.html', url_s=url_s, url_m=url_m, url_l=url_l)
