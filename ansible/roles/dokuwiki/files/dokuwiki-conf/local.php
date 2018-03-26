<?php
/**
 * Dokuwiki's Main Configuration File - Local Settings
 * Auto-generated by liquid initialization script
 * Date: {timestamp}
 */
$conf['title'] = '{title}';
$conf['lang'] = 'en';
$conf['license'] = '0';
$conf['useacl'] = 1;
$conf['superuser'] = '@admin';
$conf['disableactions'] = 'register';
$conf['authtype'] = 'oauth';
$conf['defaultgroup'] = 'admin,user';
$conf['plugin']['oauth']['liquid-key'] = '{oauth_id}';
$conf['plugin']['oauth']['liquid-secret'] = '{oauth_secret}';
$conf['plugin']['oauth']['liquid-authurl'] = '{oauth_url}authorize';
$conf['plugin']['oauth']['liquid-tokenurl'] = '{oauth_url}token';
