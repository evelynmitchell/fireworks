"""
Master tests for FireWorks - generally used to ensure that installation was \
completed properly.
"""

import unittest

import pytest

from fireworks import Firework, FWAction
from fireworks.core.firework import Workflow
from fireworks.user_objects.firetasks.script_task import ScriptTask
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter
from fireworks.utilities.fw_serializers import load_object

__author__ = "Anubhav Jain"
__copyright__ = "Copyright 2013, The Materials Project"
__maintainer__ = "Anubhav Jain"
__email__ = "ajain@lbl.gov"
__date__ = "Jan 9, 2013"


class TestImports(unittest.TestCase):
    """Make sure that required external libraries can be imported."""

    def test_imports(self) -> None:
        pass
        # test that MongoClient is available (newer pymongo)


class BasicTests(unittest.TestCase):
    """Make sure that required external libraries can be imported."""

    def test_fwconnector(self) -> None:
        fw1 = Firework(ScriptTask.from_str('echo "1"'))
        fw2 = Firework(ScriptTask.from_str('echo "1"'))

        wf1 = Workflow([fw1, fw2], {fw1.fw_id: fw2.fw_id})
        assert wf1.links == {fw1.fw_id: [fw2.fw_id], fw2.fw_id: []}

        wf2 = Workflow([fw1, fw2], {fw1: fw2})
        assert wf2.links == {fw1.fw_id: [fw2.fw_id], fw2.fw_id: []}

        wf3 = Workflow([fw1, fw2])
        assert wf3.links == {fw1.fw_id: [], fw2.fw_id: []}

    def test_parentconnector(self) -> None:
        fw1 = Firework(ScriptTask.from_str('echo "1"'))
        fw2 = Firework(ScriptTask.from_str('echo "1"'), parents=fw1)
        fw3 = Firework(ScriptTask.from_str('echo "1"'), parents=[fw1, fw2])

        assert Workflow([fw1, fw2, fw3]).links == {
            fw1.fw_id: [fw2.fw_id, fw3.fw_id],
            fw2.fw_id: [fw3.fw_id],
            fw3.fw_id: [],
        }
        with pytest.raises(ValueError):
            Workflow([fw1, fw3])  # can't make this


class SerializationTests(unittest.TestCase):
    @staticmethod
    def get_data(obj_dict):
        mod_name = "fireworks.user_objects.queue_adapters.common_adapter"
        classname = "CommonAdapter"
        mod = __import__(mod_name, globals(), locals(), [classname], 0)
        if hasattr(mod, classname):
            cls_ = getattr(mod, classname)
            return cls_.from_dict(obj_dict)
        return None

    def test_serialization_details(self) -> None:
        # This detects a weird bug found in early version of serializers

        pbs = CommonAdapter("PBS")
        assert isinstance(pbs, CommonAdapter)
        assert isinstance(self.get_data(pbs.to_dict()), CommonAdapter)
        assert isinstance(load_object(pbs.to_dict()), CommonAdapter)
        assert isinstance(self.get_data(pbs.to_dict()), CommonAdapter)  # repeated test on purpose!

    def test_recursive_deserialize(self) -> None:
        my_dict = {
            "update_spec": {},
            "mod_spec": [],
            "stored_data": {},
            "exit": False,
            "detours": [],
            "additions": [
                {
                    "updated_on": "2014-10-14T00:56:27.758673",
                    "fw_id": -2,
                    "spec": {"_tasks": [{"use_shell": True, "_fw_name": "ScriptTask", "script": ['echo "1"']}]},
                    "created_on": "2014-10-14T00:56:27.758669",
                    "name": "Unnamed FW",
                }
            ],
            "defuse_children": False,
        }
        FWAction.from_dict(my_dict)
