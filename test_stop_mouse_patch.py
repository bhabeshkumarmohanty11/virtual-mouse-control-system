
import ast
import unittest
from pathlib import Path


APP_PATH = Path(__file__).with_name("app.py")


class StopMouseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.functions = {
            node.name: node
            for node in cls.tree.body
            if isinstance(node, ast.FunctionDef)
        }

    def test_app_source_parses(self):
        self.assertIsNotNone(self.tree)

    def test_stop_mouse_signals_shutdown(self):
        stop_fn = self.functions["stop_mouse"]
        calls = [
            node.func.attr
            for node in ast.walk(stop_fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        ]
        self.assertIn("set", calls)

        stop_source = ast.get_source_segment(self.source, stop_fn)
        self.assertIn("stop_event.set()", stop_source)

    def test_stop_mouse_does_not_release_button_on_gui_thread(self):
        stop_fn = self.functions["stop_mouse"]
        calls = [
            node.func.attr
            for node in ast.walk(stop_fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        ]
        self.assertNotIn("mouseUp", calls)

    def test_worker_releases_button_during_cleanup(self):
        worker = self.functions["run_virtual_mouse"]
        worker_source = ast.get_source_segment(self.source, worker)
        self.assertIn("finally:", worker_source)
        self.assertIn('pyautogui.mouseUp(button="left")', worker_source)

    def test_worker_resets_dragging_state(self):
        worker = self.functions["run_virtual_mouse"]
        worker_source = ast.get_source_segment(self.source, worker)
        self.assertIn("set_dragging(False)", worker_source)

    def test_stop_button_disables_itself(self):
        stop_fn = self.functions["stop_mouse"]
        calls = [
            node for node in ast.walk(stop_fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "config"
        ]
        self.assertTrue(calls)


if __name__ == "__main__":
    unittest.main()
