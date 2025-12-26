.. _cfaua_requests:

REST API специфікації
=====================

Тендер:
-------

* GET:
    `/tenders`

    Отримайте список тендерів

    `/tenders/:tender_id`

    Отримайте тендер по його ідентифікатору (id)

* POST
    `/tenders:tender_id`

    Відредагувати тендер


Документи тендера:
------------------

* GET
    `/tenders/:tender_id/documents/:document_id`

    Читайте документи тендера

    `/tenders/:tender_id/documents`

    Список документів тендера

* PUT
    `/tenders/:tender_id/documents/:document_id`

    Оновлення документів тендера

* POST
    `/tenders/:tender_id/documents`

    Завантаження документів тендера

* PATCH
    `/tenders/:tender_id/documents/:document_id`

    Оновлення документів тендера

Звернення до тендера
--------------------

* GET
    `/tenders/:tender_id/questions/:question_id`

    Отримання звернення

    `/tenders/:tender_id/questions`

    Список питань

* POST
    `/tenders/:tender_id/questions`

    Опублікувати звернення

* PATCH
    `/tenders/:tender_id/questions/:question_id`

    Опублікувати відповідь

Кваліфікації тендера
--------------------

* GET
    `/tenders/:tender_id/qualifications`

    Список кваліфікацій

    `/tenders/:tender_id/qual…tions/:qualification_id`

    Отримання кваліфікацій

* PATCH
    `/tenders/:tender_id/qual…tions/:qualification_id`

    Опублікувати рішення по кваліфікації

Скарги на кваліфікації тендера
------------------------------

* GET
    `/tenders/:tender_id/qualifications/:qualification_id/complaints`

    Список скарг на переможців

    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id`

    Отримання скарги на переможця

* PATCH
    `/tenders/:tender_id/qualifications/:qualification_id/complaints`

    Опублікувати скаргу

Документи по кваліфікаціях тендера
----------------------------------

* PATCH
    `/tenders/:tender_id/qualifications/:qualification_id/documents/:document_id`

    Оновлення документів по кваліфікаціях тендера

* POST

    `/tenders/:tender_id/qualifications/:qualification_id/documents`

    Завантаження документів по кваліфікаціях тендера

* PUT

    `/tenders/:tender_id/qualifications/:qualification_id/documents/:document_id`

    Оновлення документів по кваліфікаціях тендера

* GET
    `/tenders/:tender_id/qualifications/:qualification_id/documents/:document_id`

    Читайте документи по кваліфікаціях тендера

    `/tenders/:tender_id/qualifications/:qualification_id/documents`

    Список документів по кваліфікаціях тендера

Документи до скарг по кваліфікаціяз тендера
-------------------------------------------

* GET
    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents/document_id`

    Читайте документи до скарг на переможців тендера

    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents`

    Список документів до скарг на переможців тендера

* PUT
    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents/:document_id`

    Оновлення документів до скарг на переможців тендера

* POST
    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents`

    Завантаження документів до скарг на переможців тендера

* PATCH
    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents/:document_id`

    Оновлення документів до скарг на переможців тендера

Лоти тендера
------------

* GET
    `/tenders/:tender_id/lots`

    Список лотів

    `/tenders/:tender_id/lots/:lot_id`

    Отримання лота

* PATCH
    `/tenders/:tender_id/lots/:lot_id`

    Оновлення лота

* POST
    `/tenders/:tender_id/lots`

    Додавання лота

* DELETE
    `/tenders/:tender_id/lots/:lot_id`

    Видалення лота

Скасування тендера
------------------

* GET
    `/tenders/:tender_id/cancellations`

    Список об'єктів скасування тендера

    `/tenders/:tender_id/cancellations/:cancellation_id`

    Отримання скасування

* PATCH
    `/tenders/:tender_id/cancellations/:cancellation_id`

    Опублікувати рішення про скасування

* POST
    `/tenders/:tender_id/cancellations`

    Опублікувати скасування

Документи до скасування тендера
-------------------------------

* GET
    `/tenders/:tender_id/cancellations/:cancellation_id/documents/:document_id`

    Читайте документи до скасування тендера

    `/tenders/:tender_id/cancellations/:cancellation_id/documents`

    Список документів до скасування тендера

* POST
    `/tenders/:tender_id/cancellations/:cancellation_id/documents`

    Завантаження документів до скасування тендера

* PATCH
    `/tenders/:tender_id/cancellations/:cancellation_id/documents/:document_id`

    Оновлення документів до скасування тендера

* PUT
    `/tenders/:tender_id/cancellations/:cancellation_id/documents/:document_id`

    Оновлення документів до скасування тендера

Скарги на тендер
----------------

* GET
    `/tenders/:tender_id/complaints`

    Список скарг

    `/tenders/:tender_id/complaints/:complaint_id`

    Отримання скарги

* POST
    `/tenders/:tender_id/complaints`

    Опублікувати скаргу

    `/tenders/:tender_id/complaints/:complaint_id`

    Отримання скарги

* PATCH
    `/tenders/:tender_id/complaints/:complaint_id`

    Опублікуавти рішення по скарзі

Ставки тендера
--------------

* GET
    `/tenders/:tender_id/bids/:bid_id`

    Отримання пропозицій

    `/tenders/:tender_id/bids`

    Список пропозицій

* POST
    `/tenders/:tender_id/bids`

    Реєстрація нової пропозиції

* PATCH
    `/tenders/:tender_id/bids/:bid_id`

    Оновлення пропозиції

* DELETE
    `/tenders/:tender_id/bids/:bid_id`

    Скасування пропозиції

Документи до пропозиції
-----------------------

* GET
    `/tenders/:tender_id/bids/:bid_id/documents/:document_id`

    Читайте документи до пропозиції

    `/tenders/:tender_id/bids/:bid_id/documents`

    Список документів до пропозиції

* POST
    `/tenders/:tender_id/bids/:bid_id/documents`

    Завантаження документів до пропозиції

* PUT
    `/tenders/:tender_id/bids…/documents/:document_id`

    Оновлення документів до пропозиції

* PATCH
    /tenders/:tender_id/bids/:bid_id/documents/:document_id

    Оновлення документів до пропозиції

Документи по критеріях відбору пропозицій
-----------------------------------------

* GET
    `/tenders/:tender_id/bids…_documents/:document_id`

    Читайте документи до пропозиції

    `/tenders/:tender_id/bids/:bid_id/eligibility_documents`

    Список документів до пропозиції

* PATCH
    `/tenders/:tender_id/bids/:bid_id/eligibility_documents/:document_id`

    Оновлення документів до пропозиції

* PUT
    `/tenders/:tender_id/bids/:bid_id/eligibility_documents/:document_id`
                                                                     
    Оновлення документів до пропозиції

* POST
    `/tenders/:tender_id/bids/:bid_id/eligibility_documents`

    Завантаження документів до пропозиції

Фінансові документи до пропозиції
---------------------------------

* GET
    `/tenders/:tender_id/bids…_documents/:document_id`

    Читайте документи до пропозиції

    `tenders/:tender_id/bids…_id/financial_documents`

    Список документів до пропозиції

* POST
    `/tenders/:tender_id/bids/:bid_id/financial_documents`

    Завантаження документів до пропозиції

* PATCH
    `/tenders/:tender_id/bids/:bid_id/financial_documents/:document_id`

    Оновлення документів до пропозиції

* PUT
    `/tenders/:tender_id/bids/:bid_id/financial_documents/:document_id`

    Оновлення документів до пропозиції

Кваліфікаційні документи до пропозиції
--------------------------------------

* GET
    `/tenders/:tender_id/bids/:bid_id/qualification_documents/:document_id`

    Читайте документи до пропозиції

    `/tenders/:tender_id/bids/:bid_id/qualification_documents`

    Список документів до пропозиції

* POST
    `/tenders/:tender_id/bids/:bid_id/qualification_documents`

    Завантаження документів до пропозиції

* PATCH
    `/tenders/:tender_id/bids/:bid_id/qualification_documents/:document_id`
                                                                       
    Оновлення документів до пропозиції

* PUT
    `/tenders/:tender_id/bids/:bid_id/qualification_documents/:document_id`
                                                                       
    Оновлення документів до пропозиції

Переможці тендера
-----------------

* GET
    `/tenders/:tender_id/awards/:award_id`

    Отримання переможця

    `/tenders/:tender_id/awards`

    Список переможців

* PATCH
    `/tenders/:tender_id/awards/:award_id`

    Оновлення переможця

* POST
    `/tenders/:tender_id/awards`

    Прийняти або відхилити додаток пропозиції

Документи до переможця тендера
------------------------------

* GET
    `/tenders/:tender_id/awar…/documents/:document_id`

    Читайте документи до переможця тендера

    `/tenders/:tender_id/awards/:award_id/documents`

    Список документів до переможця тендера

* POST
    `/tenders/:tender_id/awards/:award_id/documents`

    Завантаження документів до переможця тендера

* PUT
    `/tenders/:tender_id/awards/:award_id/documents/:document_id`

    Оновлення документів до переможця тендера

* PATCH
    `/tenders/:tender_id/awards/:award_id/documents/:document_id`

    Оновлення документів до переможця тендера

Скарга на переможця тендера
---------------------------

* GET
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id`

    Отримання скарги на переможця

    `/tenders/:tender_id/awards/:award_id/complaints`

    Список скарг на переможця

* POST
    `/tenders/:tender_id/awards/:award_id/complaints`

    Опублікуавти скаргу на переможця

* PATCH
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id`

    Оновіть скаргу на переможця

Документи до скарги на переможця тендера
----------------------------------------

* GET
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id/documents/:document_id`

    Читайте документи до скарг на переможців тендера

    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id/documents`

    Список документів до скарг на переможців тендера

* POST
    `/tenders/:tender_id/awar…:complaint_id/documents`

    Завантаження документів до скарг на переможців тендера

* PATCH
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id/documents/:document_id`

    Оновлення документів до скарг на переможців тендера

* PUT
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id/documents/:document_id`

    Оновлення документів до скарг на переможців тендера

Аукціон
-------

* GET
    `/tenders/:tender_id/auction`

    Отримати інформацію про аукціон

* POST
    `/tenders/:tender_id/auction`

    Опублікувати результати аукціону

    `/tenders/:tender_id/auction/:auction_lot_id`

    Опублікувати результати аукціону по лоту

* PATCH
    `/tenders/:tender_id/auction`

    Налаштувати URL для доступу до аукціону

    `/tenders/:tender_id/auction/:auction_lot_id`

    Налаштувати URL для доступу до аукціону по лоту

Угода
-----

* GET
    `/tenders/:tender_id/agreements`

    Список угод до переможця

* POST
    `/tenders/:tender_id/agreements`

    Опублікувати угоду до переможця

* PATCH
    `/tenders/:tender_id/agreements/:agreement_id`

    Оновити угоду

Контракт до угоди
-----------------

* GET
    `/tenders/:tender_id/agreements/:agreement_id/contracts/:contract_id`
                                                                     
    Отримання контракту до угоди

    `/tenders/:tender_id/agreements/:agreement_id/contracts`

    Список контрактів до угоди

* PATCH
    `/tenders/:tender_id/agreements/:agreement_id/contracts/:contract_id`

    Оновити контракт до угоди

Документи до угоди
------------------

* GET
    `/tenders/:tender_id/agreements/:agreement_id/documents/:document_id`

    Читайте документи до угоди

    `/tenders/:tender_id/agreements/:agreement_id/documents`

    Список документів до угоди

* POST
    `/tenders/:tender_id/agreements/:agreement_id/documents`

    Завантажте документи до угоди

* PUT
    `/tenders/:tender_id/agreements/:agreement_id/documents/:document_id`

    Оновіть документи до угоди

* PATCH
    `/tenders/:tender_id/agreements/:agreement_id/documents/:document_id`

    Оновіть документи до угоди
