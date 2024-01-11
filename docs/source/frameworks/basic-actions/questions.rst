Questions
=========

Framework
---------

Let's take a look at activated framework:

.. http:example:: http/questions/get-framework.http
   :code:

Enquiries
---------

The participant has the opportunity to contact the administrator through the electronic procurement system regarding the review of the requirements for the participant, specified in the announcement of qualification for the electronic catalog within ten working days from the day of its publication.

During enquiry period, interested parties can ask questions:

.. http:example:: http/questions/ask-question.http
   :code:

Procuring entity can answer them:

.. http:example:: http/questions/answer-question.http
   :code:

It is allowed to answer the question during the whole `enquiryPeriod` and between `enquiryPeriod.endDate` and `enquiryPeriod.clarificationUntil`.
In case procuring entity is answering question after `enquiryPeriod.clarificationUntil`, the error will be raised:

.. http:example:: http/questions/answer-question-after-clarifications-until.http
   :code:

Only procuring entity has permission to answer the questions:

.. http:example:: http/questions/answer-question-invalid.http
   :code:

To retrieve the questions list:

.. http:example:: http/questions/list-questions.http
   :code:

To retrieve the individual answer:

.. http:example:: http/questions/get-answer.http
   :code:

The presence of a question does not block the transition of the qualification announcement to the next status.

The presence or absence of an answer to the question does not block the transition of the qualification announcement to the next status.

The period during which the participant can apply to the administrator through the electronic procurement system to review the requirements for the participant: the date of publication of the announcement + 10 working days.

It is forbidden to ask or answer question outside the enquiry period:

.. http:example:: http/questions/ask-question-invalid.http
   :code:
