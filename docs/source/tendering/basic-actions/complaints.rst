
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

Tender Award Claims
"""""""""""""""""""

.. toctree::
    :maxdepth: 1

    claims-award

Tender Qualification Claims
"""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    claim-qualification


Complaints
----------

Before Release 2020-04-19
~~~~~~~~~~~~~~~~~~~~~~~~~

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; mistaken; invalid; resolved; declined; stopped}
        subgraph cluster_complaint {
            label = "complaint";
            pending; satisfied; accepted; stopping;
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
        pending -> {accepted,invalid,stopped};
        stopping -> {stopped,invalid,declined,satisfied};
    }

Tutorials
~~~~~~~~~

Tender Conditions Complaints
""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-tender

Tender Award Complaints
"""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-award

Tender Qualification Complaints
"""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-qualification

Tender Cancellation Complaints
""""""""""""""""""""""""""""""

.. toctree::
    :maxdepth: 1

    complaints-cancellation


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

Statuses
--------

:draft:
    Initial status

    Complainant can submit claim, upload documents, cancel claim, and re-submit it.

:claim:
    Procuring entity can upload documents and answer to claim.

    Complainant can cancel claim.

:answered:
    Complainant can cancel claim, upload documents, agree or disagree with decision.

:pending:
    Reviewer can upload documents and review complaint.

    Complainant can cancel claim.

:invalid:
    Terminal status

    Claim recognized as invalid.

:declined:
    Terminal status

    Claim recognized as declined.

:resolved:
    Terminal status

    Claim recognized as resolved.

:cancelled:
    Terminal status

    Claim cancelled by complainant.

:ignored:
    Terminal status

    Claim ignored by procuring entity.
