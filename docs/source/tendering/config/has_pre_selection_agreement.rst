.. _has_pre_selection_agreement:

hasPreSelectionAgreement
========================

Field `hasPreSelectionAgreement` is a boolean field that indicates whether the tender has pre-selection procedure and has to be connected to agreement.

Possible values for `hasPreSelectionAgreement` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/has-pre-selection-agreement-values.csv
   :header-rows: 1

hasPreSelectionAgreement is `true`
----------------------------------

Example tutorials:

Standard rules:
    * :ref:`competitiveordering` → :ref:`competitiveordering_tutorial`
    * :ref:`requestforproposal` → :ref:`requestforproposal_tutorial`

Special rules:
    * :ref:`cfaselectionua` → :ref:`cfaselection_tutorial`
    * :ref:`pricequotation` → :ref:`pricequotation_tutorial`
