.. _cdb_code:

Python linter and code formatters
=================================

Для автоматичної перевірки відповідності стилі і форматування коду,
включіть `pre-commit hooks <https://pre-commit.com>`_



1. Встановіть його, якщо ще не маєте:

.. code-block:: bash

   pip install pre-commit


2. В корені проекту виконайте команду активації хука:

.. code-block:: bash

   pre-commit install

Це все, далі під час коміту змін необхідні перевірки та форматування буде виконано.

Десь ось так:

.. code-block:: bash

    $ git commit -m "ruff code checker"
    isort....................................................................Passed
    ruff.....................................................................Passed
    ruff-format..............................................................Passed
    [ruff b65bb9744] ruff code checker
     5 files changed, 94 insertions(+), 20 deletions(-)
     create mode 100644 .pre-commit-config.yaml
     create mode 100644 ruff.toml