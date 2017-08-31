#!/bin/bash

sudo -u liquid /opt/liquid-core/libexec/create-oauth-application "hoover" "http{% if use_https %}s{% endif %}://hoover.{{ liquid_domain }}/accounts/oauth2-exchange/"

sudo -u liquid /opt/liquid-core/libexec/create-oauth-application "davros" "http{% if use_https %}s{% endif %}://davros.{{ liquid_domain }}/__auth/callback"

