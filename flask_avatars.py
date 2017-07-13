# -*- coding: utf-8 -*-
import urllib

from flask import send_from_directory
from randomavatar import randomavatar

class Avatars(object):
    pass


class Identicon(object):

	def __init__(self, rows=10, cols=10):
		self.rows = rows
		self.cols = cols

	def save(self):




def gravatar(hash, size=100, rating='g', default='identicon'):
	"""
	You can get hash like this:
	import hashlib

	avatar_hash = hashlib.md5(email.lower()).hexdigest()
	:param hash
	:param size
	:param rating
	:param default

	"""
	default = current_app.config['AVATARS_GRAVATAR_DEFAULT'] or default
	query_string = urllib.urlencode({'s': int(size), 'r': rating, 'd': default})
	return 'https://gravatar.com/avatar/' + hash + '?' + query_string


def robohash(text, size=200):
    return 'https://robohash.org/{text}?size={size}x{size}'.format(text=text, size=size)


def identicon():
    pass


def social_media(username, paltform='twitter', size='medium'):
	"""
	facebook, instagram, twitter, gravatar
	"""
    return 'https://avatars.io/{platform}/{username}/{size}'.format(platform=platform, username=username, size=size)


def default(size='m'):
    return url_for('static', filename='default_{size}.jpg'.format(size=size))


def custom():
    pass


def crop():
	pass