---
layout: post
title: Django Session And Auth Middleware
tags:
datetime: 2016-9-27 11:30
---

{{ page.title }}
================
前言:<br/>
    一个Django App(app2)需要使用另外一个Django App(app1)的session和用户系统进行登录认证.
app1使用Django自带的SessionMiddle和AuthenticationMiddle,下面我结合Django源码和需求,
分析从带session_key的请求,获得用户的过程.

app1的settings如下:
{% highlight python %}
SECRET_KEY = '*(&^&&JSIIJIFEJIFJ'
INSTALL_APPS = (
    'django.contrib.sessions'
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_FILE_PATH
    }
}
# Session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
{% endhighlight %}

从请求中获取用户的过程:<br/>
SessionMiddleware从request取得session_key,
然后根据session_key在数据库表Django_session中加载session数据(包含_auth_user_id),把sesion data设值到request<br/>
AuthenticationMiddleware从上一步的session中取得_auth_user_id,根据这个id从数据库用户表加载user,把user设值到request.<br/>
先看看SessionStore load session的过程:<br/>

{% highlight python %}
# django.contrib.sessions.backends.cached_db
Class SessionStore(DBStore):
    def load(self):
        try:
            data = self._cache.get(self.cache_key)
        except Exception:
            # Some backends (e.g. memcache) raise an exception on invalid
            # cache keys. If this happens, reset the session. See #17810.
            data = None
        if data is None:
            # Duplicate DBStore.load, because we need to keep track
            # of the expiry date to set it properly in the cache.
            try:
                s = self.model.objects.get(
                    session_key=self.session_key,
                    expire_date__gt=timezone.now()
                )
                data = self.decode(s.session_data)
                self._cache.set(self.cache_key, data, self.get_expiry_age(expiry=s.expire_date))
            except (self.model.DoesNotExist, SuspiciousOperation) as e:
                if isinstance(e, SuspiciousOperation):
                    logger = logging.getLogger('django.security.%s' % e.__class__.__name__)
                    logger.warning(force_text(e))
                self._session_key = None
                data = {}
        return data
{% endhighlight %}
{% highlight python %}
# django.contrib.sessions.backends.db
Class SessionStore(SessionBase):
    def load(self):
        try:
            s = self.model.objects.get(
                session_key=self.session_key,
                expire_date__gt=timezone.now()
            )
            return self.decode(s.session_data)
        except (self.model.DoesNotExist, SuspiciousOperation) as e:
            if isinstance(e, SuspiciousOperation):
                logger = logging.getLogger('django.security.%s' % e.__class__.__name__)
                logger.warning(force_text(e))
            self._session_key = None
            return {}
{% endhighlight %}
<p>
从load函数可以看出,cache_db.py的SessionStore先从caches里边根据cache_key找session data,而且当key不存在于cached backend时，
要求返回None，比如memcached backend返回空字典，导致无法从数据库获取session 信息，所以要把session cached backend禁用掉，
或者换一个返回None的backend，或者替换这个cacehd backend。
</p>
<p>
如果找不到才会从数据库里找(通过ORM),而db.py的SessionStore是直接从数据库里边加载session data的<br/>
另外{% highlight python %}self.decode(s.session_data){% endhighlight %}很重要,这里是
用HMAC的签名加密的方式验证调用者得身份,如果身份不对的话会抛出SuspiciousOperation的错误,导致加载失败,返回空字典.<br/>
</p>
追踪下去得到验证代码如下:

{% highlight python %}
# django.utils.crypto
def salted_hmac(key_salt, value, secret=None):
    """
    Returns the HMAC-SHA1 of 'value', using a key generated from key_salt and a
    secret (which defaults to settings.SECRET_KEY).
    A different key_salt should be passed in for every application of HMAC.
    """
    if secret is None:
        secret = settings.SECRET_KEY
    key_salt = force_bytes(key_salt)
    secret = force_bytes(secret)
    # We need to generate a derived key from our base key.  We can do this by
    # passing the key_salt and our base key through a pseudo-random function and
    # SHA1 works nicely.
    key = hashlib.sha1(key_salt + secret).digest()
    # If len(key_salt + secret) > sha_constructor().block_size, the above
    # line is redundant and could be replaced by key = key_salt + secret, since
    # the hmac module does the same thing for keys longer than the block size.
    # However, we need to ensure that we *always* do this.
    return hmac.new(key, msg=force_bytes(value), digestmod=hashlib.sha1)
{% endhighlight %}

上面代码可以看到,hmac使用一个key对value进行加密,而这个key的一部分就是Django App的SECRET_KEY,
关于SECRET_KEY的用途参考: <a href="https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-SECRET_KEY">Django-setting-SECRET_KEY</a>

AuthenticationMiddle中也有一个HMAC校验的过程:

{% highlight python %}
# django.contrib.auth.__init__
def get_user(request):
    """
    Returns the user model instance associated with the given request session.
    If no user is retrieved an instance of `AnonymousUser` is returned.
    """
    from .models import AnonymousUser
    user = None
    try:
        user_id = _get_user_session_key(request)
        backend_path = request.session[BACKEND_SESSION_KEY]
    except KeyError:
        pass
    else:
        if backend_path in settings.AUTHENTICATION_BACKENDS:
            backend = load_backend(backend_path)
            user = backend.get_user(user_id)
            # Verify the session
            if hasattr(user, 'get_session_auth_hash'):
                session_hash = request.session.get(HASH_SESSION_KEY)
                session_hash_verified = session_hash and constant_time_compare(
                    session_hash,
                    user.get_session_auth_hash()
                )
                if not session_hash_verified:
                    request.session.flush()
                    user = None
    return user or AnonymousUser()
{% endhighlight %}

所以如果要实现App2使用App1的session系统,可以的做法是:<br/>
1. 数据库设置一致<br/>
2. SECRET_KEY和app1一致<br/>
3. 如果cached backend当key不存在时不是返回None的话（比如memcached返回空字典{})，那app2不能使用带缓存的SessionStore backend.<br/>
<P> 
或者改写SessionMiddleware和AuthenticationMiddle,把HAMC校验部分去掉.
</P>
