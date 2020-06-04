.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: PlanOrganization

.. _PlanOrganization:


PlanOrganization
================

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

:address:
    :ref:`Address`, required

:kind:
    string

    Possible values:
        - ``authority`` - Public authority, local government or law enforcement agency
        - ``central`` - Legal entity that conducts procurement in the interests of the customers (CPB)
        - ``defense`` - Procuring entity that conducts procurement for the defense needs
        - ``general`` - Legal person providing the needs of the state or territorial community
        - ``other`` -  State or utility company that is not regarded as procuring entity
        - ``social`` - Social insurance authority
        - ``special`` - A legal entity that operates in one or more specific business areas