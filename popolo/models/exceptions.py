# -*- coding: utf-8 -*-


class OverlappingIntervalError(Exception):
    """Raised when date intervals overlap

    Attributes:
        overlapping -- the first entity whose date interval overlaps
        message -- the extended description of the error

    """

    def __init__(self, overlapping, message):
        self.overlapping = overlapping
        self.message = message

    def __str__(self):
        return repr(self.message)
