import unittest
from PyQt6.QtWidgets import QApplication
import os
import sys
import types
import unittest
# Skip these responsive UI tests by default unless VB2_RUN_RESP_TESTS=1 is set (they require a display environment)
if os.environ.get('VB2_RUN_RESP_TESTS', '0') != '1':
    raise unittest.SkipTest('Responsive UI tests are skipped unless VB2_RUN_RESP_TESTS=1')

# Create a dummy serial_plotter module to avoid importing pyqtgraph during tests
_dummy_mod = types.ModuleType('vb2arduino.ide.serial_plotter')
class _DummyPlotter:
    def __init__(self, parent=None):
        self.timer = types.SimpleNamespace(stop=lambda : None)
    def add_sample(self, label, value):
        pass
_dummy_mod.SerialPlotter = _DummyPlotter
sys.modules['vb2arduino.ide.serial_plotter'] = _dummy_mod

from vb2arduino.ide.serial_monitor import SerialMonitor
from vb2arduino.ide.serial_plotter import SerialPlotter  # This imports our dummy module



app = QApplication.instance() or QApplication([])

class TestResponsiveUI(unittest.TestCase):
    def test_serial_monitor_responsive(self):
        sm = SerialMonitor()
        # Stop internal plotter timer immediately to avoid background processing
        try:
            sm.plotter.timer.stop()
        except Exception:
            pass
        # Large width: more menu should be hidden
        sm.resize(800, 200)
        sm._update_responsive_layout()
        self.assertTrue(sm.more_btn.isHidden())
        # Small width: more menu should be shown (not hidden)
        sm.resize(320, 200)
        sm._update_responsive_layout()
        self.assertFalse(sm.more_btn.isHidden())

    def test_serial_plotter_responsive(self):
        sp = SerialPlotter()
        # Stop the refresh timer to avoid background processing in tests
        sp.timer.stop()
        sp.resize(800, 200)
        sp._update_responsive_layout()
        self.assertTrue(sp.plot_more_btn.isHidden())
        sp.resize(300, 200)
        sp._update_responsive_layout()
        self.assertFalse(sp.plot_more_btn.isHidden())

        # Also ensure SerialMonitor's internal plotter timer won't interfere
        sm.plotter.timer.stop()

if __name__ == '__main__':
    unittest.main()
