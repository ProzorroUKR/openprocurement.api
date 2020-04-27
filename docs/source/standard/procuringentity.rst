
.. include:: defs.hrst

.. index:: ProcuringEntity

.. _ProcuringEntity:

ProcuringEntity
===============

Schema
------

:name:
    string, multilingual

    |ocdsDescription|
    The common name of the organization.

:identifier:
    :ref:`Identifier`

    |ocdsDescription|
    The primary identifier for this organization.

:additionalIdentifiers:
    List of :ref:`identifier` objects

:address:
    :ref:`Address`, required

:contactPoint:
    :ref:`ContactPoint`, required

:kind:
    string
    
    Type of procuring entity

    Possible values:
        - ``authority`` - Public authority, local government or law enforcement agency
        - ``central`` - Legal entity that conducts procurement in the interests of the customers (CPB)
        - ``defense`` - Procuring entity that conducts procurement for the defense needs
        - ``general`` - Legal person providing the needs of the state or territorial community
        - ``other`` -  State or utility company that is not regarded as procuring entity
        - ``social`` - Social insurance authority
        - ``special`` - A legal entity that operates in one or more specific business areas
