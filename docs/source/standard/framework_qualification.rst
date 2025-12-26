
.. include:: defs.hrst

.. index:: FrameworkQualification
.. _framework_qualification:

Qualification
=============

Схема
-----

:frameworkID:
   рядок, генерується автоматично, лише для читання

   Ідентифікатор кваліфікації.

:submissionID:
   рядок, генерується автоматично, лише для читання

   Ідентифікатор заявки.

:qualificationType:
    рядок, генерується автоматично, лише для читання

    :`electronicCatalogue`:
        Рішення по заявці для процесу відбору до електронного каталогу

:date:
    рядок, :ref:`date`, генерується автоматично

:documents:
   Список об’єктів :ref:`document`

   |ocdsDescription| Всі документи та додатки пов’язані з рішенням по заявці.

:dateModified:
    рядок, :ref:`date`, генерується автоматично

:status:
   рядок

   :`pending`:
      Якщо :code:`qualificationType` має значення :code:`electronicCatalogue`, тоді в цьому статусі можуть бути завантажені документи та змінений статус.
   :`active`:
      Якщо :code:`qualificationType` має значення :code:`electronicCatalogue`, тоді в цьому статусі будь-яке поле может бути змінене.
   :`unsuccessful`:
      Термінальний статус.

   Статус рішення по зявці.

:revisions:
   Список об’єктів :ref:`revision`, генерується автоматично, лише для читання

   Зміни властивостей об’єктів рішення по заявці.
