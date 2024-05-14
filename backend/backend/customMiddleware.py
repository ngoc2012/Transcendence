from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import jwt, pytz, uuid
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser
from django.urls import resolve, Resolver404


User = get_user_model()

class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            resolve(request.path_info)
        except Resolver404:
            return HttpResponseRedirect('/')

        if '/callback/' in request.path:
            return self.process_callback(request)

        if request.headers.get('X-Internal-Request') == 'true' or request.path in self.get_unauthenticated_paths() or '/game/close/' in request.path or '/admin/' in request.path or '/pong/' in request.path or '/media/' in request.path:
            self.user = None
            return None

        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return self.return_lobby()

        jti = None

        try:
            payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            if not jti or cache.get(jti):
                return self.return_lobby()

            user = self.get_user(payload.get('user_id'))
            if not user:
                return self.return_lobby()

            request.user = user
            return None

        except jwt.ExpiredSignatureError:
            if jti:
                cache.set(jti, "revoked", timeout=None)
            return self.handle_refresh_token(request)
        except jwt.InvalidTokenError:
            return self.return_lobby()

    def process_exception(self, request, exception):
        if isinstance(exception, ObjectDoesNotExist):
            return self.return_lobby()

    def get_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return self.return_lobby()
        if isinstance(user, AnonymousUser):
            return self.return_lobby()
        return user

    def handle_refresh_token(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return self.return_lobby()

        jti = None

        try:
            payload = jwt.decode(refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            if not jti or cache.get(jti):
                return self.return_lobby()

            user = self.get_user(payload.get('user_id'))

            if user:
                new_access_token, new_refresh_token = self.generate_jwt_tokens(payload.get('user_id'))
                request.new_access_token = new_access_token
                request.new_refresh_token = new_refresh_token
                request.user = user
                if jti:
                    cache.set(jti, "revoked", timeout=None)
                return None
            else:
                return self.return_lobby()
        except jwt.ExpiredSignatureError:
            if jti:
                cache.set(jti, "revoked", timeout=None)
            return self.return_lobby()
        except jwt.InvalidTokenError:
           return self.return_lobby()

    def generate_jwt_tokens(self, user_id):
        access_token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.now(pytz.utc) + timedelta(minutes=65),
            'jti': str(uuid.uuid4())
        }, settings.JWT_SECRET_KEY, algorithm='HS256')

        refresh_token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.now(pytz.utc) + timedelta(minutes=120),
            'jti': str(uuid.uuid4())
        }, settings.JWT_REFRESH_SECRET_KEY, algorithm='HS256')

        return access_token, refresh_token

    def get_unauthenticated_paths(self):
        return [
            '/logout/',
            '/',
            '/favicon.ico',
            '/get-csrf/',
            'pages/signup/',
            '/pages/signup/',
            '/new_player/',
            '/np/',
            'pages/login/',
            '/pages/login/',
            '/login',
            '/login/',
            '/log_in/',
            '/lg/',
            '/lobby/',
            '/lobby',
            '/admin/',
            '/admin/login/',
            '/game/new',
            '/game/update',
            '/game/need_update',
            '/game/join',
            '/game/ng',
            '/game/upd',
            '/game/need_update',
            '/game/jn',
            '/validate-session/',
            '/auth_view/',
            '/twofa/',
            '/qrcode_2fa/',
            '/code_2fa/',
            '/mail_2fa/',
            '/verify_qrcode/',
            '/verify/',
            '/login42/',
            '/game/tournament/local/result/',
            '/game/tournament/local/join/setup/',
        ]

    def process_callback(self, request):
        state = request.GET.get('state', None)
        if state and 'oauth_state_login'in request.session and state == request.session['oauth_state_login']:
            return None
        else:
            return  self.return_lobby()

    def return_lobby(self):
        response = HttpResponse('Unauthorized - Token expired', status=401)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.delete_cookie('sessionid')
        response.delete_cookie('login42')
        return response

class TokenRefreshResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(request, 'new_access_token') and hasattr(request, 'new_refresh_token'):
            response.set_cookie('access_token', request.new_access_token, httponly=True, secure=True)
            response.set_cookie('refresh_token', request.new_refresh_token, httponly=True, secure=True)

        return response
