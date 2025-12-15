# abn-lookup
A python client to interact with ABN Lookup services

This library provides a Python interface to the [Australian Business Register (ABR) XML Search API](https://abr.business.gov.au/Documentation/WebServiceMethods). All API methods are based on the official ABR documentation.

- [abn-lookup](#abn-lookup)
  - [Installation](#installation)
  - [Authentication](#authentication)
    - [CLI](#cli)
  - [Usage](#usage)
    - [Python Library](#python-library)
      - [Basic Example](#basic-example)
      - [Advanced Example](#advanced-example)
    - [Supported Methods](#supported-methods)
      - [SearchByABN (docs)](#searchbyabn-docs)
      - [SearchByASIC (docs)](#searchbyasic-docs)
      - [SearchByName (docs)](#searchbyname-docs)
      - [SearchByNameAdvanced (docs)](#searchbynameadvanced-docs)
      - [SearchByPostcode (docs)](#searchbypostcode-docs)
      - [SearchByABNStatus (docs)](#searchbyabnstatus-docs)
      - [SearchByCharity (docs)](#searchbycharity-docs)
      - [SearchByRegistrationEvent (docs)](#searchbyregistrationevent-docs)
      - [SearchByUpdateEvent (docs)](#searchbyupdateevent-docs)
  - [Development](#development)
    - [Testing](#testing)
      - [Docker](#docker)
      - [Host Machine](#host-machine)


## Installation

```bash
python3 -m pip install 'abn-lookup @ git+https://github.com/tmck-code/abn-lookup'
```

## Authentication

You'll need an ABN Lookup GUID from the [Australian Business Register](https://abr.business.gov.au/). Set it as an environment variable:

```bash
export ABN_LOOKUP_GUID="your-guid-here"
```

### CLI

The package includes a command-line interface:

```bash
# Search by ABN
abn-lookup abn --abn 53004085616

# Search by name
abn-lookup name --name "Telstra" --state "VIC" --limit 5

# Search by postcode
abn-lookup postcode --postcode "3000" --state "VIC"

# Advanced name search
abn-lookup name-advanced --name "Commonwealth Bank" --state "NSW" --legalName "Y"
```

Run with `--help` to see all available commands and options:

```bash
abn-lookup --help
```
<details>
<summary><i>Example help output</i></summary>

```
usage: lookup.py [-h] {abn-status,charity,registration-event,update-event,name,abn,asic,postcode,name-advanced} ...

ABN Lookup Client

positional arguments:
  {abn-status,charity,registration-event,update-event,name,abn,asic,postcode,name-advanced}
    abn-status          Search by ABN status
    charity             Search by charity
    registration-event  Search by registration event
    update-event        Search by update event
    name                Search by name
    abn                 Search by ABN
    asic                Search by ASIC
    postcode            Search by postcode
    name-advanced       Advanced search by name

options:
  -h, --help            show this help message and exit
```

</details>

```bash
abn-lookup name --help
```

<details>
<summary><i>Example help output for 'name' command</i></summary>

```
usage: lookup.py name [-h] --name NAME --state {NSW,ACT,VIC,QLD,SA,WA,TAS,NT} [--limit LIMIT]

options:
  -h, --help            show this help message and exit
  --name NAME           Name to search for
  --state {NSW,ACT,VIC,QLD,SA,WA,TAS,NT}
                        State to filter results by
  --limit LIMIT         Maximum number of results to return
```

</details>

## Usage

### Python Library

#### Basic Example

```python
from abn_lookup.lookup import ABNLookupClient
import os

# Initialize the client
client = ABNLookupClient(authentication_guid=os.environ['ABN_LOOKUP_GUID'])

# Search by ABN
for result in client.search_by_abn('53004085616'):
    print(result)

# Search by business name
for result in client.search_by_name(name='Telstra', state='VIC'):
    print(result)

# {"ABN": {"identifierValue": "53653884756", "identifierStatus": "Active"}, "mainName": {"organisationName": "MOONTH MOTORS PTY LTD", "score": "98", "isCurrentIndicator": "Y"}, "mainBusinessPhysicalAddress": {"stateCode": "VIC", "postcode": "3031", "isCurrentIndicator": "Y"}}
# ...
```

#### Advanced Example

```python
from abn_lookup.lookup import ABNLookupClient
import os

client = ABNLookupClient(authentication_guid=os.environ['ABN_LOOKUP_GUID'])

# Advanced name search with filters
results = client.search_by_name_advanced(
    name='Commonwealth Bank',
    state='NSW',
    legalName='Y',
    minimumScore=80,
    maxSearchResults=10
)

for result in results:
    # Access result fields
    abn = result.get('ABN', {}).get('identifierValue')
    name = result.get('mainName', {}).get('organisationName')
    print(f"ABN: {abn}, Name: {name}")

# ABN: 48045546848, Name: COMMONWEALTH BANK OF AUSTRALIA
# ABN: 53004085616, Name: COMMONWEALTH BANK OF AUSTRALIA
# ...
```

### Supported Methods

#### SearchByABN ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#abn))
*Search for an entity by ABN.*

**Parameters:**
- `abn` (str, required): The ABN to search for
- `includeHistoricalDetails` (str, optional): 'Y' or 'N' (default: 'N')

#### SearchByASIC ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#acn))
*Search for an entity by ASIC number (ACN, ARBN, ARSN, ARFN).*

**Parameters:**
- `asic` (str, required): The ASIC number to search for
- `includeHistoricalDetails` (str, optional): 'Y' or 'N' (default: 'N')

#### SearchByName ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#name))
*Search for entities by name (simple protocol).*

**Parameters:**
- `name` (str, required): Name to search for
- `postcode` (str, optional): Filter by postcode
- `legalName` (str, optional): 'Y' to search legal names only
- `businessName` (str, optional): 'Y' to search business names only
- `tradingName` (str, optional): 'Y' to search trading names only
- `state` (str, optional): Filter by state (NSW, ACT, VIC, QLD, SA, WA, TAS, NT)

#### SearchByNameAdvanced ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#name))
*Advanced search for entities by name with additional filters.*

**Parameters:**
- `name` (str, required): Name to search for
- `postcode` (str, optional): Filter by postcode
- `legalName` (str, optional): 'Y' to search legal names only
- `businessName` (str, optional): 'Y' to search business names only
- `tradingName` (str, optional): 'Y' to search trading names only
- `state` (str, optional): Filter by state
- `searchWidth` (str, optional): Search width (narrow, typical, wide)
- `minimumScore` (int, optional): Minimum matching score (0-100)
- `maxSearchResults` (int, optional): Maximum number of results to return
- `activeABNsOnly` (str, optional): 'Y' to return only active ABNs

#### SearchByPostcode ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#filters))
*Search for entities by postcode.*

**Parameters:**
- `postcode` (str, required): The postcode to search for
- `state` (str, optional): Filter by state
- `activeABNsOnly` (str, optional): 'Y' to return only active ABNs
- `currentGSTRegistrationOnly` (str, optional): 'Y' to return only GST registered entities
- `entityTypeCode` (str, optional): Filter by entity type code
- `concessionTypeCode` (str, optional): Filter by concession type code

#### SearchByABNStatus ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#filters))
*Search for entities by ABN status.*

**Parameters:**
- `entityStatusCode` (str, required): Entity status code
- `postcode` (str, optional): Filter by postcode
- `state` (str, optional): Filter by state
- `activeABNsOnly` (str, optional): 'Y' to return only active ABNs
- `currentGSTRegistrationOnly` (str, optional): 'Y' to return only GST registered entities
- `entityTypeCode` (str, optional): Filter by entity type code
- `concessionTypeCode` (str, optional): Filter by concession type code

#### SearchByCharity ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#filters))
*Search for charities.*

**Parameters:**
- `postcode` (str, optional): Filter by postcode
- `state` (str, optional): Filter by state
- `activeABNsOnly` (str, optional): 'Y' to return only active ABNs
- `currentGSTRegistrationOnly` (str, optional): 'Y' to return only GST registered entities
- `entityTypeCode` (str, optional): Filter by entity type code
- `concessionTypeCode` (str, optional): Filter by concession type code

#### SearchByRegistrationEvent ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#filters))
*Search for entities by registration event.*

**Parameters:**
- `eventType` (str, required): Event type
- `fromDate` (str, required): From date (YYYY-MM-DD format)
- `toDate` (str, required): To date (YYYY-MM-DD format)
- `postcode` (str, optional): Filter by postcode
- `state` (str, optional): Filter by state
- `activeABNsOnly` (str, optional): 'Y' to return only active ABNs
- `currentGSTRegistrationOnly` (str, optional): 'Y' to return only GST registered entities
- `entityTypeCode` (str, optional): Filter by entity type code
- `concessionTypeCode` (str, optional): Filter by concession type code

#### SearchByUpdateEvent ([docs](https://abr.business.gov.au/Documentation/WebServiceMethods#filters))
*Search for entities by update event.*

**Parameters:**
- `eventType` (str, required): Event type
- `fromDate` (str, required): From date (YYYY-MM-DD format)
- `toDate` (str, required): To date (YYYY-MM-DD format)
- `postcode` (str, optional): Filter by postcode
- `state` (str, optional): Filter by state
- `activeABNsOnly` (str, optional): 'Y' to return only active ABNs
- `currentGSTRegistrationOnly` (str, optional): 'Y' to return only GST registered entities
- `entityTypeCode` (str, optional): Filter by entity type code
- `concessionTypeCode` (str, optional): Filter by concession type code

---

## Development

> *This doc section is for developers contributing to the project.*

### Testing

#### Docker

Build the docker image

```shell
 docker build -f test/Dockerfile -t abn-lookup .
```

Run the tests with

```shell
docker run \
    -it \
    -v "$PWD":/app \
    abn-lookup:latest \
    bash -c 'pytest -vv test'
```

#### Host Machine

```shell
uv sync --all-groups
. .venv/bin/activate

pytest -vv -s test/
```
