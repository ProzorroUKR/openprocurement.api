.. index:: PlanMilestone

.. _planmilestone:

PlanMilestone
=============

Schema
------

:id:
    uid, auto-generated

:title:
    string, required

    The only possible value is:

    * `Підготовка до проведення процедури`

:description:
    string, min-length is 3

    Default value is:

    * `Узагальнення та аналіз отриманної інформації щодо проведення закупівель товарів, послуг (крім поточного ремонту) в інтересах замовників`

:type:
    string, required

    The only possible value is:

    * `approval`

:dueDate:
    string, :ref:`date`, required

:author:
    :ref:`PlanOrganization` object, required


:status:
    string, default `scheduled`

    Possible values are:

    * `scheduled`
    * `met`
    * `notMet`
    * `invalid`

:documents:
    List of :ref:`document` objects

:dateModified:
    string, :ref:`date`, auto-generated

:dateMet:
    string, :ref:`date`, auto-generated

:owner:
    string, auto-generated