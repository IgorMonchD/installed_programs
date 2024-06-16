import os
import django
import psycopg2
from sys import platform
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from software.models import *

data_objects = Data.objects.all()    
directory_objects = Directory.objects.all()
while True:
    for data_object in data_objects:         
        for directory_object in directory_objects:        
             if directory_object.name in data_object.name:                 
                 data_object.directory = directory_object                
                 data_object.save()
