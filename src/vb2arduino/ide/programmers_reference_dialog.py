from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt6.QtCore import Qt
import pathlib

class ProgrammersReferenceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Programmer's Reference")
        self.resize(800, 600)
        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser(self)
        layout.addWidget(self.text_browser)

        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        # Load the markdown file and display as HTML
        import os
        import sys
        import markdown
        # Try CWD/docs first
        cwd = pathlib.Path(os.getcwd())
        ref_path = cwd / "docs" / "programmers_reference.md"
        if not ref_path.exists():
            # Try walking up from __file__
            here = pathlib.Path(__file__).resolve()
            for parent in here.parents:
                candidate = parent.parent / "docs" / "programmers_reference.md"
                if candidate.exists():
                    ref_path = candidate
                    break
        if ref_path.exists():
            with open(ref_path, "r", encoding="utf-8") as f:
                html = markdown.markdown(
                    f.read(),
                    extensions=[
                        "fenced_code",
                        "tables",
                        "toc",
                        "attr_list",
                        "md_in_html"
                    ]
                )
                self.text_browser.setHtml(html)
        else:
            self.text_browser.setText(f"Reference file not found: {ref_path}")
