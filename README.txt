Introduction
============

`collective.widget.fileupload` is a plone.app.widgets widget which lets users
upload multiple files.

Usage
-----

Using the widget is quiet easy::

    >>> from plone.directives import form as directivesform
    >>> from collective.widget.fileupload import FileUploadFieldWidget
    >>> from plone.namedfile.field import NamedFile
    >>> from zope import schema
    >>> from zope.interface import Interface
    >>> 
    >>> class IMySchema(Interface):
    ...     """My schema interface"""
    ...     
    ...     directivesform.widget(files=FileUploadFieldWidget)
    ...     files = schema.List(title=u'Files',
    ...                         value_type=NamedFile())


Limitations
-----------


