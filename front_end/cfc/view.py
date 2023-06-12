"""Exposes the View class.

See also:
https://learn.microsoft.com/en-us/cpp/mfc/reference/cview-class?view=msvc-170
"""

import abc

class View(abc.ABC):
    """Provides the basic functionality for user-defined view classes."""

    _document = None

    def bindDocument(self, document):
        """Binds to the document that holds the correspondig data."""
        self._document = document

    def getDocument(self):
        """Returns the document associated with the view."""
        return self._document

    @abc.abstractmethod
    def update(self):
        """Called to update the view. 

        Needs to be implemented by the client code.
        """
