import abc

from ..timeout import TimeoutContext
from .base import BaseMixin


class TimeoutMixin(BaseMixin):
    # -----------
    # Constructor
    # -----------

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        TimeoutContext.initialize(self)

    def timeout(self,
                timeout=None,
                total=None,
                overwrite=False,
                propagate=False):
        """Create a timeout context."""
        return TimeoutContext(self, timeout, total, overwrite, propagate)
