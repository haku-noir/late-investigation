"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import include
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from late_investigation import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', login_required(auth_views.LogoutView.as_view()), name='logout'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('user/', login_required(views.UserList.as_view()), name='user'),
    path('user/register/', views.UserRegister.as_view(), name='user_register'),
    path('user/edit/', login_required(views.UserEdit.as_view()), name='user_edit'),
    path('route/', login_required(views.Routelist.as_view()), name='route'),
    path('delay/register/', login_required(views.DelayRegister.as_view()), name='delay_register'),
    path('user/delay/', login_required(views.UserDelayList.as_view()), name='userdelay'),
    path('user/delay/register/', login_required(views.UserDelayRegister.as_view()), name='userdelay_register'),
    path('user/delay/history/', login_required(views.UserDelayHistory.as_view()), name='userdelay_history'),
]
