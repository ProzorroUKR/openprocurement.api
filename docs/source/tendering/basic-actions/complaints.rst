
.. _complaints:


..
    contents:: Table of Contents
   :depth: 2
   :local:

Схема роботи скарг/вимог
========================


Вимоги
------

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same;resolved; cancelled}
        subgraph cluster_claim {
            claim; answered;
        }
        claim -> answered;
        edge[style=dashed];
        draft -> claim;
        answered -> resolved;
        {draft,claim,answered} -> cancelled;
    }


Туторіали
~~~~~~~~~

Вимоги на умови закупівлі
"""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    claims-tender

Вимоги на кваліфікацію
""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    claims-award

Вимоги на пре-кваліфікацію
""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    claim-qualification


Статуси
~~~~~~~

:draft:
    Початковий статус

    На цьому етапі скаржник може подати вимогу, завантажити документи, відкликати вимогу та подати її знову.

:claim:
    Замовник може завантажити документи та відповісти на вимогу.

    Скаржник може відкликати вимогу.

:answered:
    Скаржник може відкликати вимогу, завантажити документи, згодитись або не згодитись з вирішенням.

:resolved:
    Кінцевий статус

    Вимогу визнано вирішеною.

:cancelled:
    Кінцевий статус

    Вимогу відкликано скаржником.


Скарги
------

До релізу 2020-04-19
~~~~~~~~~~~~~~~~~~~~

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; invalid; resolved; declined; stopped; mistaken;}
        subgraph cluster_complaint {
            pending; satisfied; accepted;
        }
        satisfied -> resolved;
        edge[style=dashed];
        draft -> pending;
        pending -> stopping;
        accepted -> stopping;
        edge[style=bold];
        accepted -> {declined,satisfied,stopped};
        pending -> {accepted,invalid,stopped,mistaken};
        stopping -> {stopped,invalid,declined,satisfied,mistaken};
    }


Туторіали
~~~~~~~~~

Скарги на умови закупівлі
"""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-tender

Скарги на кваліфікацію
""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-award

Скарги на пре-кваліфікацію
""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-qualification

Статуси
~~~~~~~

:draft:
    Початковий статус

    Скаржник може завантажити документи та подати скаргу.

:pending:
    Орган оскарження може завантажувати документи та розглядати скарги.

:accepted:
    Скарга прийнята до розгляду

:satisfied:
    Скарга задоволена АМКУ

:stopping:
    Скарга відкликана участником

:stopped:
    Кінцевий статус

    Розгляд по скарзі припинено

:mistaken:
    Кінцевий статус

    Скарга була помилково направлена(

:invalid:
    Кінцевий статус

    Вимогу визнано недійсною.

:declined:
    Кінцевий статус

    Вимогу визнано відхиленою.

:resolved:
    Кінцевий статус

    Скаргу визнано вирішеною.


Після релізу 2020-04-19
~~~~~~~~~~~~~~~~~~~~~~~

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; mistaken; invalid; resolved; declined; stopped;}
        subgraph cluster_complaint {
            pending; satisfied; accepted;
        }
        satisfied -> resolved;
        edge[style=dotted];
        draft -> pending;
        edge[style=dashed];
        draft -> mistaken;
        edge[style=bold];
        accepted -> {declined,satisfied,stopped};
        pending -> {accepted,invalid};
    }

Туторіали
~~~~~~~~~

Скарги на умови закупівлі
"""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-tender-2020-04-19

Скарги на кваліфікацію
""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-award-2020-04-19

Скарги на пре-кваліфікацію
""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-qualification-2020-04-19

Скарги на скасування закупівлі
""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-cancellation

Статуси
~~~~~~~

:draft:
    Початковий статус

    Скаржник може завантажити документи, відхилити або подати скаргу.

:pending:
    Орган оскарження може завантажувати документи та розглядати скарги.

:accepted:
    Скарга прийнята до розгляду

:satisfied:
    Скарга задоволена АМКУ

:stopped:
    Кінцевий статус

    Розгляд по скарзі припинено

:mistaken:
    Кінцевий статус

    Скарга скасована

:invalid:
    Кінцевий статус

    Вимогу визнано недійсною.

:declined:
    Кінцевий статус

    Вимогу визнано відхиленою.

:resolved:
    Кінцевий статус

    Скаргу визнано вирішеною.



Ролі
----

:Complaint owner:
    пунктирна лінія

:Tender owner:
    звичайна лінія

:AboveThresholdReviewer:
    жирна лінія

:Chronograph:
    лінія з крапками
