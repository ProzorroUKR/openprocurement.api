
.. include:: defs.hrst

.. index:: Framework
.. _framework:

Framework
=========

Схема
-----

:title:
   рядок, багатомовний

   Назва кваліфікації, яка відображається у списках.

:description:
   рядок, багатомовний

   Детальний опис кваліфікації.

:prettyID:
   рядок, генерується автоматично, лише для читання

   Ідентифікатор кваліфікації.


:procuringEntity:
   :ref:`ProcuringEntity`, обов’язково

   Замовник (організація, що створює кваліфікацію).

   Якщо :code:`frameworkType` має значення :code:`electronicCatalogue`, тоді можливі значення :code:`ProcuringEntity.kind` обмежені :code:`[‘central’]`.


:frameworkType:
    рядок

    :`electronicCatalogue`:
        Кваліфікація для процесу відбору до електронного каталогу


:date:
    рядок, :ref:`date`, генерується автоматично


:documents:
   Список об’єктів :ref:`document`

   |ocdsDescription| Всі документи та додатки пов’язані з кваліфікацією.

:enquiryPeriod:
   :ref:`period`, лише для читання, генерується автоматично

   Період, коли дозволено подавати звернення.

   |ocdsDescription| Період, коли можна зробити уточнення та отримати відповіді на них.

   Якщо :code:`frameworkType` має значення :code:`electronicCatalogue`, тоді постачальник не може подавати заявки в цей період.

:dateModified:
    рядок, :ref:`date`, генерується автоматично

:owner:
    рядок, генерується автоматично

:period:
   :ref:`period`, лише для читання, генерується автоматично

   Період, в який постачальники можуть додавати заявки до кваліфікації.

   |ocdsDescription| Період, коли кваліфікація відкрита для подачі заявки.

:qualificationPeriod:
   :ref:`period`, обов’язково

   Період, коли приймаються рішення щодо заявок постачальників. Повинна бути вказана хоча б `endDate` дата.

    Якщо :code:`frameworkType` має значення :code:`electronicCatalogue`, тоді :code:`qualificationPeriod` має бути від 365 до 1461 днів


:status:
   рядок

   :`draft`:
      Якщо :code:`frameworkType` має значення :code:`electronicCatalogue`, тоді в цьому статусі можна змінювати будь-які поля кваліфікації.
   :`active`:
      Якщо :code:`frameworkType` має значення :code:`electronicCatalogue`, тоді в цьому статусі можна змінювати лише поля :code:`contactPoint`, :code:`qualificationPeriod.endDate`, :code:`description` та :code:`documents`
   :`unsuccessful`:
      Завершальний статус. Кваліфікація може перейти в статус `unsuccessful` якщо за перші 20 повних робочих днів до неї не було створенно жодної заявки.
   :`complete`:
      Завершена кваліфікація.

   Статус кваліфікації.


:classification:
   :ref:`Classification`, обов'язково

   |ocdsDescription| Початкова класифікація кваліфікації.

   Якщо :code:`frameworkType` має значення :code:`electronicCatalogue`, тоді `classification.scheme` має бути `ДК021`. `classification.id` повинно бути дійсним ДК021 кодом.


:additionalClassification:
   Список об'єктів :ref:`Classification`.

   |ocdsDescription| Массив додаткових класифікацій кваліфікації.

:changes:
   Список об’єктів :ref:`FrameworkChange`

   Список всіх змін під час активного відбору.


:revisions:
   Список об’єктів :ref:`revision`, генерується автоматично, лише для читання

   Зміни властивостей об’єктів кваліфікації.
