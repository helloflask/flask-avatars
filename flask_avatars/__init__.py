# -*- coding: utf-8 -*-
"""
    flask_avatars
    ~~~~~~~~~~~~~

    :author: Grey Li <withlihui@gmail.com>
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from uuid import uuid4

import PIL
from PIL import Image
from flask import current_app, Blueprint, url_for, Markup
from .identicon import Identicon  # noqa


class _Avatars(object):

    @staticmethod
    def gravatar(hash, size=100, rating='g', default='identicon', include_extension=False, force_default=False):
        """Pass email hash, return Gravatar URL. You can get email hash like this::

            import hashlib
            avatar_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()

        Visit https://en.gravatar.com/site/implement/images/ for more information.

        :param hash: The email hash used to generate avatar URL.
        :param size: The size of the avatar, default to 100 pixel.
        :param rating: The rating of the avatar, default to ``g``
        :param default: The type of default avatar, default to ``identicon``.
        :param include_extension: Append a '.jpg' extension at the end of URL, default to ``False``.
        :param force_default: Force to use default avatar, default to ``False``.
        """
        if include_extension:
            hash += '.jpg'

        default = default or current_app.config['AVATARS_GRAVATAR_DEFAULT']
        query_string = urlencode({'s': int(size), 'r': rating, 'd': default})

        if force_default:
            query_string += '&q=y'
        return 'https://gravatar.com/avatar/' + hash + '?' + query_string

    @staticmethod
    def robohash(text, size=200):
        """Pass text, return Robohash-style avatar (robot).
        Visit https://robohash.org/ for more information.

        :param text: The text used to generate avatar.
        :param size: The size of the avatar, default to 200 pixel.
        """
        return 'https://robohash.org/{text}?size={size}x{size}'.format(text=text, size=size)

    @staticmethod
    def social_media(username, platform='twitter', size='medium'):
        """Return avatar URL at social media.
        Visit https://avatars.io for more information.

        :param username: The username of the social media.
        :param platform: One of facebook, instagram, twitter, gravatar.
        :param size: The size of avatar, one of small, medium and large.
        """
        return 'https://avatars.io/{platform}/{username}/{size}'.format(
            platform=platform, username=username, size=size)

    @staticmethod
    def default(size='m'):
        """Return built-in default avatar.

        :param size: The size of avatar, one of s, m, l.
        :return: Default avatar URL
        """
        return url_for('avatars.static', filename='default/default_{size}.jpg'.format(size=size))

    @staticmethod
    def jcrop_css(css_url=None):
        """Load jcrop css file.

        :param css_url: The custom CSS URL.
        """
        if css_url is None:
            if current_app.config['AVATARS_SERVE_LOCAL']:
                css_url = url_for('avatars.static', filename='jcrop/css/jquery.Jcrop.min.css')
            else:
                css_url = 'https://cdn.jsdelivr.net/npm/jcrop-0.9.12@0.9.12/css/jquery.Jcrop.min.css'
        return Markup('<link rel="stylesheet" href="%s">' % css_url)

    @staticmethod
    def jcrop_js(js_url=None, with_jquery=True):
        """Load jcrop Javascript file.

        :param js_url: The custom JavaScript URL.
        :param with_jquery: Include jQuery or not, default to ``True``.
        """
        serve_local = current_app.config['AVATARS_SERVE_LOCAL']

        if js_url is None:
            if serve_local:
                js_url = url_for('avatars.static', filename='jcrop/js/jquery.Jcrop.min.js')
            else:
                js_url = 'https://cdn.jsdelivr.net/npm/jcrop-0.9.12@0.9.12/js/jquery.Jcrop.min.js'

        if with_jquery:
            if serve_local:
                jquery = '<script src="%s"></script>' % url_for('avatars.static', filename='jcrop/js/jquery.min.js')
            else:
                jquery = '<script src="https://cdn.jsdelivr.net/npm/jcrop-0.9.12@0.9.12/js/jquery.min.js"></script>'
        else:
            jquery = ''
        return Markup('''%s\n<script src="%s"></script>
        ''' % (jquery, js_url))

    @staticmethod
    def crop_box(endpoint=None, filename=None):
        """Create a crop box.

        :param endpoint: The endpoint of view function that serve avatar image file.
        :param filename: The filename of the image that need to be crop.
        """
        crop_size = current_app.config['AVATARS_CROP_BASE_WIDTH']

        if endpoint is None or filename is None:
            url = url_for('avatars.static', filename='default/default_l.jpg')
        else:
            url = url_for(endpoint, filename=filename)
        return Markup('<img src="%s" id="crop-box" style="max-width: %dpx; display: block;">' % (url, crop_size))

    @staticmethod
    def preview_box(endpoint=None, filename=None):
        """Create a preview box.

        :param endpoint: The endpoint of view function that serve avatar image file.
        :param filename: The filename of the image that need to be crop.
        """
        preview_size = current_app.config['AVATARS_CROP_PREVIEW_SIZE'] or current_app.config['AVATARS_SIZE_TUPLE'][2]

        if endpoint is None or filename is None:
            url = url_for('avatars.static', filename='default/default_l.jpg')
        else:
            url = url_for(endpoint, filename=filename)
        return Markup('''
        <div id="preview-box">
        <div class="preview-box" style="width: %dpx; height: %dpx; overflow: hidden;">
          <img src="%s" class="jcrop-preview" alt="Preview"/>
        </div>
      </div>''' % (preview_size, preview_size, url))

    @staticmethod
    def init_jcrop(min_size=None):
        """Initialize jcrop.

        :param min_size: The minimal size of crop area.
        """
        init_x = current_app.config['AVATARS_CROP_INIT_POS'][0]
        init_y = current_app.config['AVATARS_CROP_INIT_POS'][1]
        init_size = current_app.config['AVATARS_CROP_INIT_SIZE'] or current_app.config['AVATARS_SIZE_TUPLE'][2]

        if current_app.config['AVATARS_CROP_MIN_SIZE']:
            min_size = min_size or current_app.config['AVATARS_SIZE_TUPLE'][2]
            min_size_js = 'jcrop_api.setOptions({minSize: [%d, %d]});' % (min_size, min_size)
        else:
            min_size_js = ''
        return Markup('''
<script type="text/javascript">
    jQuery(function ($) {
      // Create variables (in this scope) to hold the API and image size
      var jcrop_api,
          boundx,
          boundy,

          // Grab some information about the preview pane
          $preview = $('#preview-box'),
          $pcnt = $('#preview-box .preview-box'),
          $pimg = $('#preview-box .preview-box img'),

          xsize = $pcnt.width(),
          ysize = $pcnt.height();

      $('#crop-box').Jcrop({
        onChange: updatePreview,
        onSelect: updateCoords,
        setSelect: [%s, %s, %s, %s],
        aspectRatio: 1
      }, function () {
        // Use the API to get the real image size
        var bounds = this.getBounds();
        boundx = bounds[0];
        boundy = bounds[1];
        // Store the API in the jcrop_api variable
        jcrop_api = this;
        %s
        jcrop_api.focus();
        // Move the preview into the jcrop container for css positioning
        $preview.appendTo(jcrop_api.ui.holder);
      });

      function updatePreview(c) {
        if (parseInt(c.w) > 0) {
          var rx = xsize / c.w;
          var ry = ysize / c.h;
          $pimg.css({
            width: Math.round(rx * boundx) + 'px',
            height: Math.round(ry * boundy) + 'px',
            marginLeft: '-' + Math.round(rx * c.x) + 'px',
            marginTop: '-' + Math.round(ry * c.y) + 'px'
          });
        }
      }
    });

    function updateCoords(c) {
      $('#x').val(c.x);
      $('#y').val(c.y);
      $('#w').val(c.w);
      $('#h').val(c.h);
    }
  </script>
            ''' % (init_x, init_y, init_size, init_size, min_size_js))


class Avatars(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['avatars'] = _Avatars
        app.context_processor(self.context_processor)

        blueprint = Blueprint('avatars', __name__,
                              static_folder='static',
                              static_url_path='/avatars' + app.static_url_path)
        app.register_blueprint(blueprint)

        self.root_path = blueprint.root_path

        # TODO: custom file extension support
        # settings
        app.config.setdefault('AVATARS_GRAVATAR_DEFAULT', 'identicon')

        app.config.setdefault('AVATARS_SERVE_LOCAL', False)

        app.config.setdefault('AVATARS_SAVE_PATH', None)
        app.config.setdefault('AVATARS_SIZE_TUPLE', (30, 60, 150))
        # Identicon
        app.config.setdefault('AVATARS_IDENTICON_COLS', 7)
        app.config.setdefault('AVATARS_IDENTICON_ROWS', 7)
        app.config.setdefault('AVATARS_IDENTICON_BG', None)
        # Jcrop
        app.config.setdefault('AVATARS_CROP_BASE_WIDTH', 500)
        app.config.setdefault('AVATARS_CROP_INIT_POS', (0, 0))
        app.config.setdefault('AVATARS_CROP_INIT_SIZE', None)
        app.config.setdefault('AVATARS_CROP_PREVIEW_SIZE', None)
        app.config.setdefault('AVATARS_CROP_MIN_SIZE', None)

        # @blueprint.route('/%s/<path:filename>/<size>' % app.config['AVATARS_STATIC_PREFIX'])
        # def static(filename_m):
        #     path = current_app.config['AVATARS_SAVE_PATH']
        #     filename = '%s_%s.png' % (filename, size)
        #     return send_from_directory(path, filename)

    @staticmethod
    def context_processor():
        return {
            'avatars': current_app.extensions['avatars']
        }

    def resize_avatar(self, img, base_width):
        """Resize an avatar.

        :param img: The image that needs to be resize.
        :param base_width: The width of output image.
        """
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        return img

    def save_avatar(self, image):
        """Save an avatar as raw image, return new filename.

        :param image: The image that needs to be saved.
        """
        path = current_app.config['AVATARS_SAVE_PATH']
        filename = uuid4().hex + '_raw.png'
        image.save(os.path.join(path, filename))
        return filename

    def crop_avatar(self, filename, x, y, w, h):
        """Crop avatar with given size, return a list of file name: [filename_s, filename_m, filename_l].

        :param filename: The raw image's filename.
        :param x: The x-pos to start crop.
        :param y: The y-pos to start crop.
        :param w: The crop width.
        :param h: The crop height.
        """
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)

        sizes = current_app.config['AVATARS_SIZE_TUPLE']

        if not filename:
            path = os.path.join(self.root_path, 'static/default/default_l.jpg')
        else:
            path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename)

        print(path)

        raw_img = Image.open(path)

        base_width = current_app.config['AVATARS_CROP_BASE_WIDTH']

        if raw_img.size[0] >= base_width:
            raw_img = self.resize_avatar(raw_img, base_width=base_width)

        cropped_img = raw_img.crop((x, y, x + w, y + h))

        filename = uuid4().hex

        avatar_s = self.resize_avatar(cropped_img, base_width=sizes[0])
        avatar_m = self.resize_avatar(cropped_img, base_width=sizes[1])
        avatar_l = self.resize_avatar(cropped_img, base_width=sizes[2])

        filename_s = filename + '_s.png'
        filename_m = filename + '_m.png'
        filename_l = filename + '_l.png'

        path_s = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename_s)
        path_m = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename_m)
        path_l = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename_l)

        avatar_s.save(path_s, optimize=True, quality=85)
        avatar_m.save(path_m, optimize=True, quality=85)
        avatar_l.save(path_l, optimize=True, quality=85)

        return [filename_s, filename_m, filename_l]

    @staticmethod
    def gravatar(*args, **kwargs):
        return _Avatars.gravatar(*args, **kwargs)

    @staticmethod
    def robohash(*args, **kwargs):
        return _Avatars.robohash(*args, **kwargs)

    @staticmethod
    def social_media(*args, **kwargs):
        return _Avatars.social_media(*args, **kwargs)

    @staticmethod
    def default(*args, **kwargs):
        return _Avatars.default(*args, **kwargs)
