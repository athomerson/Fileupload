#from Acquisition import aq_inner
from plone.namedfile.utils import set_headers, stream_data
from Products.Five.browser import BrowserView
from z3c.form.interfaces import IFieldWidget, IDataManager, NO_VALUE, IAddForm
from z3c.form.widget import FieldWidget
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implements, implementer
from zope.publisher.interfaces import IPublishTraverse, NotFound

from collective.widget.fileupload.interfaces import IFileUploadWidget
from collective.widget.fileupload.converter import FileUploadConverter
from collective.widget.fileupload.base import FileWidget
from plone.app.widgets.dx import BaseWidget
from zope.interface import implementsOnly
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from tempfile import NamedTemporaryFile
from tempfile import gettempdir
from z3c.form.browser.text import TextWidget
from os.path import basename
from os.path import join
import json
import fnmatch
import os
import time
import mimetypes
from ZPublisher.Iterators import filestream_iterator


class FileUploadWidget(BaseWidget, TextWidget):
    implementsOnly(IFileUploadWidget)

    _base = FileWidget
    _converter = FileUploadConverter

    pattern = 'fileupload'
    pattern_options = BaseWidget.pattern_options.copy()
    multiple = True

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `multiple `: field multiple

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super(FileUploadWidget, self)._base_args()
        url = '%s/++widget++%s/@@upload/' % (
                    self.request.getURL(),
                    self.name)
        args['name'] = self.name
        args['multiple'] = self.multiple
        args.setdefault('pattern_options', {})
        args['pattern_options'] = {'url': url}
        self.cleanup()
        loaded = []
        if not IAddForm.providedBy(self.form):
            dm = queryMultiAdapter((self.context, self.field,), IDataManager)
        else:
            dm = None

        current_field_value = (
            dm.query()
            if ((dm is not None) and
                self.field.interface.providedBy(self.context))
            else None
        )
        if current_field_value and current_field_value != NO_VALUE:
            if not isinstance(current_field_value, list):
                current_field_value = [current_field_value]
            current_field_set = set(current_field_value)
            for item in current_field_set:
                dl_url = '%s/++widget++%s/@@downloadexisting/' % (
                             self.request.getURL(),
                             self.name) + item.filename
                info = {'name': item.filename,
                            'title': item.filename,
                            'size': item.getSize(),
                            'url': dl_url,
                            }
                loaded.append(info)
        args['pattern_options']['existing'] = loaded
        return args

    def extract(self, default=NO_VALUE):
        """Extract all real FileUpload objects.
        """
        value = []
        if getattr(self.request, "uploaded", None) is not None:
            files = self.request['uploaded']
            if files:
                extracted = json.loads(str(files))
                for extracted_file in extracted:
                    if extracted_file['name'] != extracted_file['title']:
                        tmpdir = gettempdir()
                        path = join(tmpdir, extracted_file['name'])
                        file_ = open(path, 'r+b')
                        newfile = {'name': extracted_file['title'],
                                   'file': file_, 'new': True,
                                   'temp': extracted_file['name']}
                        value.append(newfile)
                    else:
                        oldfile = {'name': extracted_file['name'],
                                   'file': None, 'new': False}
                        value.append(oldfile)
        return value

    def cleanup(self):
        """
        look through upload directory and remove old uploads
        (older than 24 hrs)
        """
        now = time.time()
        tmpdir = gettempdir()
        for filename in os.listdir(tmpdir):
            if fnmatch.fnmatch(filename, '*FileUpload'):
                filepath = os.path.join(tmpdir, filename)
                if (os.stat(filepath).st_mtime) < now - 24 * 60 * 60:
                    os.unlink(filepath)


@implementer(IFieldWidget)
def FileUploadFieldWidget(field, request):
    return FieldWidget(field, FileUploadWidget(request))


class Upload(BrowserView):
    """Upload a file via ++widget++widget_name/@@upload"""

    implements(IPublishTraverse)

    def __call__(self):

        if hasattr(self.request, "REQUEST_METHOD"):
            # TODO: we should check errors in the creation process, and
            # broadcast those to the error template in JS
            if self.request["REQUEST_METHOD"] == "POST":
                if getattr(self.request, self.context.name, None) is not None:
                    files = self.request[self.context.name]
                    uploaded = self.upload([files])
                    if uploaded:
                        return json.dumps({'files': uploaded})
                return json.dumps({'files': []})

    def upload(self, files):
        loaded = []
        fileid = self.request['fileids']
        for item in files:
            if item.filename:
                filename = safe_unicode(item.filename)
                item.seek(0, 2)  # end of file
                tmpsize = item.tell()
                tmpfile = NamedTemporaryFile(suffix='FileUpload', delete=False)
                item.seek(0)
                tmpfile.write(item.read())
                tmpfile.close()
                dlname = basename(tmpfile.name)
                dl_url = '%s/@@download/' % (
                         self.request.URL1) + dlname + '?name=' + filename
                info = {'name': dlname,
                        'title': filename,
                        'size': tmpsize,
                        'url': dl_url,
                        'fileid': fileid,
                        }
                loaded.append(info)
            return loaded


class DownloadExisting(BrowserView):
    """Download a file via ++widget++widget_name/@@downloadexisting/filename"""

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.filename = None

    def publishTraverse(self, request, name):

        if self.filename is None:  # ../@@download/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)

        return self

    def __call__(self):

        if self.context.form is not None:
            content = aq_inner(self.context.form.getContent())
        else:
            content = aq_inner(self.context.context)
        field = aq_inner(self.context.field)

        dm = getMultiAdapter((content, field,), IDataManager)
        file_list = dm.query()
        if file_list == NO_VALUE:
            return None
        file_ = None
        if not isinstance(file_list, list):
            file_list = [file_list]
        for curr_file in file_list:
            if curr_file.filename == self.filename:
                file_ = curr_file
        filename = getattr(file_, 'filename', '')
        if not file_:
            return None
        set_headers(file_, self.request.response, filename=filename)
        return stream_data(file_)


class Download(BrowserView):
    """Download a file via ++widget++widget_name/@@download/filename"""

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.filename = None

    def publishTraverse(self, request, name):

        if self.filename is None:  # ../@@download/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)

        return self

    def __call__(self):

        if getattr(self.request, "name", None) is not None:
            filename = self.request['name']
        tmpdir = gettempdir()
        filepath = os.path.join(tmpdir, self.filename)
        try:
            file_ = open(filepath)
        except IOError:
            return

        file_.seek(0, 2)  # end of file
        tmpsize = file_.tell()
        file_.seek(0)
        contenttype = 'application/octet-stream'
        filename = safe_unicode(filename)
        if filename:
            extension = os.path.splitext(filename)[1].lower()
            contenttype = mimetypes.types_map.get(extension,
                                                  'application/octet-stream')
        self.request.response.setHeader("Content-Type", contenttype)
        self.request.response.setHeader("Content-Length", tmpsize)
        if filename is not None:
            self.request.response.setHeader("Content-Disposition",
                                            "attachment; filename=\"%s\""
                                             % filename)
        return filestream_iterator(filepath, 'rb')
