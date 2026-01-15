#!/usr/bin/env python3
"""Generate offscreen screenshots for the Visual Designer features.
Creates PNGs under docs/images/ for inclusion in documentation.
"""
from pathlib import Path
import sys

# Ensure project root is on sys.path so local packages (visualasic) can be imported
repo_root = Path(__file__).resolve().parents[1]
# Ensure both repo root and visualasic/src are importable
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
visualasic_src = repo_root / 'visualasic' / 'src'
if visualasic_src.exists() and str(visualasic_src) not in sys.path:
    sys.path.insert(0, str(visualasic_src))

# Use offscreen platform for headless rendering
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter
from visualasic.ide.designer_widget import DesignerCanvas

OUT_DIR = Path(__file__).resolve().parents[1] / 'docs' / 'images'
OUT_DIR.mkdir(parents=True, exist_ok=True)

app = QApplication.instance() or QApplication([])

# 1) Basic form screenshot
canvas = DesignerCanvas(width=400, height=300)
# load classic template to show typical form
from pathlib import Path
import json
tmpl = Path(__file__).resolve().parents[1] / 'visualasic' / 'examples' / 'form_templates' / 'classic.form.json'
try:
    with open(tmpl, 'r', encoding='utf-8') as f:
        form = json.load(f)
    canvas.load_from_form(form)
except Exception:
    # fallback: add a few controls manually
    canvas.add_label(12, 8)
    canvas.add_button(120, 200)
    canvas.add_button(210, 200)

# render the scene to a pixmap
img1 = QPixmap(canvas.width(), canvas.height())
img1.fill()
p = QPainter(img1)
canvas.render(p)
p.end()
img1.save(str(OUT_DIR / 'visual_designer_form.png'))
print('Wrote', OUT_DIR / 'visual_designer_form.png')

# 2) Preview screenshot (use the form and render the preview content widget)
from visualasic.ide.form_preview import FormPreviewDialog
preview = None
try:
    preview = FormPreviewDialog(canvas.to_form())
    # build content without showing; render its children to pixmap
    wdg = preview._content
    if wdg is not None:
        img2 = QPixmap(wdg.width() or 320, wdg.height() or 240)
        img2.fill()
        p2 = QPainter(img2)
        wdg.render(p2)
        p2.end()
        img2.save(str(OUT_DIR / 'visual_designer_preview.png'))
        print('Wrote', OUT_DIR / 'visual_designer_preview.png')
except Exception as e:
    print('Preview render failed:', e)

# 3) Snaplines/rulers demonstration: enable rulers and trigger snaplines
canvas.show_rulers = True
b1 = canvas.add_button(20, 30)
b2 = canvas.add_button(120, 30)
# trigger snapline update by simulating move
canvas.control_moved.emit(b2)
img3 = QPixmap(canvas.width(), canvas.height())
img3.fill()
p3 = QPainter(img3)
canvas.render(p3)
p3.end()
img3.save(str(OUT_DIR / 'visual_designer_snaplines.png'))
print('Wrote', OUT_DIR / 'visual_designer_snaplines.png')

print('Done')
