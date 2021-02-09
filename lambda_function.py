import re
import urllib.parse as urlparse
import requests
import json

base_url = "https://dnsdumpster.com/"


if 'session' not in globals():
    session = requests.Session()


def get_response(response):
    if response is None:
        return 0
    return response.text if hasattr(response, "text") else response.content


def send_req(domain):
    try:
        resp = session.get(base_url)
        csrf_token = resp.text.split(
            '<input type="hidden" name="csrfmiddlewaretoken" value="')[1].split('"')[0].strip()
        data = {'csrfmiddlewaretoken': csrf_token, 'targetip': domain}
        resp = session.post(base_url, data=data, headers={
                            'Referer': 'https://dnsdumpster.com'})

    except Exception:
        resp = None
    return get_response(resp)


def enumerate(domain):
    r = send_req(domain)
    subdomains = extract_domains(r)

    return subdomains


def extract_domains(resp):

    subdomains = set()
    print(resp)
    s = resp.split('Host Record')[1]
    try:
        for line in s.split('<tr><td class="col-md-4">'):
            d = line.split('<br>')[0]
            if '*' not in d:
                subdomains.add(d)
    except Exception:
        pass

    return list(subdomains)


def lambda_handler(event, context):

    domain = event['domain']
    domains = enumerate(domain)
    return {
        'statusCode': 200,
        'body': json.dumps(domains)
    }


