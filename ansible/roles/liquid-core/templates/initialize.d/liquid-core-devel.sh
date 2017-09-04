#!/bin/bash

# create initial admin user
sudo -u liquid /opt/liquid-core/venv/bin/python /opt/liquid-core/liquid-core/manage.py shell <<EOF
from django.contrib.auth.models import User
if User.objects.filter(username='liquid'): exit()

user = User.objects.create_user('liquid', password='liquid')
user.is_superuser=True
user.is_staff=True
user.save()
EOF
