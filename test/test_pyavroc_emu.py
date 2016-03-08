# BEGIN_COPYRIGHT
#
# Copyright (C) 2014-2016 CRS4.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# END_COPYRIGHT

import unittest
import tempfile
import shutil
import os

import pyfeatures.pyavroc_emu as pyavroc_emu
import pyfeatures.schema as schema


class Base(unittest.TestCase):

    def setUp(self):
        array_slice = {
            "dtype": "UINT8",
            "little_endian": True,
            "shape": [4, 4, 1, 2, 3],
            "offsets": [0, 0, 0, 0, 0],
            "deltas": [4, 4, 1, 1, 1],
            "data": ''.join(chr(_) for _ in xrange(16))
        }
        self.record_map = {
            "BioImgPlane": {
                "name": "foo",
                "dimension_order": "XYZCT",
                "pixel_data": array_slice,
            },
            "Signatures": {
                "feature_names": ["one", "two", "three"],
                "values": [.1, .2, .3],
                "name": "bar",
                "feature_set_version": "0.1",
                "source_filepath": "/foo/bar",
                "auxiliary_feature_storage": "storage",
                "plane_tag": "tag",
            }
        }


class TestFileIO(Base):

    def setUp(self):
        super(TestFileIO, self).setUp()
        self.wd = tempfile.mkdtemp(prefix="pyfeatures_")

    def tearDown(self):
        shutil.rmtree(self.wd)

    def runTest(self):
        for name, record in self.record_map.iteritems():
            fn = os.path.join(self.wd, "foo")
            with open(fn, "w") as f:
                writer = pyavroc_emu.AvroFileWriter(f, getattr(schema, name))
                writer.write(record)
                writer.close()
            with open(fn) as f:
                reader = pyavroc_emu.AvroFileReader(f)
                self.assertEqual(reader.next(), record)


class TestSerDe(Base):

    def setUp(self):
        super(TestSerDe, self).setUp()

    def runTest(self):
        for name, record in self.record_map.iteritems():
            schema_str = getattr(schema, name)
            serializer = pyavroc_emu.AvroSerializer(schema_str)
            rec_bytes = serializer.serialize(record)
            deserializer = pyavroc_emu.AvroDeserializer(schema_str)
            self.assertEqual(deserializer.deserialize(rec_bytes), record)


def load_tests(loader, tests, pattern):
    test_cases = (TestFileIO, TestSerDe)
    suite = unittest.TestSuite()
    for tc in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(tc))
    return suite


def main():
    suite = load_tests(unittest.defaultTestLoader, None, None)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    main()