
.. include:: defs.hrst

.. index:: Item, Parameter, Classification, CPV, Unit

.. _Item:

Item
====

Schema
------

:id:
    string, auto-generated

:description:
    string, multilingual, required

    |ocdsDescription|
    A description of the goods, services to be provided.

:classification:
    :ref:`Classification`

    |ocdsDescription|
    The primary classification for the item. See the
    itemClassificationScheme to identify preferred classification lists,
    including CPV and GSIN.

    It is mandatory for `classification.scheme` to be `CPV` or `ДК021`. The
    `classification.id` should be valid CPV or ДК021 code.

:additionalClassifications:
    List of :ref:`Classification` objects

    |ocdsDescription|
    An array of additional classifications for the item. See the
    itemClassificationScheme codelist for common options to use in OCDS. 
    This may also be used to present codes from an internal classification
    scheme.

    Item wich classification.id starts with 336 and contains
    additionalClassification objects have to contain no more than one
    additionalClassifications with scheme=INN.

    Item with classification.id=33600000-6 have to contain exactly one
    additionalClassifications with scheme=INN.

    It is mandatory to have at least one item with `ДКПП` as `scheme`.

    Validation depends on:

        * :ref:`NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM` constant
        * :ref:`CPV_336_INN_FROM` constant (for :ref:`Tender` :ref:`Item`)

:unit:
    :ref:`Unit`

    |ocdsDescription| 
    Description of the unit which the good comes in e.g.  hours, kilograms. 
    Made up of a unit name, and the value of a single unit.

:quantity:
    integer

    |ocdsDescription|
    The number of units required

    Absent in :ref:`esco`

:deliveryDate:
    :ref:`Period`

    Period during which the item should be delivered.

    Absent in :ref:`esco`

:deliveryAddress:
    :ref:`Address`

    Address, where the item should be delivered.

:deliveryLocation:
    dictionary

    Geographical coordinates of delivery location. Element consist of the following items:

    :latitude:
        string, required
    :longitude:
        string, required
    :elevation:
        string, optional, usually not used

    `deliveryLocation` usually takes precedence over `deliveryAddress` if both are present.

:relatedLot:
    string

    Id of related :ref:`lot`.

Additionally in :ref:`pricequotation`:

:profile:
    string, required

    ID for related profile


Additional fields for :ref:`econtracting`:

:attributes:
    List of :ref:`ItemAttribute`


.. _BidItem:

BidItem
=======

Schema
------

:id:
    string, auto-generated

:description:
    string, multilingual, required

    |ocdsDescription|
    A description of the goods, services to be provided.

:unit:
    :ref:`Unit`

    |ocdsDescription|
    Description of the unit which the good comes in e.g.  hours, kilograms.
    Made up of a unit name, and the value of a single unit.

:quantity:
    integer

    |ocdsDescription|
    The number of units required

:relatedLot:
    string

    Id of related :ref:`lot`.

Additionally in :ref:`belowthreshold` :ref:`openua`, :ref:`openeu`, :ref:`open`, :ref:`competitiveordering`, :ref:`esco` and :ref:`competitivedialogue`: :ref:`pricequotation`:

:product:
    string, required

    ID for related product from catalogue


.. _Classification:

Classification
==============

Schema
------

:scheme:
    string

    |ocdsDescription|
    A classification should be drawn from an existing scheme or list of
    codes.  This field is used to indicate the scheme/codelist from which
    the classification is drawn.  For line item classifications, this value
    should represent a known Item Classification Scheme wherever possible.

:id:
    string

    |ocdsDescription|
    The classification code drawn from the selected scheme.

:description:
    string

    |ocdsDescription|
    A textual description or title for the code.

:uri:
    uri

    |ocdsDescription|
    A URI to identify the code. In the event individual URIs are not
    available for items in the identifier scheme this value should be left
    blank.

    Regular expression for this field: ``^https?://\S+$``

.. _Unit:

Unit
====

Schema
------

:code:
    string, required

    UN/CEFACT Recommendation 20 unit code.

:name:
    string

    |ocdsDescription|
    Name of the unit

Additionally in :ref:`limited`:

:value:
    :ref:`Value`

    Price per unit.
