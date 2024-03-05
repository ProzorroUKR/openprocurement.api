.. _cfaua_questions:

Asking Questions
================

Submitting Questions
--------------------

Anybody (who provides their identity) can ask questions:

.. http:example:: tutorial/ask-question.http
   :code:

Retrieving Questions
--------------------

Author of question will be hashed with his `identifier.id` plus `access token` of the procedure:

.. http:example:: tutorial/list-question.http
   :code:

Submitting Answers
------------------

Tender creator can answer questions:
 
.. http:example:: tutorial/answer-question.http
   :code:
