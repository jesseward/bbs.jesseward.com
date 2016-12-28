import logging
import requests

from x84.bbs import echo, disconnect, get_ini, getterminal

log = logging.getLogger()

#: list of banned countries
geo_banned_counties = get_ini(
    section='geo-check', key='banned', split=True
) or list()

#: disconnect message string
geo_disconnect_message = get_ini(
    section='geo-check', key='message'
) or 'Please call back later'

def main():
    """Performs a lookup against freegeoip and drops client connections if
    the source IP belongs a netblock from a banned country/region."""

    term = getterminal()

    FREEGEOIP = 'http://freegeoip.net/json/'
    source_ip = term.session.addrport.rsplit(':', 1)[0]

    try:
        source = requests.get(FREEGEOIP + source_ip, timeout=0.5).json()
    except (requests.exceptions.RequestException, ValueError) as e:
        log.error('Unable to query FREEGEOIP, source_ip={0}, error={1}'.format(source_ip, e))
        return
    log.info('source_ip={0}, country_code={1}'.format(source_ip, source.get('country_code')))

    if source.get('country_code') in geo_banned_counties:
        log.warn('Source {0} is from banned country "{1}".'.format(source_ip, source['country_code']))
        echo(geo_disconnect_message + u'\r\n')
        disconnect('country is banned')
