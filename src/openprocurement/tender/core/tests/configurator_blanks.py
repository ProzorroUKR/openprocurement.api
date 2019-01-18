
def reverse_awarding_criteria_check(self):
    self.assertEqual(self.configurator_class.reverse_awarding_criteria,
                     self.reverse_awarding_criteria)


def awarding_criteria_key(self):
    self.assertEqual(getattr(self.configurator_class, 'awarding_criteria_key', 'not yet implemented'),
                     self.awarding_criteria_key)


def configurator_model(self):
    self.assertEqual(self.configurator_class.model, self.configurator_model)
