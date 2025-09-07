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


## More Documentation

[Documentation](https://prozorro-api-docs.readthedocs.io/uk/master/)

[Development](https://prozorro-api-docs.readthedocs.io/en/master/developers/index.html)

[Documentation maintenance](https://prozorro-api-docs.readthedocs.io/en/master/developers/projects/cdb/documentation.html)