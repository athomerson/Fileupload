
from plone.app.widgets.base import BaseWidget
from plone.app.widgets.base import el_attrib


class FileWidget(BaseWidget):
    """Widget with `file` element."""

    type = el_attrib('type')
    name = el_attrib('name')
    _multiple = el_attrib('multiple')

    def __init__(self, pattern, pattern_options={}, type='file',
                 name=None, multiple=False):
        """
        :param pattern: [required] Pattern name.
        :type pattern: string

        :param pattern_options: Patterns options.
        :type pattern_options: dict

        :param action: `type` attribute of element.
        :type value: string

        :param method: `name` attribute of element.
        :type value: string

        :param enctype: `multiple` attribute of element.
        :type value: bool
        """
        super(FileWidget, self).__init__('input', pattern, pattern_options)
        self.type = type
        self.multiple = multiple
        if name is not None:
            self.name = name

    def _get_multiple(self):
        """Does element allows multiple items to be selected.

        :returns: `True` if allows multiple elements to be selected, otherwise
                  `False`.
        :rtype: bool
        """
        if self._multiple == 'multiple':
            return True
        return False

    def _set_multiple(self, value):
        """Make element accept multiple values.

        :param value: `True` if you want to set element as `multiple`,
                      otherwise `False`
        :type value: bool
        """
        if value:
            self._multiple = 'multiple'
        else:
            self._del_multiple()

    def _del_multiple(self):
        """Remove `multiple` attribute from element."""
        del self._multiple

    multiple = property(_get_multiple, _set_multiple, _del_multiple)
