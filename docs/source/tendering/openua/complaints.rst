..
    contents:: Table of Contents
   :depth: 2
   :local:

.. _openua_complaint_workflow:

Complaint Workflow
==================

For more detailed information read `Complaints <http://openprocurement.org/en/complaints.html>`_.

Tender Conditions Claims/Complaints
-----------------------------------

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; mistaken; invalid; resolved; declined; stopped; cancelled;}
        subgraph cluster_claim {
            label = "claim";
            claim; answered;
        }
        subgraph cluster_complaint {
            label = "complaint";
            pending; satisfied; accepted; stopping;
        }
        claim -> answered;
        satisfied -> resolved;
        edge[style=dashed];
        answered -> {pending,resolved};
        draft -> {claim,pending,mistaken};
        claim -> pending;
        {draft,claim,answered} -> cancelled;
        pending -> stopping;
        accepted -> stopping;
        edge[style=bold];
        accepted -> {declined,satisfied,stopped};
        pending -> {accepted,invalid,stopped};
        stopping -> {stopped,invalid,declined,satisfied};
        edge[label="auction" style=dotted];
        answered -> {invalid,declined,resolved};
    }


Tender Conditions Claims/Complaints (After Release 2020-04-19)
--------------------------------------------------------------

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; mistaken; invalid; resolved; declined; stopped; cancelled;}
        subgraph cluster_claim {
            label = "claim";
            claim; answered;
        }
        subgraph cluster_complaint {
            label = "complaint";
            pending; satisfied; accepted; stopping;
        }
        claim -> answered;
        satisfied -> resolved;
        edge[style=dashed];
        draft -> {claim,pending, mistaken};
        {draft,claim,answered} -> cancelled;
        pending -> stopping;
        accepted -> stopping;
        edge[style=bold];
        accepted -> {declined,satisfied,stopped};
        pending -> {accepted,invalid,stopped};
        stopping -> {stopped,invalid,declined,satisfied};
        edge[label="auction" style=dotted];
        answered -> {invalid,declined,resolved};
    }

.. toctree::
    :maxdepth: 1

    complaints-tender

Tender Award Claims/Complaints
------------------------------

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; mistaken; invalid; resolved; declined; stopped; cancelled;}
        subgraph cluster_complaint {
            label = "complaint";
            pending; accepted; stopping; satisfied;
        }
        subgraph cluster_claim {
            label = "claim";
            claim; answered;
        }
        claim -> answered;
        satisfied -> resolved;
        edge[style=dashed];
        draft -> {claim,pending,mistaken};
        {draft,claim,answered} -> cancelled;
        pending -> stopping;
        accepted -> stopping;
        edge[style=bold];
        pending -> {accepted,invalid,stopped};
        stopping -> {stopped,invalid,declined,satisfied};
        accepted -> {declined,satisfied,stopped};
    }

.. toctree::
    :maxdepth: 1

    complaints-award

Tender Cancellation Complaints
------------------------------

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; mistaken; invalid; resolved; declined; stopped;}
        subgraph cluster_complaint {
            label = "complaint";
            pending; satisfied; accepted;
        }
        satisfied -> resolved;
        edge[style=dashed];
        draft -> {pending, mistaken};
        edge[style=bold];
        accepted -> {declined,satisfied,stopped};
        pending -> {accepted,invalid,stopped};
    }

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
    Complainant can cancel claim, upload documents or accept solution.

:pending:
    Reviewer can upload documents and review complaint.

    Complainant can cancel claim.

:invalid:
    Terminal status

    Complaint recognized as invalid.

:declined:
    Terminal status

    Complaint recognized as declined.

:resolved:
    Terminal status

    Complaint recognized as resolved.

:cancelled:
    Terminal status

    Complaint cancelled by complainant.
