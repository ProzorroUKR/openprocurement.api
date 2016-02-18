from schematics.transforms import Role

def confidential(*field_list):
    """
    Returns a function that operates as a whitelist for the provided list of
    fields.

    A whitelist is a list of fields explicitly named that are allowed.
    """
    def confidential_filter(name, value, seq):
        """
        Implements the behavior of a whitelist by requesting a field be skipped
        whenever it's name is not in the list of fields.

        :param name:
            The field name to inspect.
        :param value:
            The field's value.
        :param seq:
            The list of fields associated with the ``Role``.
        """
        import pdb; pdb.set_trace()  # debug ktarasz
        if seq is not None and len(seq) > 0:
            return name not in seq
        return True
    return Role(confidential_filter, field_list)
