import importlib.util
import pathlib
import unittest


MODULE_PATH = (
    pathlib.Path(__file__).parents[1]
    / "custom_components"
    / "treeow"
    / "core"
    / "availability.py"
)


def load_availability_module():
    spec = importlib.util.spec_from_file_location("treeow_availability", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeviceAvailabilityTrackerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_availability_module()

    def test_offline_status_is_unavailable_immediately(self):
        tracker = self.module.DeviceAvailabilityTracker({"status": 2})

        self.assertFalse(tracker.available)
        self.assertEqual(tracker.consecutive_failures, 0)

    def test_online_status_recovers_an_offline_device(self):
        tracker = self.module.DeviceAvailabilityTracker({"status": 2})

        changed = tracker.observe_payload({"status": 1})

        self.assertTrue(changed)
        self.assertTrue(tracker.available)

    def test_string_status_values_are_supported(self):
        tracker = self.module.DeviceAvailabilityTracker({"status": "2"})

        self.assertFalse(tracker.available)
        self.assertTrue(tracker.observe_payload({"status": "1"}))
        self.assertTrue(tracker.available)

    def test_unknown_status_preserves_the_previous_state(self):
        tracker = self.module.DeviceAvailabilityTracker({"status": 1})

        changed = tracker.observe_payload({"status": 99})

        self.assertFalse(changed)
        self.assertTrue(tracker.available)

    def test_boolean_status_is_not_treated_as_integer_status(self):
        tracker = self.module.DeviceAvailabilityTracker({"status": True})

        self.assertFalse(tracker.available)

    def test_three_consecutive_poll_failures_mark_device_unavailable(self):
        tracker = self.module.DeviceAvailabilityTracker(
            {"status": 1},
            failure_limit=3,
        )

        self.assertFalse(tracker.observe_failure())
        self.assertTrue(tracker.available)
        self.assertFalse(tracker.observe_failure())
        self.assertTrue(tracker.available)
        self.assertTrue(tracker.observe_failure())
        self.assertFalse(tracker.available)

    def test_successful_payload_resets_failure_counter(self):
        tracker = self.module.DeviceAvailabilityTracker(
            {"status": 1},
            failure_limit=3,
        )
        tracker.observe_failure()
        tracker.observe_failure()

        self.assertFalse(tracker.observe_payload({"status": 1}))
        self.assertEqual(tracker.consecutive_failures, 0)
        self.assertFalse(tracker.observe_failure())
        self.assertTrue(tracker.available)

    def test_force_unavailable_only_reports_a_real_transition(self):
        tracker = self.module.DeviceAvailabilityTracker({"status": 1})

        self.assertTrue(tracker.force_unavailable())
        self.assertFalse(tracker.available)
        self.assertFalse(tracker.force_unavailable())


if __name__ == "__main__":
    unittest.main()
