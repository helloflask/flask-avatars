# -*- coding: utf-8 -*-
import os
import urllib

from flask import send_from_directory, current_app, Blueprint, url_for, Markup
from randomavatar.randomavatar import Avatar


class _Avatars(object):

    @staticmethod
    def gravatar(hash, size=100, rating='g', default='identicon', include_extension=False, force_default=False):
        """
        You can get hash like this::
            import hashlib

            avatar_hash = hashlib.md5(email.lower()).hexdigest()
        :param hash
        :param size
        :param rating
        :param default

        """
        if include_extension:
            hash += '.jpg'

        default = current_app.config['AVATARS_GRAVATAR_DEFAULT'] or default
        query_string = urllib.urlencode({'s': int(size), 'r': rating, 'd': default})

        if force_default:
            query_string += '&q=y'
        return 'https://gravatar.com/avatar/' + hash + '?' + query_string

    @staticmethod
    def robohash(text, size=200):
        return 'https://robohash.org/{text}?size={size}x{size}'.format(text=text, size=size)

    @staticmethod
    def social_media(username, platform='twitter', size='medium'):
        """
        facebook, instagram, twitter, gravatar
        """
        return 'https://avatars.io/{platform}/{username}/{size}'.format(platform=platform, username=username, size=size)

    @staticmethod
    def default(size='m'):
        return url_for('static', filename='default/{size}.jpg'.format(size=size))


    @staticmethod
    def load_jcrop():

        preview_size = 180
        crop_size = 500
        return Markup('''
        
<style>
#preview-pane .preview-container {
  width: %dpx;
  height: %dpx;
  overflow: hidden;
}

#crop-box {
  max-width: %dpx;
  display: block;
}
        </style>
        ''' % (preview_size, preview_size, crop_size))

    @staticmethod
    def crop_box(url):
        if url is None:
            url = '/avatar/%s'
        return '<img src="%s" id="cropbox">' % url

    @staticmethod
    def preview_pane(url):
        return '''
        <div id="preview-pane">
        <div class="preview-container">
          <img src="%s"
               class="jcrop-preview" alt="Preview"/>
        </div>
      </div>''' % url




class Identicon(object):
    def __init__(self, rows=10, cols=10):
        self.rows = rows
        self.cols = cols

    def generate(self, text, path, id, size=100):
        avatar = Avatar(rows=self.rows, columns=self.cols)
        image_byte_array = avatar.get_image(
            string=str(text),
            width=int(size),
            height=int(size),
            pad=int(size * 0.05))
        avatar.save(image_byte_array,
                    save_location=os.path.join(path, '%s_%d.png' % (id, size)))



class Avatars(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['avatars'] = _Avatars
        app.context_processor(self.context_processor)

        blueprint = Blueprint('avatars', __name__)
        app.register_blueprint(blueprint)

        # settings
        app.config.setdefault('AVATARS_GRAVATAR_DEFAULT', 'identicon')
        app.config.setdefault('AVATARS_UPLOAD_PATH', None)

        @blueprint.route('/avatar/<int:id>/<int:size>')
        def avatar(id, size):
            path = current_app.config['AVATARS_UPLOAD_PATH']
            filename = '%s_%d.png' % (id, size)
            return send_from_directory(path, filename)


    @staticmethod
    def context_processor():
        return {
            'avatars': current_app.extensions['avatars']
        }
