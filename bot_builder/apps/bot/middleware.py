from django.http import HttpResponseForbidden
from apps.bot.models import UserValidIP

class AdminIPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):  # Проверяем только путь /admin/
            ip = self.get_client_ip(request)
            if not self.is_ip_allowed(ip):
                return HttpResponseForbidden("Access Denied: Unauthorized IP")
        return self.get_response(request)

    def get_client_ip(self, request):
        """Получаем IP-адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_ip_allowed(self, ip):
        """Проверяем, разрешен ли IP"""
        return UserValidIP.objects.filter(ip=ip).exists()
    


from django.http import HttpResponseForbidden
from django.contrib.auth.models import User

class RoleBasedIPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):  # Проверяем только путь /admin/
            if request.user.is_authenticated:  # Убедимся, что пользователь аутентифицирован
                ip = self.get_client_ip(request)
                # Проверяем, есть ли связанный IP у пользователя
                if not self.is_ip_allowed(request.user, ip):
                    return HttpResponseForbidden("Access Denied: Unauthorized IP")
        return self.get_response(request)

    def get_client_ip(self, request):
        """Получаем IP-адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_ip_allowed(self, user, ip):
        """Проверяем, разрешен ли IP для данного пользователя"""
        try:
            # Получаем все записи разрешённых IP для пользователя
            users_ip = UserValidIP.objects.filter(linked_user=user)
            # Проверяем, совпадает ли текущий IP с любым из разрешённых
            return any(user_ip.ip == ip for user_ip in users_ip)
        except UserValidIP.DoesNotExist:
            return False