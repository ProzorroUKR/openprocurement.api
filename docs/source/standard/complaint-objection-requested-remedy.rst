
.. include:: defs.hrst

.. index:: ComplaintObjectionRequestedRemedy, dispute

.. _complaint-objection-requested-remedy:

ComplaintObjectionRequestedRemedy
=================================

Schema
------

:id:
    uid, auto-generated

    Id of the requested remedy

:type:
    string, required

    Type of requested remedy.
    Possible values are:

    * `set_aside`
    * `change_tender_documentation`
    * `provide_clarification`
    * `tender_cancellation`
    * `set_aside_reject`
    * `set_aside_qualification`
    * `set_aside_award`
    * `set_aside_others`

:description:
    string, required

    Description of the requested remedy
