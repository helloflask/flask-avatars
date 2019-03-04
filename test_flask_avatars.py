# -*- coding: utf-8 -*-
"""
    test_flask_avatars
    ~~~~~~~~~~~~~~~~~~

    :author: Grey Li <withlihui@gmail.com>
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import hashlib
import os
import unittest

from PIL import Image
from flask import Flask, render_template_string, current_app

from flask_avatars import Avatars, _Avatars, Identicon

basedir = os.path.abspath(os.path.dirname(__file__))


class AvatarsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)

        self.app.testing = True
        self.app.secret_key = 'for test'

        self.email_hash = hashlib.md5('test@helloflask.com'.lower().encode('utf-8')).hexdigest()

        avatars = Avatars(self.app)  # noqa

        self.real_avatars = avatars

        self.avatars = _Avatars

        self.context = self.app.test_request_context()
        self.context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.context.pop()

    def test_extension_init(self):
        self.assertIn('avatars', current_app.extensions)

    def test_gravatar(self):
        avatar_url = self.avatars.gravatar(self.email_hash)
        self.assertIn('https://gravatar.com/avatar/%s' % self.email_hash, avatar_url)
        self.assertIn('s=100', avatar_url)
        self.assertIn('r=g', avatar_url)
        self.assertIn('d=identicon', avatar_url)

        avatar_url = self.avatars.gravatar(self.email_hash, size=200, rating='x', default='monsterid',
                                           include_extension=True)
        self.assertIn('https://gravatar.com/avatar/%s' % self.email_hash, avatar_url)
        self.assertIn('s=200', avatar_url)
        self.assertIn('r=x', avatar_url)
        self.assertIn('d=monsterid', avatar_url)

    def test_robohash(self):
        avatar_url = self.avatars.robohash(self.email_hash)
        self.assertEqual(avatar_url, 'https://robohash.org/%s?size=200x200' % self.email_hash)

        avatar_url = self.avatars.robohash(self.email_hash, size=100)
        self.assertEqual(avatar_url, 'https://robohash.org/%s?size=100x100' % self.email_hash)

    def test_social_media(self):
        avatar_url = self.avatars.social_media('greyli')
        self.assertEqual(avatar_url, 'https://avatars.io/twitter/greyli/medium')

        avatar_url = self.avatars.social_media('greyli', platform='facebook', size='small')
        self.assertEqual(avatar_url, 'https://avatars.io/facebook/greyli/small')

    def test_default_avatar(self):
        avatar_url = self.avatars.default()
        self.assertEqual(avatar_url, '/avatars/static/default/default_m.jpg')

        avatar_url = self.avatars.default(size='l')
        self.assertEqual(avatar_url, '/avatars/static/default/default_l.jpg')

        avatar_url = self.avatars.default(size='s')
        self.assertEqual(avatar_url, '/avatars/static/default/default_s.jpg')

        response = self.client.get(avatar_url)
        self.assertEqual(response.status_code, 200)

    def test_load_jcrop(self):
        rv = self.avatars.jcrop_css()
        self.assertIn('<link rel="stylesheet" href="https://cdn.jsdelivr.net', rv)

        rv = self.avatars.jcrop_js()
        self.assertIn('<script src="https://cdn.jsdelivr.net', rv)
        self.assertIn('jquery.min.js', rv)

        rv = self.avatars.jcrop_js(with_jquery=False)
        self.assertIn('jquery.Jcrop.min.js', rv)
        self.assertNotIn('jquery.min.js', rv)

    def test_local_resources(self):
        current_app.config['AVATARS_SERVE_LOCAL'] = True

        response = self.client.get('/avatars/static/jcrop/js/jquery.Jcrop.min.js')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/avatars/static/jcrop/css/jquery.Jcrop.min.css')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/avatars/static/jcrop/js/jquery.min.js')
        self.assertEqual(response.status_code, 200)

        rv = self.avatars.jcrop_css()
        self.assertIn('/avatars/static/jcrop/css/jquery.Jcrop.min.css', rv)
        self.assertNotIn('<link rel="stylesheet" href="https://cdn.jsdelivr.net', rv)

        rv = self.avatars.jcrop_js()
        self.assertIn('/avatars/static/jcrop/js/jquery.Jcrop.min.js', rv)
        self.assertIn('/avatars/static/jcrop/js/jquery.min.js', rv)
        self.assertNotIn('<script src="https://cdn.jsdelivr.net', rv)

        rv = self.avatars.jcrop_js(with_jquery=False)
        self.assertIn('/avatars/static/jcrop/js/jquery.Jcrop.min.js', rv)
        self.assertNotIn('jquery.min.js', rv)

    def test_init_jcrop(self):
        rv = self.avatars.init_jcrop()
        self.assertIn('var jcrop_api,', rv)

    def test_crop_box(self):
        rv = self.avatars.crop_box()
        self.assertIn('id="crop-box"', rv)

    def test_preview_box(self):
        rv = self.avatars.preview_box()
        self.assertIn('<div id="preview-box">', rv)

    def test_render_template(self):
        rv = render_template_string('''{{ avatars.jcrop_css() }}''')
        self.assertIn('<link rel="stylesheet" href="https://cdn.jsdelivr.net', rv)

        rv = render_template_string('''{{ avatars.jcrop_js() }}''')
        self.assertIn('<script src="https://cdn.jsdelivr.net', rv)

        rv = render_template_string('''{{ avatars.init_jcrop() }}''')
        self.assertIn('var jcrop_api,', rv)

        rv = render_template_string('''{{ avatars.crop_box() }}''')
        self.assertIn('id="crop-box"', rv)

        rv = render_template_string('''{{ avatars.preview_box() }}''')
        self.assertIn('<div id="preview-box">', rv)

    def test_resize_avatar(self):
        current_app.config['AVATARS_SAVE_PATH'] = basedir
        img = Image.new(mode='RGB', size=(800, 800), color=(125, 125, 125))
        resized = self.real_avatars.resize_avatar(img, 300)
        self.assertEqual(resized.size[0], 300)

    def test_save_avatar(self):
        current_app.config['AVATARS_SAVE_PATH'] = basedir
        img = Image.new(mode='RGB', size=(800, 800), color=(125, 125, 125))
        filename = self.real_avatars.save_avatar(img)
        self.assertIn('_raw.png', filename)
        self.assertTrue(os.path.exists(os.path.join(basedir, filename)))
        os.remove(os.path.join(basedir, filename))

    def test_crop_avatar(self):
        current_app.config['AVATARS_SAVE_PATH'] = basedir
        img = Image.new(mode='RGB', size=(1000, 1000), color=(125, 125, 125))
        img.save(os.path.join(basedir, 'test.png'))
        filenames = self.real_avatars.crop_avatar('test.png', x=1, y=1, w=30, h=30)
        self.assertIn('_s.png', filenames[0])
        self.assertIn('_m.png', filenames[1])
        self.assertIn('_l.png', filenames[2])

        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[0])))
        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[1])))
        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[2])))

        file_s = Image.open(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[0]))
        self.assertEqual(file_s.size[0], current_app.config['AVATARS_SIZE_TUPLE'][0])
        file_s.close()

        for filename in filenames:
            os.remove(os.path.join(basedir, filename))

        os.remove(os.path.join(basedir, 'test.png'))

    def test_crop_default_avatar(self):
        current_app.config['AVATARS_SAVE_PATH'] = basedir
        filenames = self.real_avatars.crop_avatar(None, x=1, y=1, w=100, h=100)
        self.assertIn('_s.png', filenames[0])
        self.assertIn('_m.png', filenames[1])
        self.assertIn('_l.png', filenames[2])

        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[0])))
        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[1])))
        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[2])))

        file_s = Image.open(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[0]))
        self.assertEqual(file_s.size[0], current_app.config['AVATARS_SIZE_TUPLE'][0])
        file_s.close()

        for filename in filenames:
            os.remove(os.path.join(basedir, filename))

    def test_gravatar_mirror(self):
        mirror = self.real_avatars.gravatar(self.email_hash)
        real = self.avatars.gravatar(self.email_hash)
        self.assertEqual(mirror, real)

    def test_robohash_mirror(self):
        mirror = self.real_avatars.robohash(self.email_hash)
        real = self.avatars.robohash(self.email_hash)
        self.assertEqual(mirror, real)

    def test_social_media_mirror(self):
        mirror = self.real_avatars.social_media('grey')
        real = self.avatars.social_media('grey')
        self.assertEqual(mirror, real)

    def test_default_avatar_mirror(self):
        mirror = self.real_avatars.default()
        real = self.avatars.default()
        self.assertEqual(mirror, real)

    def test_identicon(self):
        current_app.config['AVATARS_SAVE_PATH'] = basedir

        avatar = Identicon()
        filenames = avatar.generate(text='grey')
        self.assertEqual(filenames[0], 'grey_s.png')
        self.assertEqual(filenames[1], 'grey_m.png')
        self.assertEqual(filenames[2], 'grey_l.png')

        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[0])))
        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[1])))
        self.assertTrue(os.path.exists(os.path.join(current_app.config['AVATARS_SAVE_PATH'], filenames[2])))

        # comment out these two lines to check the generated image, then delete them manually.
        for filename in filenames:
            os.remove(os.path.join(basedir, filename))
