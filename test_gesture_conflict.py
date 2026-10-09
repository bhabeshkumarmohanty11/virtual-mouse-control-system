
import ast
import unittest
from pathlib import Path


class GestureConflictTests(unittest.TestCase):
    def test_right_click_guarded_during_drag(self):
        source = Path("app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        run_function = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_virtual_mouse"
        )

        source_segment = ast.get_source_segment(source, run_function)
        self.assertIsNotNone(source_segment)
        self.assertIn("left_button_held", source_segment)

        lines = source_segment.splitlines()

        guard_line = next(
            i for i, line in enumerate(lines)
            if line.strip() == "if left_button_held:"
        )
        right_click_line = next(
            i for i, line in enumerate(lines)
            if 'pyautogui.click(button="right")' in line
        )

        self.assertLess(guard_line, right_click_line)

        guard_indent = len(lines[guard_line]) - len(lines[guard_line].lstrip())
        action_indent = (
            len(lines[right_click_line])
            - len(lines[right_click_line].lstrip())
        )
        self.assertGreater(action_indent, guard_indent)


if __name__ == "__main__":
    unittest.main()
