# Flask-Avatars
All avatar generators in one place.

## Installation
```
$ pip install flask-avatars
```

## Initialization
The extension needs to be initialized in the usual way before it can be used:

```python
from flask_avatars import Avatars

app = Flask(__name__)
avatars = Avatars(app)
```

## Avatars

Flask-Avatars provide a `avatars` object in template context, you can use
it to get avatar URL.

### Gravatar

You can use `avatars.gravatar()` to get an avatar URL provided by
[Gravatar](https://en.gravatar.com/site/implement/images/), pass the email
hash:
```html
<img src="{{ avatars.gravatar(email_hash) }}">
```
You can get email hash like this:
```py
import hashlib

avatar_hash = hashlib.md5(my_email.lower().encode('utf-8')).hexdigest()
```

### Robohash

[Robohash](https://robohash.org) provide random robot avatar, you can use
`avatars.robohash()` to get the avatar URL, pass a random text:
```html
<img src="{{ avatars.robohash(some_text) }}">
```

### Avatars.io

[Avatars.io](https://avatars.io) let you use your social media's avatar
(Twitter, Facebook or Instagram), you can use `avatars.social_media()`
to get the avatar URL, pass your username on target social media:

```html
<img src="{{ avatars.social_media(username) }}">
```
Default to use Twitter, use `platform` to change it:
```html
<img src="{{ avatars.social_media(username, platform='facebook') }}">
```

### Default avatar

Flask-Avatars provide a default avatar with three size, use `avatars.default()`
to get the URL:
```html
<img src="{{ avatars.default() }}">
```
You can use `size` to change size (one of `s`, `m` and `l`), for example:
```html
<img src="{{ avatars.default(size='s') }}">
```

### Identicon generate
Flask-Avatars provide a `Identicon` class to generate [identicon](https://www.wikiwand.com/en/Identicon)
avatar, most of the code was based on [randomavatar](https://pypi.org/project/randomavatar/).
First, you need set configuration variable `AVATARS_SAVE_PATH` to tell
Flask-Avatars the path to save generated avatars. Generally speaking, we
will generate avavar when the user record was created, so the best place to
generate avatar is in user database model class:
```py
class User(db.Model):
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))

    def __init__():
        generate_avatar()

    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()
```

Then create a view to serve avatar image like this:
```py
from flask import send_form_directory, current_app

@app.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)
```

## Configuration

The configuration options available were listed below:

| Configuration | Default Value | Description |
| ------------- | ------------- | ----------- |
| AVATARS_GRAVATAR_DEFAULT | identicon | Gravatar default avatar type |
| AVATARS_SAVE_PATH | `None` | The path where avatar save |
| AVATARS_SIZE_TUPLE | `(30, 60, 150)` | The avatar size tuple in a format of `(small, medium, large)`, used when generate identicon avatar |
| AVATARS_IDENTICON_COLS | 7 | The cols of identicon avatar block |
| AVATARS_IDENTICON_ROWS | 7 | The ros of identicon avatar block |
| AVATARS_IDENTICON_BG | `None` | The back ground color of identicaon avatar, pass RGB tuple (for example `(125, 125, 125)`). Default (`None`) to use random color |


## TODO
- [ ] Fix English grammar error at everywhere :(
- [ ] Documentation
- [ ] Tests
- [ ] Example applications

## ChangeLog

### 0.1.0

Release date: 2018/6/19

Initialize release.

## License

This project is licensed under the MIT License (see the
`LICENSE` file for details).
