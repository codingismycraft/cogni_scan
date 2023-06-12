# See also
# https://learn.microsoft.com/en-us/cpp/mfc/reference/cdocument-class?view=msvc-170#addview

import abc

class Document(abc.ABC):
    
    _views = None
    _title = None
    
    def __init__(self):
        self._title = "Title not assigned."
        self._views = [] 
    
    def addView(self, view):
        """ Call this function to attach a view to the document.

        Adds the specified view to the list of views associated with the
        document; also sets the view's document pointer to this document. 
        """
        if not self._views:
            self._views = []
        self._views.append(view)
        view.bindDocument(self)
        
    def removeView(self, view):
        """Detaches as view from the document."""
        if self._view:
            self._views.remove(view)

    def setTitle(self, title):
        """Set the document's title."""
        self._title = title

    def getTitle(self):
        """Get the document's title."""
        return self._title

    def updateAllViews(self, sender=None):
        """Call this function after the document has been modified."""
        for view in self._views:
            if view is not sender:
                view.update()
                        
    @abc.abstractmethod
    def clear(self):
        """Delete the document's data without destroying the object."""

    @abc.abstractmethod
    def load(self, **kwargs):
        """Loads the documentDelete the document's data without destroying the object.."""

    @abc.abstractmethod
    def isDirty(self):
        """Determine modification since it was last saved.""" 

    @abc.abstractmethod
    def save(self):
        """Saves the document if modified."""
