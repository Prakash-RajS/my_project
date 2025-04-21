from django.contrib import admin
from django.urls import path, include
from appln import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('auth/', include('appln.urls')), #for auth0
    path('auth/', include('social_django.urls')),  # For social authentication
    path('signup/', include('appln.urls')),
    path('', views.signup_view, name='home'),  # Add this line for the root URL
]
