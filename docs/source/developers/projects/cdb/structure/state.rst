.. _cdb_context:

State
=====
Класи що визначають бізнес логіку проведеня тендерів/планів/контрактів  etc,
фактично реалізуючи BPMN та sequence діаграми надані БА.
StateClasses можуть управляти/визначати модель даних, необхідний для кожної дії,
та серіалізатор відповіді (напр. повний або неповний)

Приклад:

.. sourcecode:: python

    class ObjectState(BaseState):
        should_do_something: bool = False
        something_to_return: int = 42

        def on_patch(self, before, after):
            self.do_something()

        def do_something(self):
            if self.should_do_something:
                # do something
                return self.something_to_return


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