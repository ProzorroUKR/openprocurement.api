
.. _complaints:


..
    contents:: Table of Contents
   :depth: 2
   :local:

Claims/Complaints Workflow
==========================


Claims
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


Tutorials
~~~~~~~~~

Tender Conditions Claims
""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    claims-tender

Tender Qualification Claims
"""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    claims-award

Tender Pre-qualification Claims
"""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    claim-qualification


Statuses
~~~~~~~~

:draft:
    Initial status

    Complainant can submit claim, upload documents, cancel claim, and re-submit it.

:claim:
    Procuring entity can upload documents and answer to claim.

    Complainant can cancel claim.

:answered:
    Complainant can cancel claim, upload documents, agree or disagree with decision.

:resolved:
    Terminal status

    Claim recognized as resolved.

:cancelled:
    Terminal status

    Claim cancelled by complainant.


Complaints
----------

Before Release 2020-04-19
~~~~~~~~~~~~~~~~~~~~~~~~~

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


Tutorials
~~~~~~~~~

Tender Conditions Complaints
""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-tender

Tender Qualification Complaints
"""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-award

Tender Pre-qualification Complaints
"""""""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-qualification

Statuses
~~~~~~~~

:draft:
    Initial status

    Complainant can upload documents and submit complaint.

:pending:
    Reviewer can upload documents and review complaint.

:accepted:
    Complaint accepted

:satisfied:
    Complaint is the satisfied by reviewer

:stopping:
    Complaint recalled by participant

:stopped:
    Terminal status

    Сomplaint has been discontinued

:mistaken:
    Terminal status

    Complaint was in error

:invalid:
    Terminal status

    Claim recognized as invalid.

:declined:
    Terminal status

    Claim recognized as declined.

:resolved:
    Terminal status

    Complaint recognized as resolved.


After Release 2020-04-19
~~~~~~~~~~~~~~~~~~~~~~~~

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; mistaken; invalid; resolved; declined; stopped;}
        subgraph cluster_complaint {
            pending; satisfied; accepted;
        }
        satisfied -> resolved;
        edge[style=dashed];
        draft -> {pending,mistaken};
        pending -> stopping;
        accepted -> stopping;
        edge[style=bold];
        accepted -> {declined,satisfied,stopped};
        pending -> {accepted,invalid};
        stopping -> {stopped,invalid,declined,satisfied};
    }

Tutorials
~~~~~~~~~

Tender Conditions Complaints
""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-tender-2020-04-19

Tender Qualification Complaints
"""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-award-2020-04-19

Tender Pre-qualification Complaints
"""""""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-qualification-2020-04-19

Tender Cancellation Complaints
""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-cancellation

Statuses
~~~~~~~~

:draft:
    Initial status

    Complainant can upload documents, cancel complaint and submit complaint.

:pending:
    Reviewer can upload documents and review complaint.

:accepted:
    Complaint accepted

:satisfied:
    Complaint is the satisfied by reviewer

:stopping:
    Complaint recalled by participant

:stopped:
    Terminal status

    Сomplaint has been discontinued

:mistaken:
    Terminal status

    Complaint dismissed

:invalid:
    Terminal status

    Claim recognized as invalid.

:declined:
    Terminal status

    Claim recognized as declined.

:resolved:
    Terminal status

    Complaint recognized as resolved.



Roles
-----

:Complaint owner:
    dashed

:Tender owner:
    plain

:AboveThresholdReviewer:
    bold

:Chronograph:
    dotted
