# -*- coding: utf-8 -*-
""" 
    basic.app
    ~~~~~~~~~~
    Example application that demonstrate basic use.

    :author: Grey Li <withlihui@gmail.com>
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import hashlib

from flask import Flask, render_template
from flask_avatars import Avatars

app = Flask(__name__)
avatars = Avatars(app)


@app.route('/')
def index():
    email_hash = hashlib.md5('test@helloflask.com'.lower().encode('utf-8')).hexdigest()
    return render_template('index.html', email_hash=email_hash)

