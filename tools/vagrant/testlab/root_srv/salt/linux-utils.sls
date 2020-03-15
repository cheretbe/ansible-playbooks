Update system packages:
  pkg.uptodate:
    - refresh: True

# 'CentOS', 'RedHat'
{% if grains['os'] in ['Ubuntu', 'Debian'] %}
  {% set packages_to_install = ['mc', 'htop', 'net-tools', 'dnsutils',
    'mtr-tiny', 'ncdu', 'wget', 'git', 'nano', 'dialog'] %}
{% else %}
  {% set packages_to_install = ['mc', 'htop', 'net-tools', 'bind-utils',
    'mtr', 'ncdu', 'wget', 'git', 'nano', 'dialog'] %}
{% endif %}

utils:
  pkg:
    - names: {{ packages_to_install }}
    - installed
    - require: [Update system packages]