#!/bin/bash

{% if devel %}
# create initial admin user
sudo -u liquid /opt/liquid-core/venv/bin/python /opt/liquid-core/liquid-core/manage.py shell <<EOF
from django.contrib.auth.models import User
if User.objects.filter(username='liquid'): exit()

user = User.objects.create_user('liquid', password='liquid')
user.is_superuser=True
user.is_staff=True
user.save()
EOF
{% endif %}

sudo -u liquid /opt/liquid-core/libexec/create-oauth-application "hoover" "http{% if use_https %}s{% endif %}://hoover.{{ liquid_domain }}/accounts/oauth2-exchange/"

sudo -u liquid /opt/liquid-core/libexec/create-oauth-application "davros" "http{% if use_https %}s{% endif %}://davros.{{ liquid_domain }}/__auth/callback"

