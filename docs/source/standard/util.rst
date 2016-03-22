.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Period, startDate, endDate
.. _period:

Period
======

Schema
------

:startDate:
    string, :ref:`date`

    |ocdsDescription|
    The start date for the period.

:endDate:
    string, required, :ref:`date`

    |ocdsDescription|
    The end date for the period.

`startDate` should always precede `endDate`.


.. index:: Address, City, Street, Country

.. _Address:

Address
=======

Schema
------

:streetAddress:
    string, required
    
    |ocdsDescription|
    The street address. For example, 1600 Amphitheatre Pkwy.
    
:locality:
    string, required
    
    |ocdsDescription|
    The locality. For example, Mountain View.
    
:region:
    string, required
    
    |ocdsDescription|
    The region. For example, CA.
    
:postalCode:
    string, required
    
    |ocdsDescription|
    The postal code. For example, 94043.
    
:countryName:
    string, required
    
    |ocdsDescription|
    The country name. For example, United States.

.. _Date:

Date
====

Date/time in :ref:`date-format`.
