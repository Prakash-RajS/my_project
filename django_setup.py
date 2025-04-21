#create this file for (profile datas validations)
#and used to connect the db in django
# fastapi_app/django_setup.py

# fastapi_app/django_setup.py
import os
import django

def django_setup():
    # Set the DJANGO_SETTINGS_MODULE environment variable before setting up Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")
    
    # Initialize Django
    django.setup()