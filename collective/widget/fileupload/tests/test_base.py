# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma: nocover
    import unittest  # pragma: nocover
    assert unittest  # pragma: nocover


class BaseWidgetTests(unittest.TestCase):
    """Tests for collective.widget.fileupload.base.FileWidget."""

    def test_defaults(self):
        from collective.widget.fileupload.base import FileWidget

        widget = FileWidget('fileupload', name='example1')
        self.assertEqual(
            widget.render(),
            '<input class="pat-fileupload" type="file" name="example1"/>')

        self.assertEqual(widget.klass, 'pat-fileupload')
    def test_multiple(self):
        from collective.widget.fileupload.base import FileWidget

        widget = FileWidget('fileupload', name='example2', multiple=True)
        self.assertEqual(
            widget.render(),
            '<input class="pat-fileupload" type="file" multiple="multiple" name="example2"/>')

        self.assertTrue(widget.multiple)

        widget = FileWidget('fileupload', name='example3', multiple=False)
        self.assertEqual(
            widget.render(),
            '<input class="pat-fileupload" type="file" name="example3"/>')

        self.assertFalse(widget.multiple)

    def test_setting_patterns_options(self):
        from collective.widget.fileupload.base import FileWidget

        widget = FileWidget(
            'fileupload',
            name='example2',
            pattern_options={
                'option1': 'value1',
                'option2': 'value2',
            })

        self.assertEqual(
            widget.render(),
            '<input class="pat-fileupload" type="file" name="example2" '
            'data-pat-fileupload="{'
            '&quot;option2&quot;: &quot;value2&quot;, '
            '&quot;option1&quot;: &quot;value1&quot;}"/>')
