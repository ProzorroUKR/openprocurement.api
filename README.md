# Prozorro CDB Api (openprocurement.api)

## Installation

```
docker-compose build
docker-compose up
```

## Pre-commit

To install `pre-commit` simply run inside the shell:

```bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

`pre-commit` is very useful to check your code before publishing it.
It's configured using `.pre-commit-config.yaml` file.

You can read more about pre-commit here: https://pre-commit.com/


## Run tests

1. Build docker container
    ```
    docker compose build
    ```

2. Run tests
    ```
    docker compose run --rm api pytest src/openprocurement/tender/core -x -vvv
    ```
   
## Docs
   
   1. Update *.http files
      ```
      docker compose run --rm api pytest docs/tests -x -vvv
      ```
  
   2. Generate docs
      ```
      docker compose run --rm api sh -c "cd docs && make html"
      ```
      See docs/build/html for the built doc files
    
   3. [See more](https://prozorro-api-docs.readthedocs.io/uk/master/developers/projects/cdb/documentation.html) 


## Manage dependencies

### Sync your local virtual env with project requirements

Sync explicitly
```shell
uv sync --frozen
```

Or run any command with `--frozen` option and `.venv` will be synced automatically.
```commandline
uv run --frozen pylint .
```


### Manage requirement version

To add a requirement
```shell
uv add httpx
```
or with a constraint
```shell
uv add "aiohttp>=3.12,<4"
```
or
```shell
uv add aiohttp~=3.12
```

To add `dev` requirements
```shell
uv add pytest-aiohttp~=1.0  --group=dev
```

To add/update requirement with a github source
```shell
uv add git+https://github.com/ProzorroUKR/standards.git --rev 1.0.207
```
or by hash itself (tag version also adds hash to the lock file, so I prefer the option above)
```shell
uv add git+https://github.com/ProzorroUKR/standards.git --rev 06f4339cf69bddab93a830b387704be5c5ec9d7b
```


### Manage lock versions

To update all package versions
```shell
uv lock --upgrade
```

To update only one package
```shell
uv lock --upgrade-package pymongo==4.14.1
```
```commandline
Resolved 133 packages in 451ms
Updated pymongo v4.13.1 -> v4.14.1
```

## More Documentation

[Documentation](https://prozorro-api-docs.readthedocs.io/uk/master/)

[Development](https://prozorro-api-docs.readthedocs.io/en/master/developers/index.html)

[Documentation maintenance](https://prozorro-api-docs.readthedocs.io/en/master/developers/projects/cdb/documentation.html)