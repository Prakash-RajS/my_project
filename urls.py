"""from django.urls import path
from . import views  # to use views from views.py

urlpatterns = [
    path('', views.login_page, name='login'),  # Home page shows login.html
    path('signup/', views.signup_view, name='signup'),  # Go to signup page
    path('index/', views.index_view, name='index'),  # Go to index page (Home page after login)
    path('login/', views.login_page, name='login_view'),  # Explicit login view for form submission
]
"""

# urls.py
"""from django.urls import path
from .views import FrontendAppView

urlpatterns = [
    path('', FrontendAppView.as_view(), name='frontend'),
    # other urls...
]
"""

from django.contrib import admin
from django.urls import path,  include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('', TemplateView.as_view(template_name='index.html')),
    #path("login/<str:provider>/", views.auth_login, name="auth_login"),
    #path("callback/", views.auth_callback, name="auth_callback"),
     # Social login routes
    path('google/', views.auth_login, {'provider': 'google-oauth2'}, name='google_login'),
    path('facebook/', views.auth_login, {'provider': 'facebook'}, name='facebook_login'),
    path('apple/', views.auth_login, {'provider': 'apple'}, name='apple_login'),

    # Callback URL from Auth0
    path('callback/', views.auth_callback, name='auth_callback'),
    path('auth/', include('social_django.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#check "auth0 update" comment
