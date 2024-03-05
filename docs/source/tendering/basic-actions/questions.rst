
.. _questions:

Asking Questions
================

Submitting Questions
--------------------

Anybody (who provides their identity) can ask questions:

.. http:example:: ../belowthreshold/http/tutorial/ask-question.http
   :code:

Retrieving Questions
--------------------

All appeals for clarifications and appeals for the elimination of violations are automatically published in the electronic procurement system without identification of the person who addressed the customer.

Author of question will be hashed with his `identifier.id` plus `access token` of the procedure.
This gives us a possibility to determine that at the tender level a certain number of questions came from the same author.

Let's look at asked question:

.. http:example:: ../belowthreshold/http/tutorial/list-question.http
   :code:

Answering
=========

Submitting Answers
------------------

Tender creator can answer questions:
 
.. http:example:: ../belowthreshold/http/tutorial/answer-question.http
   :code:
