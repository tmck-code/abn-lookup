#!/usr/bin/env python3

from argparse import ArgumentParser
from dataclasses import dataclass
import os

import requests
from urllib.parse import urlencode

import xmltodict

from pp import pp

STATES = ['NSW', 'ACT', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT']

@dataclass
class ABNLookupClient:
    authentication_guid: str

    def _request(self, url: str, params: dict) -> dict:
        # pp.ppd({'url': url, 'params': params})
        response = requests.get(url, params=urlencode(params | {'authenticationGuid': self.authentication_guid}))

        # pp.ppd({'response': {'status_code': response.status_code, 'text': response.text}})
        response.raise_for_status()

        parsed = xmltodict.parse(response.text)
        return parsed

    def _state_flags(self, state: str) -> dict:
        return {k: 'Y' if k == state else 'N' for k in STATES}

    def search_by_name(self, name: str, state: str = '') -> dict:
        return self._request(
            'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByNameSimpleProtocol',
            {
                'name': name,
                'postcode': '',
                'tradingName': '',
                'legalName': '',
                **self._state_flags(state)
            }
        )

def parse_args():
    args = ArgumentParser(description='ABN Lookup Client')
    args.add_argument('--name', type=str, required=True, help='Name to search for')
    args.add_argument('--state', type=str, required=True, choices=['NSW', 'ACT', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT'], help='State to filter results by')
    args.add_argument('--limit', type=int, default=10, help='Maximum number of results to return')
    return args.parse_args().__dict__

def main():
    args = parse_args()
    client = ABNLookupClient(authentication_guid=os.environ['ABN_LOOKUP_GUID'])
    result = client.search_by_name(name=args['name'], state=args['state'])
    for i, r in enumerate(result['ABRPayloadSearchResults']['response']['searchResultsList']['searchResultsRecord']):
        if i >= args['limit']:
            break
        pp.ppd({'result': r}, indent=None, style=None)

if __name__ == '__main__':
    main()