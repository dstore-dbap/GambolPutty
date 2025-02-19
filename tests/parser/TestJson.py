import mock
import json
import lumbermill.utils.DictUtils as DictUtils

from tests.ModuleBaseTestCase import ModuleBaseTestCase
from lumbermill.parser import Json


class TestJson(ModuleBaseTestCase):

    def setUp(self):
        super(TestJson, self).setUp(Json.Json(mock.Mock()))

    def testDecode(self):
        self.test_object.configure({'source_fields': ['json_data']})
        self.checkConfiguration()
        data = DictUtils.getDefaultEventDict({'json_data': '{"South African": "Fast", "unladen": "swallow"}'})
        event = None
        for event in self.test_object.handleEvent(data):
            self.assertTrue('South African' in event and event['South African'] == "Fast")
        self.assertIsNotNone(event)

    def testDecodeOfNestedSourceField(self):
        self.test_object.configure({'source_fields': ['swallow.json_data']})
        self.checkConfiguration()
        data = DictUtils.getDefaultEventDict({'swallow': {'json_data': '{"South African": "Fast", "unladen": "swallow"}'}})
        event = None
        for event in self.test_object.handleEvent(data):
            self.assertTrue('South African' in event and event['South African'] == "Fast")
        self.assertIsNotNone(event)

    def testEncode(self):
        self.test_object.configure({'action': 'encode',
                                    'source_fields': 'all',
                                    'target_field': 'json_data'})
        self.checkConfiguration()
        data = DictUtils.getDefaultEventDict({"South African": "Fast", "unladen": "swallow"})
        event = None
        for event in self.test_object.handleEvent(data):
            json_str = event.pop('json_data')
            self.assertDictEqual(json.loads(json_str), data)
        self.assertIsNotNone(event)

    def testEncodeSingleField(self):
        self.test_object.configure({'action': 'encode',
                                    'source_fields': ["South African"],
                                    'target_field': 'json_data'})
        self.checkConfiguration()
        data = DictUtils.getDefaultEventDict({"South African": {"Fast": True}, "unladen": {"swallow": False}})
        event = None
        for event in self.test_object.handleEvent(data):
            json_str = event.pop('json_data')
            self.assertDictEqual(json.loads(json_str), {"South African": {"Fast": True}})
        self.assertIsNotNone(event)

    def testEncodeMultipleFields(self):
        self.test_object.configure({'action': 'encode',
                                    'source_fields': ["South African", "unladen"],
                                    'target_field': 'json_data'})
        self.checkConfiguration()
        data = DictUtils.getDefaultEventDict({"South African": {"Fast": True}, "unladen": {"swallow": False}})
        event = None
        for event in self.test_object.handleEvent(data):
            json_str = event.pop('json_data')
            import pprint
            pprint.pprint(json_str)
            self.assertDictEqual(json.loads(json_str), {"South African": {"Fast": True}, "unladen": {"swallow": False}})
        self.assertIsNotNone(event)