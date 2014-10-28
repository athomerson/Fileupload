from collective.widget.fileupload.interfaces import IFileUploadWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataManager, NO_VALUE, IAddForm
from zope.component import adapts
from zope.schema.interfaces import ISequence
from zope.component import queryMultiAdapter
from tempfile import gettempdir
from os.path import join
import os


class FileUploadConverter(BaseDataConverter):
    """Converter for multi file widgets used on `schema.List` fields."""

    adapts(ISequence, IFileUploadWidget)

    def toWidgetValue(self, value):
        """Converts the value to a form used by the widget.
            For some reason this never gets called for File Uploads
            """
        return value

    def toFieldValue(self, value):
        """Converts the value to a storable form."""
        context = self.widget.context
        tmpdir = gettempdir()
        if not IAddForm.providedBy(self.widget.form):
            dm = queryMultiAdapter((context, self.field), IDataManager)
        else:
            dm = None

        current_field_value = (
            dm.query()
            if ((dm is not None) and self.field.interface.providedBy(context))
            else None
        )
        if not current_field_value or current_field_value == NO_VALUE:
            current_field_value = []
        if not isinstance(current_field_value, list):
            current_field_value = [current_field_value]
        current_field_set = set(current_field_value)
        retvalue = []
        value_type = self.field.value_type._type
        if not value:
            return value
        elif not isinstance(value, list):
            value = [value]
        for item in value:
            if item['new']:
                retvalue.append(value_type(data=item['file'].read(),
                                filename=item['name']))
                filepath = join(tmpdir, item['temp'])
                os.remove(filepath)
            else:
                for existing_file in current_field_set:
                    if existing_file.filename == item['name']:
                        retvalue.append(existing_file)
        return retvalue
