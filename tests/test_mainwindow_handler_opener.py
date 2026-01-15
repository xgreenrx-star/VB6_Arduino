import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from vb2arduino.ide.main_window import MainWindow


def test_create_handler_manager_opens_file(tmp_path, qtbot):
    # create a MainWindow and ensure created handler opens in a tab
    mw = MainWindow()
    qtbot.addWidget(mw)

    project_root = tmp_path / 'project'
    project_root.mkdir()

    hm = mw.create_handler_manager(project_root)
    p = hm.create_handler('btnOk_Click')
    # The main window should have opened the file in a tab (tab widget count > 0)
    assert mw.tab_widget.count() >= 1
    # The top tab should have file_path property pointing to the created .bas
    tab0 = mw.tab_widget.widget(0)
    assert tab0.property('file_path') is not None
    assert str(p) == tab0.property('file_path')
    # cleanup
    mw.close()