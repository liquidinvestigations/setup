#!/bin/bash

sudo -u liquid /opt/liquid-core/libexec/create-oauth-application "hoover" "{{ http_scheme }}://hoover.{{ liquid_domain }}/accounts/oauth2-exchange/"

sudo -u liquid /opt/liquid-core/libexec/create-oauth-application "davros" "{{ http_scheme }}://davros.{{ liquid_domain }}/__auth/callback"

