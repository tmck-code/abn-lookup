#!/usr/bin/env python3

from argparse import ArgumentParser
from dataclasses import dataclass
from itertools import islice
import os
from typing import Generator, Optional

import requests

import xmltodict

from pp import pp

STATES = ['NSW', 'ACT', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT']
DEBUG = os.environ.get('DEBUG', '0') == '1'

@dataclass
class ABNLookupClient:
    authentication_guid: str

    def _request(self, url: str, params: dict) -> dict:
        'Internal method to perform a GET request to the ABR XML Search API. Converts XML response to dict.'
        if DEBUG:
            pp.ppd({'url': url, 'params': params}, style=None)
        response = requests.get(url, params=params | {'authenticationGuid': self.authentication_guid})
        response.raise_for_status()
        if DEBUG:
            pp.ppd({'response': {'status_code': response.status_code, 'text': response.text}}, style=None)
        parsed = xmltodict.parse(response.text)
        if DEBUG:
            pp.ppd({'parsed': parsed}, style=None)
        return parsed

    def _state_flags(self, state: str) -> dict:
        'Generate state flags for API requests.'
        return {k: 'Y' if k == state else 'N' for k in STATES}

    def _iter_search_results(self, result: dict, result_list_key: str, record_key: str, limit: Optional[int] = None) -> Generator[dict, None, None]:
        'Generator that yields individual search results from a search response.'
        yield from islice(
            result.get('ABRPayloadSearchResults', {}).get('response', {}).get(result_list_key, {}).get(record_key, []),
            limit
        )

    def search_by_abn(self, abn: str, includeHistoricalDetails: str = 'N') -> Generator[dict, None, None]:
        '''
        Search for an entity by ABN.
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchbyABN
        '''
        yield self._request(
            'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/ABRSearchByABN',
            {
                'searchString': abn,
                'includeHistoricalDetails': includeHistoricalDetails
            }
        )

    def search_by_asic(self, asic: str, includeHistoricalDetails: str = 'N') -> Generator[dict, None, None]:
        '''
        Search for an entity by ASIC number (ACN, ARBN, ARSN, ARFN).
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchbyASICnumber
        '''
        yield self._request(
            'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/ABRSearchByASIC',
            {
                'searchString': asic,
                'includeHistoricalDetails': includeHistoricalDetails
            }
        )

    def search_by_name(self, name: str, postcode: str = '', legalName: str = '', businessName: str = '', tradingName: str = '', state: str = '') -> Generator[dict, None, None]:
        '''
        Search for entities by name (simple protocol).
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchbyName
        '''
        params = {
            'name': name,
            'postcode': postcode,
            'legalName': legalName,
            'businessName': businessName,
            'tradingName': tradingName,
            **self._state_flags(state)
        }
        yield from self._iter_search_results(
            self._request(
                'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/ABRSearchByNameSimpleProtocol',
                params,
            ),
            result_list_key='searchResultsList',
            record_key='searchResultsRecord'
        )

    def search_by_name_advanced(self, name: str, postcode: str = '', legalName: str = '', businessName: str = '', tradingName: str = '', state: str = '', searchWidth: str = '', minimumScore: int = 0, maxSearchResults: int = 0, activeABNsOnly: str = '') -> Generator[dict, None, None]:
        '''
        Advanced search for entities by name.
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchbyName
        '''
        params = {
            'name': name,
            'postcode': postcode,
            'legalName': legalName,
            'businessName': businessName,
            'tradingName': tradingName,
            'searchWidth': searchWidth,
            'minimumScore': minimumScore if minimumScore else '',
            'maxSearchResults': maxSearchResults if maxSearchResults else '',
            'activeABNsOnly': activeABNsOnly,
            **self._state_flags(state)
        }
        yield from self._iter_search_results(
            self._request(
                'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/ABRSearchByNameAdvancedSimpleProtocol',
                params,
            ),
            result_list_key='searchResultsList',
            record_key='searchResultsRecord'
        )

    def search_by_postcode(self, postcode: str) -> Generator[dict, None, None]:
        '''
        Search for entities by postcode.
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchwithFilters
        '''
        params = {
            'postcode': postcode,
        }
        yield from self._iter_search_results(
            self._request(
                'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/SearchByPostcode',
                params,
            ),
            result_list_key='abnList',
            record_key='abn'
        )

    def search_by_abn_status(self, postcode: str = '', activeABNsOnly: str = '', currentGSTRegistrationOnly: str = '', entityTypeCode: str = '') -> Generator[dict, None, None]:
        '''
        Search for entities by ABN status.
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchwithFilters
        '''
        params = {
            'postcode': postcode,
            'activeABNsOnly': activeABNsOnly,
            'currentGSTRegistrationOnly': currentGSTRegistrationOnly,
            'entityTypeCode': entityTypeCode,
        }
        yield from self._iter_search_results(
            self._request(
                'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/SearchByABNStatus',
                params,
            ),
            result_list_key='abnList',
            record_key='abn'
        )

    def search_by_update_event(self, updatedate: str, postcode: str = '', state: str = '', entityTypeCode: str = '') -> Generator[dict, None, None]:
        '''
        Search for entities by update event.
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchwithFilters
        '''
        params = {
            'postcode': postcode,
            'state': state,
            'entityTypeCode': entityTypeCode,
            'updatedate': updatedate,
        }
        yield from self._iter_search_results(
            self._request(
                'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/SearchByUpdateEvent',
                params,
            ),
            result_list_key='abnList',
            record_key='abn'
        )

    def search_by_registration_event(self, month: str, year: str, postcode: str = '', state: str = '', entityTypeCode: str = '') -> Generator[dict, None, None]:
        '''
        Search for entities by registration event.
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchwithFilters
        '''
        params = {
            'postcode': postcode,
            'state': state,
            'entityTypeCode': entityTypeCode,
            'month': month,
            'year': year,
        }
        yield from self._iter_search_results(
            self._request(
                'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/SearchByRegistrationEvent',
                params,
            ),
            result_list_key='abnList',
            record_key='abn'
        )

    def search_by_charity(self, postcode: str = '', state: str = '', charityTypeCode: str = '', concessionTypeCode: str = '') -> Generator[dict, None, None]:
        '''
        Search for charities.
        See: https://abr.business.gov.au/Documentation/WebServiceMethods#SearchwithFilters
        '''
        params = {
            'postcode': postcode,
            'state': state,
            'charityTypeCode': charityTypeCode,
            'concessionTypeCode': concessionTypeCode,
        }
        yield from self._iter_search_results(
            self._request(
                'https://abr.business.gov.au/ABRXMLSearchRPC/ABRXMLSearch.asmx/SearchByCharity',
                params,
            ),
            result_list_key='abnList',
            record_key='abn'
        )


def parse_args():
    parser = ArgumentParser(description='ABN Lookup Client')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # search_by_abn
    parser_abn = subparsers.add_parser('abn', help='Search by ABN')
    parser_abn.add_argument('--abn', type=str, required=True, help='ABN to search for')
    parser_abn.add_argument('--includeHistoricalDetails', type=str, default='N', choices=['Y', 'N'], help='Include historical details')

    # search_by_asic
    parser_asic = subparsers.add_parser('asic', help='Search by ASIC')
    parser_asic.add_argument('--asic', type=str, required=True, help='ASIC number to search for')
    parser_asic.add_argument('--includeHistoricalDetails', type=str, default='N', choices=['Y', 'N'], help='Include historical details')

    # search_by_name
    parser_name = subparsers.add_parser('name', help='Search by name')
    parser_name.add_argument('--name', type=str, required=True, help='Name to search for')
    parser_name.add_argument('--state', type=str, required=True, choices=STATES, help='State to filter results by')
    parser_name.add_argument('--limit', type=int, default=10, help='Maximum number of results to return')

    # search_by_name_advanced
    parser_name_adv = subparsers.add_parser('name-advanced', help='Advanced search by name')
    parser_name_adv.add_argument('--name', type=str, required=True, help='Name to search for')
    parser_name_adv.add_argument('--postcode', type=str, default='', help='Postcode (optional)')
    parser_name_adv.add_argument('--tradingName', type=str, default='', help='Trading name (optional)')
    parser_name_adv.add_argument('--legalName', type=str, default='', help='Legal name (optional)')
    parser_name_adv.add_argument('--state', type=str, default='', choices=STATES, help='State to filter results by (optional)')

    # filter searches ---------------------------

    # search_by_postcode
    parser_postcode = subparsers.add_parser('postcode', help='Search by postcode')
    parser_postcode.add_argument('--postcode', type=str, required=True, help='Postcode to search for')

    # search_by_abn_status
    parser_abn_status = subparsers.add_parser('abn-status', help='Search by ABN status')
    parser_abn_status.add_argument('--postcode', type=str, default='', help='Postcode (optional)')
    parser_abn_status.add_argument('--activeABNsOnly', type=str, default='', help='Active ABNs only (optional)')
    parser_abn_status.add_argument('--currentGSTRegistrationOnly', type=str, default='', help='Current GST registration only (optional)')
    parser_abn_status.add_argument('--entityTypeCode', type=str, default='', help='Entity type code (optional)')

    # search_by_update_event
    parser_update_event = subparsers.add_parser('update-event', help='Search by update event')
    parser_update_event.add_argument('--updatedate', type=str, required=True, help='Update date (YYYY-MM-DD format)')
    parser_update_event.add_argument('--state', type=str, default='', choices=STATES, help='State to filter results by (optional)')
    parser_update_event.add_argument('--postcode', type=str, default='', help='Postcode (optional)')
    parser_update_event.add_argument('--entityTypeCode', type=str, default='', help='Entity type code (optional)')

    # search_by_registration_event
    parser_reg_event = subparsers.add_parser('registration-event', help='Search by registration event')
    parser_reg_event.add_argument('--month', type=str, required=True, help='Month (1-12)')
    parser_reg_event.add_argument('--year', type=str, required=True, help='Year (YYYY format)')
    parser_reg_event.add_argument('--state', type=str, default='', choices=STATES, help='State to filter results by (optional)')
    parser_reg_event.add_argument('--postcode', type=str, default='', help='Postcode (optional)')
    parser_reg_event.add_argument('--entityTypeCode', type=str, default='', help='Entity type code (optional)')

    # search_by_charity
    parser_charity = subparsers.add_parser('charity', help='Search by charity')
    parser_charity.add_argument('--state', type=str, default='', choices=STATES, help='State to filter results by (optional)')
    parser_charity.add_argument('--postcode', type=str, default='', help='Postcode (optional)')
    parser_charity.add_argument('--charityTypeCode', type=str, default='', help='Charity type code (optional)')
    parser_charity.add_argument('--concessionTypeCode', type=str, default='', help='Concession type code (optional)')

    return vars(parser.parse_args())

def main():
    args = parse_args()
    client = ABNLookupClient(authentication_guid=os.environ['ABN_LOOKUP_GUID'])

    command = args.pop('command')
    limit = args.pop('limit', None)

    match command:
        case 'abn-status':
            results = client.search_by_abn_status(**args)
        case 'charity':
            results = client.search_by_charity(**args)
        case 'registration-event':
            results = client.search_by_registration_event(**args)
        case 'update-event':
            results = client.search_by_update_event(**args)
        case 'name':
            results = client.search_by_name(**args)
        case 'abn':
            results = client.search_by_abn(**args)
        case 'asic':
            results = client.search_by_asic(**args)
        case 'postcode':
            results = client.search_by_postcode(**args)
        case 'name-advanced':
            results = client.search_by_name_advanced(**args)
        case _:
            print(f"Unknown command: {command}")
            return

    for i, record in enumerate(results):
        if limit and i >= limit:
            break
        pp.ppd(record, indent=None, style=None)

if __name__ == '__main__':
    main()
