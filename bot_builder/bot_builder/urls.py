"""
URL configuration for bot_builder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from apps.worker.views import *
from apps.worker.views import task_complete_alert
from apps.bot.views import handle_payment_return


urlpatterns = [
    path('admin/', admin.site.urls),
    path('task_complete_alert', task_complete_alert, name='task_complete_alert'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
