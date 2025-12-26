
.. include:: defs.hrst

.. index:: Submission
.. _submission:

Submission
==========

Schema
------

:tenderers:
   Список об'єктів :ref:`BusinessOrganization`

:frameworkID:
   рядок

   Ідентифікатор кваліфікації.

:qualificationID:
   рядок, генерується автоматично, лише для читання

   Ідентифікатор рішення по заявці.

:submissionType:
    рядок, генерується автоматично з моделі кваліфікації з ідантифікатором frameworkID

    :`electronicCatalogue`:
        Заявка для процесу відбору до електронного каталогу

:date:
    рядок, :ref:`date`, генерується автоматично

:documents:
   Список об'єктів :ref:`document`

   |ocdsDescription| Всі документи та додатки пов’язані з заявкою.

:datePublished:
    рядок, :ref:`date`, генерується автоматично

:dateModified:
    рядок, :ref:`date`, генерується автоматично

:owner:
    рядок, генерується автоматично

:status:
   рядок

   :`draft`:
      Якщо :code:`submissionType` має значення :code:`electronicCatalogue`, тоді в цьому статусі можуть бути змінене будь-яке поле(окрім :code:`qualificationID`).
   :`active`:
      Якщо :code:`submissionType` має значення :code:`electronicCatalogue`, цьому статусі сторюється рішення по кваліфікації і встановлюється поле :code:`qualificationID`.
   :`deleted`:
      Термінальний статус.
   :`complete`:
      Завершення заявки.

   Статус заявки.

:revisions:
   Список об'єктів :ref:`revision`, генерується автоматично

   Зміни властивостей об’єктів заявки.
