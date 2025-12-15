# abn-lookup
A python client to interact with ABN Lookup services

## Usage

### CLI

```python
ABN_LOOKUP_GUID="XXX" ./abn_lookup/lookup.py \
    --name "Some Business Name" \
    --state "VIC" \
    --limit 5
```

## Development

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