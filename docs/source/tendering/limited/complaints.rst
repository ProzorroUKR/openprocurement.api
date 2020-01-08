..
    contents:: Table of Contents
   :depth: 2
   :local:

.. _limited_complaint_workflow:

Complaint Workflow
==================

For more detailed information read `Complaints <http://openprocurement.org/en/complaints.html>`_.

Tender Award Complaints
-----------------------

.. graphviz::

    digraph G {
        rankdir=LR;
        {rank=same; mistaken; invalid; resolved; declined; stopped; cancelled;}
        subgraph cluster_complaint {
            label = "complaint";
            pending; accepted; stopping; satisfied;
        }
        satisfied -> resolved;
        edge[style=dashed];
        draft -> {pending,cancelled,mistaken};
        {pending,accepted} -> stopping;
        edge[style=bold];
        pending -> {accepted,invalid,stopped};
        stopping -> {stopped,invalid,declined,satisfied};
        accepted -> {declined,satisfied,stopped};
    }

.. toctree::
    :maxdepth: 1

    complaints-award

Tender Cancellation Complaints (only for negotiation and negotiation.quick)
---------------------------------------------------------------------------

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
        draft -> pending;
        edge[style=bold];
        accepted -> {declined,satisfied,stopped};
        pending -> {accepted,invalid,stopped};
        {pending} -> mistaken;
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
    Complainant can cancel claim, upload documents, accept solution or escalate claim to complaint.

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
