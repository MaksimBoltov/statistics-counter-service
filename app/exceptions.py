class UniqueViolationException(Exception):
    """Raises when trying to re-create a similar object in the database"""

    def __init__(self, *args, **kwargs):
        pass
