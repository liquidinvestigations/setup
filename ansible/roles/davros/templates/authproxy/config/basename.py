{% if use_https %}
LIQUID_URL = 'https://{{ liquid_domain }}'
{% else $}
LIQUID_URL = 'http://{{ liquid_domain }}'
{% endif %}
