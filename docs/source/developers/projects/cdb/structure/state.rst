.. _cdb_state_classes:

State
=====
Класи що визначають бізнес логіку проведеня тендерів/планів/контрактів  etc, фактично реалізуючи BPMN та sequence діаграми надані БА. StateClasses можуть управляти/визначати модель даних, необхідний для кожної дії, та серіалізатор відповіді (напр. повний або неповний)

Приклад базового State класу:

.. sourcecode:: python

    class BaseState:
        def __init__(self, request):
            self.request = request

        def status_up(self, before, after, data):
            assert before != after, "Statuses must be different"

        def on_post(self, data):
            self.always(data)

        def on_patch(self, before, after):
            if "status" in after and before.get("status") != after["status"]:
                self.status_up(before.get("status"), after["status"], after)
            self.always(after)

        def always(self, data):  # post or patch
            pass


Приклад:

.. sourcecode:: python

    class ObjectState(BaseState):
        should_do_something: bool = False
        something_to_return: int = 42

        def on_patch(self, before, after):
            self.do_something()

        def status_up(self, before, after, data):
            super().status_up(before, after, data)
            if after == "active":
                self.do_something_else(data)

        def do_something(self):
            if self.should_do_something:
                # do something
                return self.something_to_return

        def do_something_else(self, data):
            # do something else
            pass


При реалізації похідних стейт класів, наприклад для різних типів тендерів, класи що наслідуються не мають містити реалізації бізнес логіки а мають конфігурувати `core` класи (у випадках коли спеціфічна функціональність не реалізована за допомогою конфігурації об'єкта)

Приклад:

.. sourcecode:: python

    class BelowThresholdObjectState(ObjectState):
        should_do_something: bool = True


    class RequestForProposalObjectState(ObjectState):
        should_do_something: bool = True
        something_to_return: int = 10

.. admonition:: TODO

   Текст