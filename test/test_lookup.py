#!/usr/bin/env python3

import pytest
import requests
import xmltodict

from abn_lookup.lookup import ABNLookupClient


@pytest.fixture
def client():
    return ABNLookupClient(authentication_guid='test-guid-12345')


@pytest.fixture
def single_result_dict():
    return {
        'ABRPayloadSearchResults': {
            'response': {
                'businessEntity': {
                    'ABN':          {'identifierValue': '51824753556'},
                    'entityStatus': 'Active',
                    'mainName':     {'organisationName': 'Test Company'}
                }
            }
        }
    }


@pytest.fixture
def multiple_results_dict():
    return {
        'ABRPayloadSearchResults': {
            'response': {
                'searchResultsList': {
                    'searchResultsRecord': [
                        {'ABN': '51824753556', 'name': 'Test Company 1'},
                        {'ABN': '12345678901', 'name': 'Test Company 2'}
                    ]
                }
            }
        }
    }


def test_search_by_abn(client, single_result_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByABN',
        text=xmltodict.unparse(single_result_dict)
    )
    
    results = list(client.search_by_abn('51824753556'))
    
    assert len(results) == 1
    assert 'ABRPayloadSearchResults' in results[0]
    assert 'searchString=51824753556' in requests_mock.last_request.url
    assert 'authenticationGuid=test-guid-12345' in requests_mock.last_request.url


def test_search_by_abn_with_history(client, single_result_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByABN',
        text=xmltodict.unparse(single_result_dict)
    )
    
    results = list(client.search_by_abn('51824753556', includeHistoricalDetails='Y'))
    
    assert len(results) == 1
    assert 'includeHistoricalDetails=Y' in requests_mock.last_request.url


def test_search_by_asic(client, single_result_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByASIC',
        text=xmltodict.unparse(single_result_dict)
    )
    
    results = list(client.search_by_asic('123456789'))
    
    assert len(results) == 1
    assert 'searchString=123456789' in requests_mock.last_request.url


def test_search_by_name(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByNameSimpleProtocol',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    results = list(client.search_by_name('Test Company', state='NSW'))
    
    assert len(results) == 2
    assert results[0]['ABN'] == '51824753556'
    assert results[1]['ABN'] == '12345678901'
    assert 'name=Test+Company' in requests_mock.last_request.url
    assert 'NSW=Y' in requests_mock.last_request.url


def test_search_by_abn_status(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByABNStatus',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    results = list(client.search_by_abn_status('ACT', state='NSW', postcode='2000'))
    
    assert len(results) == 2
    assert 'entityStatusCode=ACT' in requests_mock.last_request.url
    assert 'state=NSW' in requests_mock.last_request.url
    assert 'postcode=2000' in requests_mock.last_request.url


def test_search_by_charity(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByCharity',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    results = list(client.search_by_charity(postcode='2000', state='NSW'))
    
    assert len(results) == 2
    assert 'postcode=2000' in requests_mock.last_request.url
    assert 'state=NSW' in requests_mock.last_request.url


def test_search_by_registration_event(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByRegistrationEvent',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    results = list(client.search_by_registration_event(
        'GST', '2020-01-01', '2020-12-31', state='VIC'
    ))
    
    assert len(results) == 2
    assert 'eventType=GST' in requests_mock.last_request.url
    assert 'fromDate=2020-01-01' in requests_mock.last_request.url
    assert 'toDate=2020-12-31' in requests_mock.last_request.url


def test_search_by_update_event(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByUpdateEvent',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    results = list(client.search_by_update_event(
        'GST', '2020-01-01', '2020-12-31', postcode='3000'
    ))
    
    assert len(results) == 2
    assert 'eventType=GST' in requests_mock.last_request.url
    assert 'fromDate=2020-01-01' in requests_mock.last_request.url
    assert 'toDate=2020-12-31' in requests_mock.last_request.url
    assert 'postcode=3000' in requests_mock.last_request.url


def test_search_by_postcode(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByPostcode',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    results = list(client.search_by_postcode('2000', state='NSW'))
    
    assert len(results) == 2
    assert 'postcode=2000' in requests_mock.last_request.url
    assert 'state=NSW' in requests_mock.last_request.url


def test_search_by_name_advanced(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByNameAdvancedSimpleProtocol',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    results = list(client.search_by_name_advanced(
        'Test Company',
        postcode='2000',
        legalName='Y',
        searchWidth='Typical',
        minimumScore=80
    ))
    
    assert len(results) == 2
    assert 'name=Test+Company' in requests_mock.last_request.url
    assert 'postcode=2000' in requests_mock.last_request.url
    assert 'legalName=Y' in requests_mock.last_request.url
    assert 'searchWidth=Typical' in requests_mock.last_request.url
    assert 'minimumScore=80' in requests_mock.last_request.url


def test_state_flags_generation(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByNameSimpleProtocol',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    list(client.search_by_name('Test', state='VIC'))
    
    url = requests_mock.last_request.url
    assert 'VIC=Y' in url
    assert 'NSW=N' in url
    assert 'QLD=N' in url


def test_empty_params_filtered(client, multiple_results_dict, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByCharity',
        text=xmltodict.unparse(multiple_results_dict)
    )
    
    list(client.search_by_charity(postcode='', state='NSW'))
    
    url = requests_mock.last_request.url
    # postcode should not be in params since it's empty
    assert 'postcode=' not in url
    assert 'state=NSW' in url


def test_http_error_handling(client, requests_mock):
    requests_mock.get(
        'https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/ABRSearchByABN',
        status_code=404,
        text='Not Found'
    )
    
    with pytest.raises(requests.exceptions.HTTPError):
        list(client.search_by_abn('invalid'))
