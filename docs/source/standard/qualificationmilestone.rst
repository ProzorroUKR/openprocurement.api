.. index:: QualificationMilestone


.. _qualificationmilestone:


QualificationMilestone
======================


Schema
------



:id:
    uid, auto-generated

:code:
    string, required

    Possible values are:

    * ``24h`` (Used by :ref:`24hours`)
    * ``alp`` (Used to indicate an abnormally low price bid. Find an example on :ref:`openua_tutorial`)


:description:
    string

    In case of ``alp`` code, contains at least one line of the following::

        найбільш економічно вигідна пропозиція є меншою на 40 або більше відсотків 
        від середньоарифметичного значення ціни/приведеної ціни тендерних пропозицій
        інших учасників на початковому етапі аукціону
        
        найбільш економічно вигідна пропозиція є меншою на 30 або більше відсотків 
        від наступної ціни/приведеної ціни тендерної пропозиції за результатами 
        проведеного електронного аукціону


:dueDate:
    string, :ref:`date`, auto-generated


:date:
    string, :ref:`date`, auto-generated
