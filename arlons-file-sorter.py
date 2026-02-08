#!/usr/bin/env python3
# 									Arlon's File Sorter
#
# This is Arlon's File Sorter. Couldn't have built it without lots of help from our good friend ChatGPT.
# Copyright (C) 2026 Arlon Arriola
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# https://www.gnu.org/licenses/gpl-3.0.txt
#
# Usage:
# $ source ~/all/docs/txt/programs/python/file-sorter-1/venv/bin/activate;python3 /home/username/all/docs/txt/programs/python/file-sorter-1/ArlonsFileSorter.py ~/Desktop/drone/100MEDIA/
#
# Search below for 37 or self.setFixedHeight(37) # 6_4_2 # - change that to 27 if you want more folder rows - it just cuts the elements off, is all, so 37 is a little better.
#
import sys
import shutil
from pathlib import Path
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QWheelEvent, QKeyEvent
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,QHBoxLayout, QLineEdit, QFileDialog)
from PySide6.QtWidgets import QSizePolicy # 6_4_2
from PySide6.QtWidgets import QSpinBox # 668 2
from PySide6.QtGui import QFont # 684
from PySide6.QtGui import QFontMetrics # 684
from PySide6.QtGui import QPainter # 684
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QGroupBox # 685
from PySide6.QtWidgets import QComboBox # 685+for the sort-by combo box
from PySide6.QtWidgets import QDoubleSpinBox # text scale setting
import sys
import os

if "--help" in sys.argv or "-h" in sys.argv: # print the README.md if you want, with -h or --help 					#677 Help Text #677 Help Text
	readme = Path(__file__).with_name("README.md") # print the README.md if you want, with -h or --help							#677 Help Text
	if readme.exists(): # print the README.md if you want, with -h or --help													#677 Help Text
		import subprocess # I think this does the same as the above - these two lines go together								#677 Help Text
		subprocess.run(["less", "-R"], input=(f"\033[35m"+readme.read_text().splitlines()[0]+"\033[0m\n" +"\n".join(f"\033[36m{line}\033[0m" for line in readme.read_text().splitlines()[1:])+ "\033[0m"), text=True) # I think this does the same as the above - these two lines go together - I changed it so the first line is purple and the rest are cyan.			#677 Help Text												#677 Help Text
	else: # print the README.md if you want, with -h or --help																	#677 Help Text
		print("README.md not found.") # print the README.md if you want, with -h or --help 										#677 Help Text
	sys.exit(0) # print the README.md if you want, with -h or --help 															#677 Help Text

folder = sys.argv[1]
p = Path(sys.argv[1])

if p.is_file():
    folder = p.parent
else:
    folder = p
folder=str(folder)

from collections import OrderedDict
IMAGE_EXTS = list(OrderedDict.fromkeys([".jpg", ".JPG", ".JPEG", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]))
TEXT_EXTS = list(OrderedDict.fromkeys([	#684
	".txt", ".md", ".py", ".c", ".cpp", ".h",
	".json", ".yaml", ".yml", ".ini",
	".log", ".sh", ".cfg", ".java", ".js", ".php"
]))	#684

# ---------------- LinkedWindowMixin ----------------
class LinkedWindowMixin:
	_linked_windows: list = []
	_raise_in_progress: bool = False  # Class-level lock to prevent looping
	_last_activated_window: QWidget = None  # Track the last activated window
	raise_windows_enabled = False  # Flag to control whether windows should be raised
	
	@classmethod
	def toggle_window_raising(cls, enabled: bool):
		"""Toggles the window raising behavior."""
		cls.raise_windows_enabled = enabled
		# print("Line 1043 says window raising is now enabled: ", cls.raise_windows_enabled)
	
	def collect(self):
		"""Add the window instance to the shared linked windows list."""
		if self not in LinkedWindowMixin._linked_windows:
			LinkedWindowMixin._linked_windows.append(self)
		self._raise_source = False

	def _raise_other_windows(self):
		"""Helper function to raise other windows after activation."""
		# print(f"Raising windows for {self}")
		try:
			# Raise all other linked windows except the one just activated
			for win in LinkedWindowMixin._linked_windows:
				if win is not self and win != LinkedWindowMixin._last_activated_window:
					# print(f"Raising window: {win}")
					win.raise_()
					win.activateWindow()

			# After processing, update the last activated window
			LinkedWindowMixin._last_activated_window = self

		except Exception as e:
			print(f"Error while raising windows: {e}")

	def event(self, e):
		"""Handle window activation events and raise linked windows."""
		if e.type() == QEvent.WindowActivate:
			# print(f"Window {self} activated")
			
			# Skip raising windows if the toggle is disabled
			if not LinkedWindowMixin.raise_windows_enabled:
				return QWidget.event(self, e) or True  # Skip the raising logic if disabled

			if not LinkedWindowMixin._raise_in_progress:
				LinkedWindowMixin._raise_in_progress = True
				try:
					# Ensure _raise_other_windows is available before calling it
					self._raise_other_windows()  # Call the method directly
				except Exception as ex:
					print(f"Error in event handling: {ex}")
				finally:
					LinkedWindowMixin._raise_in_progress = False

				return True  # Event is handled here

		return QWidget.event(self, e) or True  # Pass to the base event handler if we don't handle it

# ---------------- Image Window ----------------
class ImageWindow(QWidget, LinkedWindowMixin):
	SHOW_OVERLAY_LABELS = True # 6_2
	# SHOW_OVERLAY_LABELS = False # 6_2
	def event(self, e):
		if LinkedWindowMixin.event(self, e):
			return True
		# return super().event(e)
	def __init__(self):
		super().__init__()
		LinkedWindowMixin.collect(self)

		self.setWindowTitle("Image")

		self.label = QLabel(alignment=Qt.AlignCenter)

		if self.SHOW_OVERLAY_LABELS: # 6_2
			self.counter = QLabel(self)
			self.counter.setStyleSheet("""
				QLabel {
					background-color: rgba(0, 0, 0, 160);
					color: white;
					padding: 4px 8px;
					border-radius: 4px;
					font-size: 12px;
				}
			""")
			self.counter.move(10, 10)
			self.counter.raise_()
		else: # 6_2
			self.counter = None # 6_2
			
		 # 6_2
		if self.SHOW_OVERLAY_LABELS: # 6_2
			self.filename = QLabel(self) # 6_2
			self.filename.setStyleSheet("""
				QLabel {
					background-color: rgba(0, 0, 0, 160);
					color: white;
					padding: 4px 8px;
					border-radius: 4px;
					font-size: 12px;
				}
			""") # 6_2
			self.filename.move(10, 10) # 6_2
			self.filename.raise_() # 6_2
		else: # 6_2
			self.filename = None # 6_2

		layout = QVBoxLayout(self)
		layout.addWidget(self.label)

		self.pixmap = None
		self.zoom = 1.0

		# in your __init__ of the window or paired window # 668
		self.middle_mouse_state = 0   # 668
		# 0 = stopped, 1 = forward, 2 = reverse # 668
		
		self.has_ever_loaded_image = False # fix for zoom restoring/not restoring/obscure zoom bug around the time of filter addition
		self._ctrl_drag_active = False
		self._ctrl_drag_offset = None

	def set_image(self, pixmap: QPixmap):
		self.pixmap = pixmap
		self.update_view()

	def update_counter(self, index: int, total: int):
		if not self.counter:
			return
		if total > 0:
			self.counter.setText(f"{index + 1} / {total}")
			self.counter.show()
		else:
			self.counter.setText("No images")
			self.counter.show()
			self.filename.setText("No images") # 668 3 normally a filename

	#683
	# Zooms on the cursor precisely, keeping the pixel beneath it locked while avoiding drift and borders. #683
	# Keeps the pixel under the mouse fixed during zoom by adjusting window and label dynamically.
	# Eliminates drift and border artifacts by computing fractional cursor positions relative to window. #683
	def update_view(self, cursor_pos: tuple[int,int] | None = None):	#683

		if not self.pixmap:
			return

		old_window_size = self.size()
		old_label_size = self.label.size()

		# Scale pixmap
		new_scaled_size = self.pixmap.size() * self.zoom
		scaled = self.pixmap.scaled(
			new_scaled_size,
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation
		)
		self.label.setPixmap(scaled)
		self.label.adjustSize()

		# Resize window to fit pixmap exactly
		self.setFixedSize(
			self.frameGeometry().size() - self.geometry().size() + scaled.size() - QSize(0, self.label.pos().y())
		)

		if cursor_pos is not None and old_label_size.width() > 0 and old_label_size.height() > 0:
			# Cursor relative to window
			win_x, win_y = self.x(), self.y()
			cx, cy = cursor_pos

			# Cursor relative to old label
			px = cx - self.label.x()
			py = cy - self.label.y()

			# Clamp to pixmap bounds
			px = max(0, min(px, old_label_size.width()))
			py = max(0, min(py, old_label_size.height()))

			# Fraction of cursor in old label
			fx = px / old_label_size.width()
			fy = py / old_label_size.height()

			# Compute new window position so pixel stays under cursor
			new_win_x = win_x + px - fx * self.label.width()
			new_win_y = win_y + py - fy * self.label.height()
			self.move(int(new_win_x), int(new_win_y))

		# Keep counter / filename
		if self.counter:
			self.counter.move(self.width() - self.counter.width() - 10, 10)
			self.counter.raise_()
		if self.filename:
			self.filename.move(10, 10)
			self.filename.raise_()
		"""
		Update the image view and window size while keeping the pixel under the mouse cursor fixed.

		This method performs three key steps:

		1. Scale the pixmap according to the current zoom factor.
		   - Uses Qt.KeepAspectRatio and Qt.SmoothTransformation for high-quality scaling.
		   - Sets the QLabel's pixmap and adjusts its size to fit the scaled image.

		2. Resize the window to match the new pixmap size exactly.
		   - Accounts for window frame offsets using `frameGeometry() - geometry()`.
		   - Corrects subtle padding at the top and left by subtracting the QLabel's position.

		3. Reposition the window so that the pixel originally under the mouse cursor
		   stays under the cursor after scaling.
		   - Computes the fractional position of the cursor relative to the window.
		   - Translates that fractional position into the new window coordinates.
		   - Moves the window so that the cursor points to the same image pixel.

		Key design notes:
		- No fudge factors or hard-coded offsets; all calculations are based on
		  QLabel positions, pixmap size, and window frame geometry.
		- Works for both zoom-in and zoom-out operations.
		- Ensures the pixel under the cursor is stable, preventing drift
		  during repeated zooms.
		- Keeps overlays (counter, filename) positioned correctly after resizing.
		"""

	def zoom_in(self, factor=1.1, cursor_pos: tuple[int,int] | None = None):
		# if not self.paired_window.has_image: #672
		if not self.pixmap: # Fix for zoom on startup not working after 685
			return #672
		self.zoom *= factor
		self.update_view(cursor_pos)

	def zoom_out(self, factor=1.1, cursor_pos: tuple[int,int] | None = None):
		# if not self.paired_window.has_image: #672
		if not self.pixmap: # Fix for zoom on startup not working after 685
			return #672
		self.zoom /= factor
		self.update_view(cursor_pos)

	def wheelEvent(self, event: QWheelEvent):
		cursor = event.position().toTuple()  # position relative to the widget
		if event.angleDelta().y() > 0:
			self.zoom_out(cursor_pos=cursor)
		else:
			self.zoom_in(cursor_pos=cursor)

	def closeEvent(self, event):
		super().closeEvent(event)
		if hasattr(self, 'paired_window'):
			self.paired_window.close()

	def open_in_external(self):
		if not self.pixmap or not hasattr(self, 'paired_window'):
			return

		cw = self.paired_window
		if not cw.images:
			return

		path = cw.images[cw.index]

		# Determine which command to use
		suffix = path.suffix.lower()
		if suffix in IMAGE_EXTS:
			cmd = cw.settings_dialog.image_open_cmd.text().strip()
		elif suffix in TEXT_EXTS:
			cmd = cw.settings_dialog.text_open_cmd.text().strip()
		else:
			return

		if not cmd:
			return

		import shlex, subprocess
		try:
			subprocess.Popen(
				shlex.split(cmd) + [str(path)]
			)
		except Exception as e:
			print("Failed to open external program:", e)
	def mouseMoveEvent(self, event):
		if self._ctrl_drag_active:
			new_pos = event.globalPosition().toPoint() - self._ctrl_drag_offset
			self.move(new_pos)
			event.accept()
			return

		super().mouseMoveEvent(event)
			
	# 6_6_3
	def mousePressEvent(self, event):
		# Ctrl + Left click = begin window drag
		if (
			event.button() == Qt.LeftButton
			and event.modifiers() & Qt.ControlModifier
		):
			self.setCursor(Qt.OpenHandCursor)
			self._ctrl_drag_active = True
			self._ctrl_drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
			event.accept()
			return
	
		# Clickable "No images found" # 6_6_5
		if self.label.text() == "No images found - Click to Select Folder" and hasattr(self, 'paired_window'): # 6_6_5
			cw = self.paired_window # 6_6_5
			cw.refresh_images() # 6_6_5
			if not cw.images: # 6_6_5
				cw.pick_root_folder() # 6_6_5
			return # 6_6_5
			
		if not hasattr(self, 'paired_window'):
			return super().mousePressEvent(event)

		cw = self.paired_window

		delay = cw.delay_spinbox.value() or 0  # fallback to 0 # 668 2
		
		if event.button() == Qt.RightButton and event.modifiers() & Qt.ControlModifier:
			self.open_in_external()
			return

		if event.button() == Qt.LeftButton:
			cw.key_direction = -1
			cw.prev_image()
		elif event.button() == Qt.RightButton:
			cw.key_direction = +1
			cw.next_image()
		elif event.button() == Qt.MiddleButton: # 668
			# cycle: 0 -> forward -> stop -> reverse -> stop -> repeat # 668
			if self.middle_mouse_state == 0:	   # start forward # 668
				cw.key_direction = +1 # 668
				# cw.key_timer.start(0) # 668 # 668 2
				cw.key_timer.setInterval(delay)  # delay ms per step # 668 2
				cw.key_timer.start(delay) # 668 # 668 2
				self.middle_mouse_state = 1 # 668
			elif self.middle_mouse_state == 1:	 # stop forward # 668
				cw.key_timer.stop() # 668
				cw.key_direction = 0 # 668
				self.middle_mouse_state = 2 # 668
			elif self.middle_mouse_state == 2:	 # start reverse # 668
				cw.key_direction = -1 # 668
				# cw.key_timer.start(0) # 668 # 668 2
				cw.key_timer.setInterval(delay)  # delay ms per step # 668 2
				cw.key_timer.start(delay) # 668 # 668 2
				self.middle_mouse_state = 3 # 668
			elif self.middle_mouse_state == 3:	 # stop reverse # 668
				cw.key_timer.stop() # 668
				cw.key_direction = 0 # 668
				self.middle_mouse_state = 0 # 668
		else:
			return super().mousePressEvent(event)

		if not cw.key_timer.isActive():
			# cw.key_timer.start(300) # 668 2
			cw.key_timer.setInterval(delay)  # delay ms per step # 668 2
			cw.key_timer.start(300+delay)  # 668 2
			
	def mouseReleaseEvent(self, event):
		if self._ctrl_drag_active and event.button() == Qt.LeftButton:
			self.unsetCursor()
			self._ctrl_drag_active = False
			self._ctrl_drag_offset = None
			event.accept()
			return

		if hasattr(self, 'paired_window'):
			cw = self.paired_window
			if event.button() in (Qt.LeftButton, Qt.RightButton): # 668
				cw.key_timer.stop()
				cw.key_direction = 0

		super().mouseReleaseEvent(event)
	def nudge(self, dx: int, dy: int):
		x = self.x() + dx
		y = self.y() + dy
		self.move(x, y)

	def window_center_cursor_pos(self) -> tuple[int, int]:
		# simulate a cursor at the center of the label
		lx = self.label.x() + self.label.width() // 2
		ly = self.label.y() + self.label.height() // 2
		return (lx, ly)

class GUI_Builder_helper():
	@staticmethod
	def cpnt(cponent,tooltip, click, button_width, button_height,layout, selfPassed, name): #669
		cponent.setToolTip(tooltip) # 6_6_6 #669
		cponent.setFixedSize(button_width, button_height) # 6_6_6 #669
		layout.addWidget(cponent) # 6_6_6 #669
		# self.swap_button = swap # 6_6_6 #669
		setattr(selfPassed, name, cponent) #669
		cponent.clicked.connect(click) #669
		return cponent #669
	@staticmethod
	def btn(text,tooltip, click, button_width, button_height,layout, selfPassed, name): #669
		return GUI_Builder_helper.cpnt(QPushButton(text),tooltip, click, button_width, button_height,layout, selfPassed, name) #669

# ---------------- Folder Row ----------------
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtWidgets import QStyle # 6_6_2
from PySide6.QtWidgets import QCheckBox # 6_6_7
class FolderRow(QWidget):
	def sizeHint(self):
		return QSize(self.width(), self.height())  # exactly 37
	# def __init__(self, root: Path,cw): # 669
	def __init__(self, root: Path,cw): # 669
		super().__init__()
		self.root = root
		self.cw = cw # 669

		self.label = QLabel()
		self.label.setFixedWidth(60)
		self.label.setAlignment(Qt.AlignCenter)
		self.label.setFixedWidth(50)

		self.path_edit = QLineEdit()
		self.path_edit.setFocusPolicy(Qt.ClickFocus)  # only accepts mouse clicks

		browse = QPushButton("…")
		move = QPushButton("Move-To")
		
		trash = QPushButton() # 6_6_2
		trash.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon)) # 6_6_2
		trash.setToolTip("Remove This Option (This Move-To-Folder Option Row)") # 6_4 # 6_6_2
		trash.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # 6_4_2
		button_height = 28
		trash.setFixedSize(28, button_height)
		
		# Make other widgets match the height
		self.path_edit.setFixedHeight(button_height)
		self.label.setFixedHeight(button_height)
		browse.setFixedHeight(button_height)
		move.setFixedHeight(button_height)

		# If you want absolute stability across platforms, make the row height stable: # 6_4_2
		self.setFixedHeight(37) # 6_4_2
		# self.setFixedHeight(27) # 6_4_2 ########################################################## Squinch more if you want but it cuts the bottoms of the elements off
		# set that to 27 and you get 34 rows, or leave it at 37 to not cut off the bottoms of the elements

		browse.clicked.connect(self.pick_folder)

		layout = QHBoxLayout(self)
		layout.addWidget(trash) # 6_4
		from PySide6.QtWidgets import QSpacerItem # I don't think I actually wound up using this - I think this line can get deleted

		auto = 	GUI_Builder_helper.cpnt(QCheckBox(),"Auto-swap when main folder is exhausted", (lambda *args, **kwargs: None), 28, button_height,layout, self, 'auto_swap_checkbox') #669
		swap_button=GUI_Builder_helper.btn('⇄','Swap with main folder',(lambda *args, **kwargs: None),28,button_height,layout,self,'swap_button') #669
			
		up_btn=GUI_Builder_helper.btn('▲','Up',lambda: self.cw.move_row(self, -1),28,button_height,layout,self,'up_btn') #669
		dwn_btn=GUI_Builder_helper.btn('▼','Down',lambda: self.cw.move_row(self, 1),28,button_height,layout,self,'dwn_btn') #669

		layout.addWidget(self.path_edit)
		layout.addWidget(self.label)
		layout.addWidget(browse)
		layout.addWidget(move)

		# optionally keep your fixed height, slightly smaller if needed
		# self.setFixedHeight(0)  # or 36.5 if you want to push it
		self.move_button = move
		self.trash_button = trash # 6_4

	def pick_folder(self):
		path = QFileDialog.getExistingDirectory(None, "Select Folder", folder)
		if path:
			self.path_edit.setText(path)
			# Restore focus to parent ControlWindow
			if parent := self.parentWidget():
				parent.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

	def target_path(self) -> Path | None:
		text = self.path_edit.text().strip()
		if not text:
			return None
		p = Path(text)
		if not p.is_absolute():
			p = self.root / p
		return p

# ---------------- Control Window ----------------
from PySide6.QtCore import QTimer
from PySide6.QtCore import QEvent
class ControlWindow(QWidget, LinkedWindowMixin):
	def event(self, e):
		if LinkedWindowMixin.event(self, e):
			return True
		# return super().event(e)
	'''
	def event(self, event):
		if event.type() == QEvent.WindowActivate:
			if hasattr(self, 'paired_window') and self.paired_window:
				self.paired_window.raise_()
				self.paired_window.activateWindow()
		return super().event(event)
	'''
	''' Commented section above is gold - I saved it because if you throw out all the LinkedWindowMixin
		stuff and JUST kept that event override I pasted twice above you get window raising for the ImageWindow
		It's still not perfect because the ControlWindow can never be on top.
	'''
	def closeEvent(self, event): # suppresses warning from below line self.settings_dialog.isVisible() on program close
		QApplication.instance().removeEventFilter(self)
		super().closeEvent(event)
	def eventFilter(self, obj, event):
		from PySide6.QtCore import QEvent
		# ?? If SettingsDialog is open, do NOT intercept keys
		if hasattr(self, "settings_dialog") and self.settings_dialog.isVisible():
			return False
		''' # Alternatively: #from PySide6.QtWidgets import QApplication
		if QApplication.activeModalWidget() is self.settings_dialog:
			return False
		'''
		if event.type() == QEvent.KeyPress:
			self.keyPressEvent(event)
			return True
		elif event.type() == QEvent.KeyRelease:
			self.keyReleaseEvent(event)
			return True
		return super().eventFilter(obj, event)
	def pick_root_folder(self): # 6_2
		path = QFileDialog.getExistingDirectory(self, "Select Image Folder", str(self.root))
		if not path:
			return

		self.root = Path(path)
		self.setWindowTitle(str(self.root)) # 6_6
		self.rebuild_image_list()
		self.index = 0
		self.load_current_image(preserve_zoom=True)
	def refresh_images(self): # 6_2
		# Remember current filename if possible
		current = None
		if self.images and 0 <= self.index < len(self.images):
			current = self.images[self.index].name

		self.rebuild_image_list()
		# Try to stay on same image if it still exists
		if current:
			for i, p in enumerate(self.images):
				if p.name == current:
					self.index = i
					break
			else:
				self.index = min(self.index, max(0, len(self.images) - 1))
		else:
			self.index = 0

		self.load_current_image(preserve_zoom=True)
	def serialize_state(self) -> dict: # 6_3
		# folders
		folder_paths = []
		for row in self.folder_rows:
			text = row.path_edit.text().strip()
			auto_swap = row.auto_swap_checkbox.isChecked() #682 save auto-swap checkboxes
			if text:
				folder_paths.append({"path":text,"auto_swap":auto_swap}) #682 save auto-swap checkboxes

		# current image info
		current_index = self.index
		current_filename = None
		if self.images and 0 <= self.index < len(self.images):
			current_filename = self.images[self.index].name

		# window geometries
		iw = self.image_window.geometry()
		cw = self.geometry()

		# file_types
		file_types_state = {}
		for parent_name, parent_cb in self.settings_dialog.parent_checkboxes.items():
			children = self.settings_dialog.child_checkboxes[parent_cb]
			file_types_state[parent_name] = {
				'parent_checked': parent_cb.isChecked(),
				'children_checked': [cb.isChecked() for cb in children]
			}
		
		
		state = {
			"version": 1,

			"root_folder": str(self.root),

			"folders": folder_paths,

			"current": {
				"index": current_index,
				"filename": current_filename
			},

			"view": {
				"zoom": self.image_window.zoom
			},
			"delay_ms": self.delay_spinbox.value(), #680 save/restore delay
			"move_backward_on_image_move": self.move_backward_checkbox.isChecked(), #681 save/restore move-backward-checkbox
			"windows": {
				"image": {
					"x": iw.x(),
					"y": iw.y(),
					"width": iw.width(),
					"height": iw.height()
				},
				"control": {
					"x": cw.x(),
					"y": cw.y(),
					"width": cw.width(),
					"height": cw.height()
				}
			}
			,"file_types": file_types_state
			,'sort_mode':self.sort_mode
			,"secondary_sort": self.settings_dialog.secondary_sort_combo.currentText()
			,"external_open": {
				"image": self.settings_dialog.image_open_cmd.text()
				,"text": self.settings_dialog.text_open_cmd.text()
			}
			,"centered_arrow_zoom": self.settings_dialog.centered_arrow_zoom_checkbox.isChecked()
			,"move_windows_up": self.settings_dialog.move_windows_up_checkbox.isChecked()
			,"text_scale": self.settings_dialog.text_scale_spin.value()


		}
		return state
	def save_state(self): # 6_3
		path, _ = QFileDialog.getSaveFileName(
			self,
			"Save Session",
			str(self.root / "arlons-file-sorter-session.json"),
			"JSON Files (*.json)"
		)
		if not path:
			return

		state = self.serialize_state()

		try:
			with open(path, "w", encoding="utf-8") as f:
				json.dump(state, f, indent=2)
		except Exception as e:
			print("Failed to save session:", e)
	def restore_state(self): # 6_3
		path, _ = QFileDialog.getOpenFileName(
			self,
			"Restore Session",
			str(self.root),
			"JSON Files (*.json)"
		)
		if not path:
			return

		try:
			with open(path, "r", encoding="utf-8") as f:
				state = json.load(f)
		except Exception as e:
			print("Failed to load session:", e)
			return

		self.apply_state(state)
	def apply_state(self, state: dict): # 6_3
		# ---- version check (non-fatal) ----
		version = state.get("version", 0)
		if version != 1:
			print(f"Warning: session version {version}")

			# ---- file types ----
		file_types_state = state.get("file_types", {})
		for parent_name, data in file_types_state.items():
			parent_cb = self.settings_dialog.parent_checkboxes[parent_name]
			parent_cb.setChecked(data['parent_checked'])
			# Restore children checkboxes
			children = self.settings_dialog.child_checkboxes[parent_cb]
			for cb, checked in zip(children, data['children_checked']):
				cb.setChecked(checked)
		
		self.sort_mode = state.get("sort_mode", "name") # for sort
		self.rebuild_image_list() # for sort
		self.settings_dialog.set_sort_mode(self.sort_mode) # for sort
		
		sec = state.get("secondary_sort", "none")
		self.settings_dialog.secondary_sort_combo.setCurrentText(sec)
		
		external = state.get("external_open", {})
		self.settings_dialog.image_open_cmd.setText(external.get("image", ""))
		self.settings_dialog.text_open_cmd.setText(external.get("text", ""))
		
		self.image_window.set_image(None)

		# ---- root folder ----
		root_path = state.get("root_folder")
		if root_path:
			root = Path(root_path)
			if root.exists():
				self.root = root
				self.setWindowTitle(str(self.root)) # 6_6 
				self.rebuild_image_list()
			else:
				print("Saved root folder does not exist:", root_path)

		# ---- folders ----
		self.clear_folder_rows()

		for folder in state.get("folders", []):
			self.add_folder_row()
			if isinstance(folder, str): #682 save auto-swap checkboxes
				self.folder_rows[-1].path_edit.setText(folder)
			else: #682 save auto-swap checkboxes
				self.folder_rows[-1].path_edit.setText(folder["path"]) #682 save auto-swap checkboxes
				self.folder_rows[-1].auto_swap_checkbox.setChecked(folder.get("auto_swap",False)) #682 save auto-swap checkboxes

		self.index = 0
		
		if self.start_file and self.images:
			try:
				self.index = self.images.index(self.start_file)
			except ValueError:
				self.index = 0
			self.start_file = None
		else:
			# ---- current image ----
			current = state.get("current", {})
			saved_filename = current.get("filename")
			saved_index = current.get("index", 0)

			if saved_filename and self.images:
				for i, p in enumerate(self.images):
					if p.name == saved_filename:
						self.index = i
						break
				else:
					self.index = min(saved_index, len(self.images) - 1)

		# ---- load image first (needed before zoom) ----
		self.load_current_image(preserve_zoom=False)

		# ---- zoom ----
		zoom = state.get("view", {}).get("zoom")
		if isinstance(zoom, (int, float)) and zoom > 0:
			self.image_window.zoom = zoom
			self.image_window.update_view()
			
			
		# ---- delay ---- #680 save/restore delay
		delay = state.get("delay_ms", 0) #680 save/restore delay
		self.delay_spinbox.setValue(delay) #680 save/restore delay
		
		# ---- save/restore move-backward-checkbox ---- #681 save/restore move-backward-checkbox
		self.move_backward_checkbox.setChecked(state.get("move_backward_on_image_move", False))  # default False #681 save/restore move-backward-checkbox
		
		# ---- Centered arrow-zoom
		self.settings_dialog.centered_arrow_zoom_checkbox.setChecked(
			state.get("centered_arrow_zoom", False)
		)
		self.settings_dialog.move_windows_up_checkbox.setChecked(
			state.get("move_windows_up", False)
		)
		LinkedWindowMixin.toggle_window_raising(state.get("move_windows_up", False))
		
		self.settings_dialog.text_scale_spin.setValue(
			state.get("text_scale", 4.0)
		)
		self.settings_dialog.saveInitialState() # almost forgot to add this it is required for cancel to work in the settings dialog
		# ---- window geometry ----
		self.restore_geometry(state.get("windows", {}))
		self.layout().invalidate()
		self.layout().activate()
		self.adjustSize()
		
	def clear_folder_rows(self): # 6_3
		for row in self.folder_rows:
			row.setParent(None)
			row.deleteLater()
		self.folder_rows.clear()
	def restore_geometry(self, windows: dict): # 6_3
		iw = windows.get("image")
		if iw:
			try:
				self.image_window.setGeometry(
					iw["x"], iw["y"], iw["width"], iw["height"]
				)
			except Exception:
				pass

		cw = windows.get("control")
		if cw:
			try:
				self.setGeometry(
					cw["x"], cw["y"], cw["width"], cw["height"]
				)
			except Exception:
				pass
	def remove_folder_row(self, row: FolderRow): # 6_4
		if row not in self.folder_rows:
			return

		idx = self.folder_rows.index(row)

		# remove from layout & UI
		row.setParent(None)
		row.deleteLater()

		# remove from model
		self.folder_rows.pop(idx)

		# re-label remaining rows (numbers + aliases)
		self.relabel_folder_rows()

		# Force layout recalculation
		self.folders_layout.invalidate()	  # marks layout dirty
		self.folders_layout.activate()		# recompute geometry

		# Now resize window vertically only
		self.resize_to_fit_rows()
		
		if idx==1: #676 Grayed-out up/down arrows - potentially two arrows need gray-ing:
			self.folder_rows[1].dwn_btn.setEnabled(False) #676 Grayed-out up/down arrows - gray-out the down for the first
		if idx==len(self.folder_rows)-1: #676 Grayed-out up/down arrows
			self.folder_rows[idx-1].up_btn.setEnabled(False) #676 Grayed-out up/down arrows - gray-out the up for the last
		
	def resize_to_fit_rows(self):
		self.folders_layout.invalidate()
		self.folders_layout.activate()
		new_height = self.folders_layout.sizeHint().height() + self.layout().contentsMargins().top() + self.layout().contentsMargins().bottom()
		self.resize(self.width(), new_height)

	def top_level_margin(self): # 6_4_2
		m = self.layout().contentsMargins() # 6_4_2
		return m.top() + m.bottom() # 6_4_2

	# 6_6_6
	def swap_with_main_folder(self, row: FolderRow):
		target = row.target_path()
		if not target or not target.exists():
			return

		old_root = self.root

		# swap paths
		self.root = target
		row.path_edit.setText(str(old_root.resolve())) # Absolute path

		# reload images from new root
		self.rebuild_image_list()
		self.index = 0

		# update title
		self.setWindowTitle(str(self.root))

		# load image
		self.load_current_image(preserve_zoom=True)
		
	# 6_6_7
	def find_auto_swap_row(self, next=True):
		checked_rows = [r for r in self.folder_rows if r.auto_swap_checkbox.isChecked()]
		if not checked_rows:
			return None
		if next:
			return checked_rows[0]  # first checked folder
		else:
			return checked_rows[-1]  # last checked folder

	def try_auto_swap(self, next=True):
		"""
		Attempt to auto-swap to the next or previous checked folder.

		:param next: True to go to next checked folder, False for previous
		:return: True if a swap occurred, False otherwise
		"""
		row = self.find_auto_swap_row(next=next)  # must update find_auto_swap_row to accept direction
		if not row:
			return

		# disable auto on the row we're about to swap in
		row.auto_swap_checkbox.setChecked(False)

		# perform the swap
		self.swap_with_main_folder(row)
		return True
	def move_row(self, row, delta): # 669
		i = self.folder_rows.index(row)
		j = i + delta
		if j < 0 or j >= len(self.folder_rows):
			return

		self.folder_rows[i], self.folder_rows[j] = \
			self.folder_rows[j], self.folder_rows[i]

		layout = self.folders_layout
		layout.removeWidget(row)
		layout.insertWidget(j, row)
		row.label.setText(self.format_folder_label(j))
		other_row = self.folder_rows[i]
		other_row.label.setText(self.format_folder_label(i))
		
		
		 #676 Grayed-out up/down arrows
		if delta==-1: # An up arrow was clicked
			if j==0: #676 Grayed-out up/down arrows
				row.up_btn.setEnabled(False) #676 Grayed-out up/down arrows
				other_row.up_btn.setEnabled(True) #676 Grayed-out up/down arrows
			if i==len(self.folder_rows)-1: #676 Grayed-out up/down arrows
				row.dwn_btn.setEnabled(True) #676 Grayed-out up/down arrows
				other_row.dwn_btn.setEnabled(False) #676 Grayed-out up/down arrows
		else: # A down arrow was clicked #676 Grayed-out up/down arrows
			if j==len(self.folder_rows)-1: #676 Grayed-out up/down arrows
				row.dwn_btn.setEnabled(False) #676 Grayed-out up/down arrows
				other_row.dwn_btn.setEnabled(True) #676 Grayed-out up/down arrows
			if i==0: #676 Grayed-out up/down arrows
				row.up_btn.setEnabled(True) #676 Grayed-out up/down arrows
				other_row.up_btn.setEnabled(False) #676 Grayed-out up/down arrows
	def sort_files_single_criterion(self, files: list[Path]) -> list[Path]:
		mode = getattr(self, "sort_mode", "name")

		if mode == "name":
			return sorted(files, key=lambda p: p.name.lower())

		elif mode == "mtime":
			return sorted(files, key=lambda p: p.stat().st_mtime)

		elif mode == "ctime":
			return sorted(files, key=lambda p: p.stat().st_ctime)

		elif mode == "size":
			return sorted(files, key=lambda p: p.stat().st_size)

		return files

	def sort_files(self, files: list[Path]) -> list[Path]: # double criterion
		# primary sort (existing behavior)
		mode = getattr(self, "sort_mode", "name")

		def key_for(mode, p: Path):
			if mode == "name":
				return p.name.lower()
			if mode == "mtime":
				return p.stat().st_mtime
			if mode == "ctime":
				return p.stat().st_ctime
			if mode == "size":
				return p.stat().st_size
			if mode == "type":
				return p.suffix.lower()
			return 0

		files = sorted(files, key=lambda p: key_for(mode, p))

		# ?? secondary sort (UI-driven, optional)
		sd = self.settings_dialog
		if hasattr(sd, "secondary_sort_combo"):
			sec = sd.secondary_sort_combo.currentText()
			if sec and sec != "none":
				files = sorted(
					files,
					key=lambda p: key_for(sec, p)
				)

		return files

	def rebuild_image_list(self):
		files = [
			p for p in self.root.iterdir()
			if p.suffix.lower() in self.settings_dialog.allowed_extensions()
		]
		self.images = self.sort_files(files)
		self.index = min(self.index, len(self.images) - 1) if self.images else 0
	def apply_settings(self):
		self.sort_mode = self.settings_dialog.sort_mode()
		self.rebuild_image_list()
		self.refresh_images()

	def __init__(self, image_window: ImageWindow, root: Path, auto_restore_coming_soon: False,start_file: Path | None = None):
		super().__init__()
		LinkedWindowMixin.collect(self)
		self.start_file = start_file
		self.setWindowTitle(str(root)) # 6_6
		self.setFocusPolicy(Qt.StrongFocus)  # <<< Add this line
		self.setFocus()					  # <<< Force focus
		self.installEventFilter(self)
		self.image_window = image_window
		self.root = root
		self.settings_dialog = SettingsDialog(self) # Create the dialog # Moved this line up from below, search it
		
		self.index = 0
		self.sort_mode = self.settings_dialog.sort_mode()
		self.rebuild_image_list()
		if self.start_file and not auto_restore_coming_soon: # retest hh387h8
			try:
				self.index = self.images.index(self.start_file)
			except ValueError:
				# file not found in filtered/sorted list
				self.index = 0
			# self.start_file = None

		# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
		
		self.folder_rows = []

		self.prev_btn = QPushButton("← Previous")
		self.next_btn = QPushButton("Next →")
		self.add_folder_btn = QPushButton("＋ Folder")
		
		self.change_root_btn = QPushButton("Change Image Folder") # 6_2
		self.change_root_btn.clicked.connect(self.pick_root_folder) # 6_2

		self.prev_btn.clicked.connect(self.prev_image)
		self.next_btn.clicked.connect(self.next_image)
		# self.add_folder_btn.clicked.connect(self.add_folder_row) # 6_6_2
		self.add_folder_btn.clicked.connect(self.add_folder_row_plus_open_folder) # 6_6_2

		main = QVBoxLayout(self)
		folder_controls = QHBoxLayout() # 6_2
		
		self.save_btn = QPushButton() # 6_3 #679 Save/Restore Icons
		self.restore_btn = QPushButton() # 6_3 #679 Save/Restore Icons

		self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton)) #679 Save/Restore Icons
		self.restore_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon)) #679 Save/Restore Icons
		self.restore_btn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon)) #679 Save/Restore Icons
		self.save_btn.setIconSize(QSize(16, 16)) #679 Save/Restore Icons
		self.restore_btn.setIconSize(QSize(16, 16)) #679 Save/Restore Icons
		self.save_btn.setToolTip("Save State") # 679 Save/Restore Icons
		self.restore_btn.setToolTip("Restore State") # 679 Save/Restore Icons

		self.save_btn.clicked.connect(self.save_state) # 6_3
		self.restore_btn.clicked.connect(self.restore_state) # 6_3

		folder_controls.addWidget(self.save_btn) # 6_3
		folder_controls.addWidget(self.restore_btn) # 6_3
		
		folder_controls.addWidget(self.change_root_btn) # 6_2
		self.refresh_btn = QPushButton("⟳") # 6_2
		self.refresh_btn.setFixedWidth(40) # 6_2
		self.refresh_btn.setToolTip("Refresh image list") # 6_2
		self.refresh_btn.clicked.connect(self.refresh_images) # 6_2
		folder_controls.addWidget(self.refresh_btn) # 6_2

		# add a label # 668 2
		self.delay_label = QLabel("Slideshow delay (ms):") # 668 2
		folder_controls.addWidget(self.delay_label) # 6_2

		# add a spin box # 668 2
		self.delay_spinbox = QSpinBox() # 668 2
		self.delay_spinbox.setRange(0, 30000)   # 0 ms to 30 seconds # 668 2
		self.delay_spinbox.setValue(0)		 # default 0 # 668 2
		folder_controls.addWidget(self.delay_spinbox) # 6_2
		self.delay_spinbox.setSingleStep(50)   # <- this is the increment
		self.delay_spinbox.setReadOnly(False)   # THIS makes it type-editable #674 type-editable spin-box #674
		self.delay_spinbox.setKeyboardTracking(True)  # optional: immediate value updates #674 type-editable spin-box #674
		self.delay_spinbox.setFocusPolicy(Qt.StrongFocus) #674
		self.delay_spinbox.keyPressEvent = lambda e: print("Line 2890 - Spinny keypress!", e.text()) #674 # 675, next-able spinny
		'''
		# Alternative colors:
		# Neon mint
		background-color: #3AFFA5;

		# Cyber green
		background-color: #00FF7F;

		# Softer lime
		background-color: #7CFC00;

		# Hacker green (terminal vibes)
		background-color: #39FF14;
		
		# Crazy lime: #32CD32
		# Darkened Crazy lime: #22BC22
		'''
		self.delay_spinbox.setStyleSheet("""
		
			selection-background-color: #22BC22;
			selection-color: white;
		
		
		""")

		# Move-back-on-move-to-folder #678
		self.move_backward_checkbox = QCheckBox("Back <- after move") #678
		self.move_backward_checkbox.setToolTip("Back <- after move - Toggles 'Go Back' functionality, after a file is moved (reverse direction)") #678
		folder_controls.addWidget(self.move_backward_checkbox) #678
		
		settings_btn=GUI_Builder_helper.btn('','Settings',lambda:self.settings_dialog.exec(),28,28,folder_controls,self,'settings_btn') #685
		settings_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
		
		folder_controls.addStretch() # 6_2

		main.addLayout(folder_controls)

		nav = QHBoxLayout()
		nav.addWidget(self.prev_btn)
		nav.addWidget(self.next_btn)

		main.addLayout(nav)
		main.addWidget(self.add_folder_btn)

		self.folders_layout = QVBoxLayout()
		self.folders_layout.setSpacing(0)  # smaller spacing between rows (default is ~6) # 6_4_2

		main.addLayout(self.folders_layout)

		if not auto_restore_coming_soon: self.load_current_image()
		
		self.key_timer = QTimer()
		self.key_timer.setInterval(50)  # 50 ms per step
		self.key_timer.timeout.connect(self.on_key_timer)
		self.key_direction = 0  # +1 for next, -1 for prev
		self.has_image = False #672
	# maps Qt.Key_* -> folder index
	KEY_TO_FOLDER = {
		# 1
		# Qt.Key_1: 0, 		#673 #673 #673 #673 #673 #673 #673 #673 #673 #673
		Qt.Key_Slash: 0,

		# ----------------------------------- 	#673 #673 #673 #673 #673 #673 #673 removes number key binding, for use with spinny now
		# 2–8 with aliases  											#673
		Qt.Key_Apostrophe: 1, # Qt.Key_2: 1,  							#673 
		Qt.Key_BracketRight: 2, # Qt.Key_3: 2,   						#673 
		Qt.Key_Backslash: 3, # Qt.Key_4: 3,   							#673 
		Qt.Key_Period: 4, # Qt.Key_5: 4,   								#673 
		Qt.Key_Semicolon: 5, # Qt.Key_6: 5,   							#673 
		Qt.Key_BracketLeft: 6, # Qt.Key_7: 6,   						#673 
		Qt.Key_Comma: 7, # Qt.Key_8: 7,   								#673 

		# continuing sequence  											#673 
		Qt.Key_L: 8, # Qt.Key_9: 8,   									#673 
		Qt.Key_P: 9, # Qt.Key_0: 9,   									#673 

		Qt.Key_Minus: 10, Qt.Key_M: 10,  								#673 
		Qt.Key_Equal: 11, Qt.Key_K: 11,  								#673 
		Qt.Key_QuoteLeft: 12, # Qt.Key_O: 12,  							#673 
		# ----------------------------------- 	#673 #673 #673 #673 #673 #673 #673 removes number key binding, for use with spinny now
		
		Qt.Key_N: 13,
		Qt.Key_J: 14,
		Qt.Key_I: 15,
		Qt.Key_B: 16,
		Qt.Key_H: 17,
		Qt.Key_U: 18,
		Qt.Key_V: 19,
		Qt.Key_G: 20,
		Qt.Key_Y: 21,
		Qt.Key_C: 22,
		Qt.Key_F: 23,
		Qt.Key_T: 24,
		Qt.Key_X: 25,
		Qt.Key_D: 26,
		Qt.Key_R: 27,
		Qt.Key_Z: 28,
		Qt.Key_S: 29,
		Qt.Key_E: 30,
		Qt.Key_A: 31,
		Qt.Key_W: 32,
		Qt.Key_Q: 33,
	}

	def load_current_image(self, preserve_zoom=True):
		total = len(self.images)
		if total == 0:
			self.image_window.label.setText("No images found - Click to Select Folder")
			self.image_window.update_counter(0, 0)
			self.image_window.setMinimumSize(400, 300) # Fix for tiny window on initial open of empty folder 685
			return
		else: # Fix for tiny window on initial open of empty folder 685
			self.image_window.setMinimumSize(400, 300) # Fix for tiny window on initial open of empty folder 685

		self.index = max(0, min(self.index, total - 1))
		pix = self.load_pixmap_for_path(self.images[self.index]) #684
		if not pix: #684
			self.has_image = False #684
			return #684

		# Only set initial zoom if not preserving zoom or first load
		if not preserve_zoom or not self.image_window.has_ever_loaded_image: # fix for zoom restoring/not restoring/obscure zoom bug around the time of filter addition
			# Compute initial zoom to fit screen
			screen_rect = QApplication.primaryScreen().availableGeometry()
			scale_w = (screen_rect.width() - 100) / pix.width()
			scale_h = (screen_rect.height() - 100) / pix.height()
			self.image_window.zoom = min(1.0, min(scale_w, scale_h))  # start <= 1.0

		self.image_window.set_image(pix)
		self.image_window.has_ever_loaded_image = True # fix for zoom restoring/not restoring/obscure zoom bug around the time of filter addition
		
		# Title bar info # 6_2
		filename = self.images[self.index].name # 6_2
		self.image_window.setWindowTitle( # 6_2
			f"{filename}  ({self.index + 1} / {total})"
		) # 6_2

		self.image_window.update_counter(self.index, total)
		self.image_window.repaint()
		if self.image_window.filename:
			self.image_window.filename.setText(self.images[self.index].name)
			self.image_window.filename.adjustSize()
		self.has_image = True #672
	def load_pixmap_for_path(self, path: Path) -> QPixmap | None:#684
		# print("Line 3084 path: ", path)
		if path.suffix.lower() in IMAGE_EXTS: # if path.suffix.lower() not in SettingsDialog.allowed_extensions():
			pixmap = QPixmap(str(path))
			if pixmap.isNull():
				return None
			return pixmap
		elif path.suffix.lower() in TEXT_EXTS:
			# print("TEXT:", path)
			lines = self.read_text_preview(path)
			return self.render_text_to_pixmap(lines)

	def read_text_preview(self, path, top=40, bottom=10, max_bytes=64_000):#684
		# print("Line 3096 path: ", path)
		with open(path, "r", errors="replace") as f:
			content = f.read(max_bytes)

		lines = content.splitlines()

		if len(lines) <= top + bottom:
			return lines

		return (
			lines[:top]
			+ ["", " . . . ", ""]
			+ lines[-bottom:]
		)
	def render_text_to_pixmap(self, lines):#684
	
		scale = self.settings_dialog.text_scale_spin.value()

		
		font = QFont("monospace", 12*scale) # 684 - either scale the whole thing or just the font - this is an option - works - marked oi3j2

		# font = QFont("monospace", 12) # 684 - either scale the whole thing or just the font - this is an option - works - marked oi3j

		metrics = QFontMetrics(font)

		line_height = metrics.height()
		width = max(metrics.horizontalAdvance(line) for line in lines) + 20
		height = line_height * len(lines) + 20

		# width*=scale # Arbitrary, to match larger images #684 # 684 - either scale the whole thing or just the font - this is an option - works - marked oi3j
		# height*=scale # Arbitrary, to match larger images #684 # 684 - either scale the whole thing or just the font - this is an option - works - marked oi3j

		
		pixmap = QPixmap(width, height)
		pixmap.fill(Qt.white)

		painter = QPainter(pixmap)
		# painter.scale(scale, scale) # 684 - either scale the whole thing or just the font - this is an option - works - marked oi3j
		# to expound - to swap from scaling the font to scaling the whole thing, uncomment 4 lines marked oi3j, comment line oi3j2
		# The scale works slightly different for the two options, too - it gets bigger with the image scaling

		painter.setFont(font)
		painter.setPen(Qt.black)

		y = line_height
		for line in lines:
			painter.drawText(10, y, line)
			y += line_height

		painter.end()
		return pixmap
		
	def next_image(self):
		if not self.images:
			if self.try_auto_swap(next=True): #671
				return #671
			return
		self.index += 1 # 6_6_7
		if self.index >= len(self.images): # 6_6_7
			# Auto-swap: move to next checked folder # 6_6_7
			if self.try_auto_swap(next=True): # 6_6_7
				# reset index for new folder # 6_6_7
				self.index = 0 # 6_6_7
			else: # 6_6_7
				# if no other folder, wrap as fallback # 6_6_7
				self.index = 0 # 6_6_7

		self.load_current_image(preserve_zoom=True)

	def prev_image(self):
		if not self.images:
			if self.try_auto_swap(next=False): #671
				return #671
			return
		self.index -= 1 # 6_6_7
		if self.index < 0: # 6_6_7
			# Auto-swap: move to previous checked folder # 6_6_7
			if self.try_auto_swap(next=False): # 6_6_7
				# reset index for new folder to last image # 6_6_7
				self.index = len(self.images) - 1 # 6_6_7
			else: # 6_6_7
				# if no other folder, wrap as fallback # 6_6_7
				self.index = len(self.images) - 1 # 6_6_7

		self.load_current_image(preserve_zoom=True)

	FOLDER_ALIAS_MAP = {
			1: "/",
			2: "\"",
			3: "]",
			4: "\\",
			5: ".",
			6: ";",
			7: "[",
			8: ",",
			9: "L",
			# 10: "0/p", #673
			10: "p", #673
			11: "-/m",
			12: "=/k",
			13: "`/o",
			14: "n",
			15: "j",
			16: "i",
			17: "b",
			18: "h",
			19: "u",
			20: "v",
			21: "g",
			22: "y",
			23: "c",
			24: "f",
			25: "t",
			26: "x",
			27: "d",
			28: "r",
			29: "z",
			30: "s",
			31: "e",
			32: "a",
			33: "w",
			34: "q",
		}
	def add_folder_row_plus_open_folder(self): # 6_6_2
		row = self.add_folder_row() # 6_6_2
		row.pick_folder() # 6_6_2

	def add_folder_row(self):
		idx = len(self.folder_rows)
		# row = FolderRow(self.root) # 669
		row = FolderRow(self.root,self) # 669
		self.folder_rows.append(row)
		self.folders_layout.addWidget(row)

		row.label.setText(self.format_folder_label(len(self.folder_rows)-1)) # 6_4
		row.move_button.clicked.connect(lambda _, i=idx: self.move_to_folder(i))
		
		# 6_4
		row.trash_button.clicked.connect(
			lambda _, r=row: self.remove_folder_row(r)
		) # 6_4
		row.swap_button.clicked.connect( # 6_6_6
			lambda _, r=row: self.swap_with_main_folder(r) # 6_6_6
		) # 6_6_6

		
		if len(self.folder_rows)==1: #676 Grayed-out up/down arrows #676
			row.up_btn.setEnabled(False) #676 Grayed-out up/down arrows # if adding 1 of 1, gray-out up, too #676
		else: #676 Grayed-out up/down arrows
			self.folder_rows[-2].dwn_btn.setEnabled(True) #676 Grayed-out up/down arrows # fix the one that was last #676
		row.dwn_btn.setEnabled(False) #676 Grayed-out up/down arrows # always gray out the last #676
		
		return row # 6_6_2
		
	def format_folder_label(self, index: int) -> str:
		num = index + 1
		alias = self.FOLDER_ALIAS_MAP.get(num, "")
		# return f"{num}{' / ' + alias if alias else ''}" #673
		return f"{'' + alias if alias else ''}" #673

	def relabel_folder_rows(self): # 6_4
		for i, row in enumerate(self.folder_rows):
			row.label.setText(self.format_folder_label(i))
	def move_to_folder(self, idx: int):
		if idx >= len(self.folder_rows):
			print(f"No folder bound to key {idx}")
			return
		if idx >= len(self.folder_rows) or not self.images:
			return

		target = self.folder_rows[idx].target_path()
		if not target:
			return

			
		target.mkdir(parents=True, exist_ok=True)

		src = self.images[self.index]
		
		# 670 fix for: Moving a photo into the same folder renames it
		if src.parent.resolve() == target.resolve(): #670
			return  # already there, do nothing #670
			
		dest = target / src.name
		counter = 1
		while dest.exists():
			dest = target / f"{src.stem}_{counter}{src.suffix}"
			counter += 1
		shutil.move(str(src), str(dest))

		old_index = self.index #678
		del self.images[self.index]
		# choose new index based on checkbox #678
		if self.images and self.move_backward_checkbox.isChecked(): #678
			self.index = max(old_index - 1, 0) #678
				
		if (old_index==0 and self.images and self.move_backward_checkbox.isChecked()) or not self.images: # 6_6_4 auto-refresh if the list is spent
			self.refresh_images() # 6_6_4 auto-refresh if the list is spent
			if (old_index==0 and self.images and self.move_backward_checkbox.isChecked()) or not self.images: # 6_6_7
				self.try_auto_swap() # 6_6_7
				if not self.images: #672
					self.has_image = False #672
		if self.images: # 6_6_4  added this conditional, indented the next line:
			self.load_current_image()

	def closeEvent(self, event):
		self.save_state_to_file()
		super().closeEvent(event)
		if hasattr(self, 'paired_window'):
			self.paired_window.close()
	def save_state_to_file(self):
		auto_file = self.root / "arlons-file-sorter-session.json"
		state = self.serialize_state()
		try:
			with open(auto_file, "w", encoding="utf-8") as f:
				json.dump(state, f, indent=2)
		except Exception as e:
			print("Failed to auto-save session:", e)
	def keyPressEvent(self, event: QKeyEvent):
	
		# --- Ctrl + Arrow = move ImageWindow --- ctrl=5px, ctrl-alt-shift=1px, ctrl-shift=20px
		if event.modifiers() & Qt.ControlModifier:
			key = event.key()

			# step = 20 if (event.modifiers() & Qt.ShiftModifier) else 5 # just ctrl-shift and ctrl, below adds in ctrl-alt-shift
			mods = event.modifiers()
			if mods & Qt.AltModifier:
				step = 1
			elif mods & Qt.ShiftModifier:
				step = 20
			else:
				step = 5

			if key == Qt.Key_Left:
				self.image_window.nudge(-step, 0)
				event.accept()
				return
			elif key == Qt.Key_Right:
				self.image_window.nudge(step, 0)
				event.accept()
				return
			elif key == Qt.Key_Up:
				self.image_window.nudge(0, -step)
				event.accept()
				return
			elif key == Qt.Key_Down:
				self.image_window.nudge(0, step)
				event.accept()
				return		
			
		# Check if a child widget has focus first #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674
		fw = self.focusWidget() #674					 													#674
		if fw is self.delay_spinbox: #674																 	#674
			#675 Next-able spinny - smack in the middle of #674: editable spinny #675 #675 #675 #675 #675 #675 #675
			le = self.delay_spinbox.lineEdit() #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675
			text_len = len(le.text()) #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675
			cursor_pos = le.cursorPosition() #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675
			if event.key() == Qt.Key_Right and cursor_pos == text_len: #675 Next-able spinny #675 #675 #675 #675
				# propagate right arrow to next image #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675
				self.next_image() #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675
				event.accept() #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675
				return #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675
			elif event.key() == Qt.Key_Left and cursor_pos == 0: #675 Next-able spinny #675 #675 #675 #675 #675
				# propagate left arrow to prev image #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675
				self.prev_image() #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675
				event.accept() #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675
				return #675 Next-able spinny #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675 #675

			QSpinBox.keyPressEvent(self.delay_spinbox, event) #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674
			return #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674 #674

		key = event.key()
		
		if key in (Qt.Key_Right, Qt.Key_Left):
			# ignore auto-repeat, only first press counts
			if event.isAutoRepeat():
				return

			# record direction
			self.key_direction = +1 if key == Qt.Key_Right else -1

			# advance once immediately
			if self.key_direction == +1:
				self.next_image()
			else:
				self.prev_image()

			# start timer for repeat
			delay = self.delay_spinbox.value() or 0  # fallback to 0 # 668 2

			if not self.key_timer.isActive():
				self.key_timer.setInterval(delay)  # delay ms per step # 668 2
				self.key_timer.start(300+delay)  # initial delay # 668 2
		elif key == Qt.Key_Up:
			self.image_window.zoom_out(
				cursor_pos=self.image_window.window_center_cursor_pos()
				if self.settings_dialog.centered_arrow_zoom_checkbox.isChecked()
				else None
			)

		elif key == Qt.Key_Down:
			self.image_window.zoom_in(
				cursor_pos=self.image_window.window_center_cursor_pos()
				if self.settings_dialog.centered_arrow_zoom_checkbox.isChecked()
				else None
			)

			
		elif key == Qt.Key_F5: # 6_2
			self.refresh_images() # 6_2
		elif key == Qt.Key_F12: # 6_2
			self.refresh_images() # 6_2
		elif key == Qt.Key_F11: # 6_2
			self.refresh_images() # 6_2
		elif key == Qt.Key_F10: # 6_2
			self.refresh_images() # 6_2
		elif key == Qt.Key_F9: # 6_2
			self.refresh_images() # 6_2
		elif key == Qt.Key_F8: # 6_2
			self.refresh_images() # 6_2
		elif key == Qt.Key_F7: # 6_2
			self.refresh_images() # 6_2
		elif key == Qt.Key_F6: # 6_2
			self.refresh_images() # 6_2
		elif key in self.KEY_TO_FOLDER: # 6_2
			self.move_to_folder(self.KEY_TO_FOLDER[key]) # 6_2
		else:
			super().keyPressEvent(event)

	def keyReleaseEvent(self, event: QKeyEvent):
		key = event.key()
		if key in (Qt.Key_Right, Qt.Key_Left):
			if event.isAutoRepeat():
				return
			# stop repeating
			self.key_timer.stop()
			self.key_direction = 0
		else:
			super().keyReleaseEvent(event)

	def on_key_timer(self):
		# cw = self.paired_window # 6_6_5
		delay = self.delay_spinbox.value() or 0  # fallback to 0 # 668 2
		# first tick after delay: switch to fast repeat
		if self.key_timer.interval() != 50+delay:
			self.key_timer.setInterval(50+delay)

		# repeat in current direction
		if self.key_direction == +1:
			self.next_image()
		elif self.key_direction == -1:
			self.prev_image()
class SettingsDialog(QDialog, LinkedWindowMixin):
	def event(self, e):
		if LinkedWindowMixin.event(self, e):
			return True
		# return super().event(e)
	def sort_mode(self) -> str:
		return self.sort_combo.currentData()
	def set_sort_mode(self, mode: str):
		index = self.sort_combo.findData(mode)
		if index >= 0:
			self.sort_combo.setCurrentIndex(index)
	def get_image_open_command(self):
		return self.image_open_cmd.text().strip()

	def get_text_open_command(self):
		return self.text_open_cmd.text().strip()

	def pick_program(self, line_edit: QLineEdit):
		path, _ = QFileDialog.getOpenFileName(
			self,
			"Select Program",
			"",
			"Programs (*)"
		)
		if path:
			line_edit.setText(path)

	def __init__(self, parent):
		super().__init__(parent)
		LinkedWindowMixin.collect(self)
		self.setWindowTitle("Settings")
		self.setModal(False)
		self.resize(700, 420)

		self.layout = QVBoxLayout(self)
		self.layout.setSpacing(12)

		# -----------------------------
		# Top layer: external open cmds
		# -----------------------------

		# Image open
		self.image_open_cmd = QLineEdit()
		self.image_open_cmd.setPlaceholderText("e.g. wine /path/to/program.exe")
		self.image_open_browse = QPushButton("Browse")
		self.image_open_browse.clicked.connect(
			lambda: self.pick_program(self.image_open_cmd)
		)

		img_open_row = QHBoxLayout()
		img_open_row.addWidget(QLabel("Image open command"))
		img_open_row.addWidget(self.image_open_cmd, 1)
		img_open_row.addWidget(self.image_open_browse)
		self.layout.addLayout(img_open_row)

		# Text open
		self.text_open_cmd = QLineEdit()
		self.text_open_cmd.setPlaceholderText("e.g. notepad++")
		self.text_open_browse = QPushButton("Browse")
		self.text_open_browse.clicked.connect(
			lambda: self.pick_program(self.text_open_cmd)
		)

		txt_open_row = QHBoxLayout()
		txt_open_row.addWidget(QLabel("Text open command"))
		txt_open_row.addWidget(self.text_open_cmd, 1)
		txt_open_row.addWidget(self.text_open_browse)
		self.layout.addLayout(txt_open_row)

		# --------------------------------
		# Filetype checkbox infrastructure
		# --------------------------------

		self.parent_checkboxes = {}
		self.child_checkboxes = {}

		# --------------------------------
		# Bottom layer: two-column layout
		# --------------------------------

		bottom_row = QHBoxLayout()
		bottom_row.setSpacing(16)
		self.layout.addLayout(bottom_row)

		# --------
		# Left col: Text checkboxes
		# --------

		left_col = QVBoxLayout()
		left_col.addStretch()
		bottom_row.addLayout(left_col, 1)

		# ---------
		# Right col: everything else
		# ---------

		right_col = QVBoxLayout()
		right_col.setSpacing(8)

		# These build the checkbox hierarchys
		self.build_filetype_hierarchy("Text", TEXT_EXTS, target_layout=left_col)
		self.build_filetype_hierarchy("Images", IMAGE_EXTS, target_layout=right_col)

		# Image checkboxes

		# Sorting
		self.sort_combo = QComboBox()
		
		items = [
			("Name", "name"),
			("Date modified", "mtime"),
			("Date created", "ctime"),
			("Size", "size"),
			("Type", "type"),
			("None", None),
		]

		for text, key in items:
			self.sort_combo.addItem(text, key)

		right_col.addWidget(QLabel("Sort images by:"))
		right_col.addWidget(self.sort_combo)

		self.secondary_sort_combo = QComboBox()
		items.insert(0, items.pop()) # Moves None to the top for the second search dropdown
		for text, key in items:
			self.secondary_sort_combo.addItem(text, key)

		right_col.addWidget(QLabel("Secondary sort:"))
		right_col.addWidget(self.secondary_sort_combo)

		# Text scale
		self.text_scale_spin = QDoubleSpinBox()
		self.text_scale_spin.setRange(0.25, 8.0)
		self.text_scale_spin.setSingleStep(0.25)
		self.text_scale_spin.setValue(4.0)
		'''
		# Alternative colors:
		# Neon mint
		background-color: #3AFFA5;

		# Cyber green
		background-color: #00FF7F;

		# Softer lime
		background-color: #7CFC00;

		# Hacker green (terminal vibes)
		background-color: #39FF14;
		
		# Crazy lime: #32CD32
		# Darkened Crazy lime: #22BC22
		'''
		self.text_scale_spin.setStyleSheet("""
		
			selection-background-color: #22BC22;
			selection-color: white;
		
		
		""")

		right_col.addWidget(QLabel("Text scale factor"))
		right_col.addWidget(self.text_scale_spin)

		# Arrow zoom preference (moved here)
		self.centered_arrow_zoom_checkbox = QCheckBox("Arrow zoom stays centered")
		right_col.addWidget(self.centered_arrow_zoom_checkbox)

		# Move windows up
		self.move_windows_up_checkbox = QCheckBox("Move windows up (experimental)")
		self.move_windows_up_checkbox.toggled.connect(LinkedWindowMixin.toggle_window_raising)
		right_col.addWidget(self.move_windows_up_checkbox)

		right_col.addStretch()

		# Buttons (bottom-right)
		buttons = QDialogButtonBox(
			QDialogButtonBox.Ok |
			QDialogButtonBox.Cancel |
			QDialogButtonBox.Apply
		)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		buttons.button(QDialogButtonBox.Apply).clicked.connect(
			self.apply_action_button_action
		)

		right_col.addWidget(buttons)

		bottom_row.addLayout(right_col, 1)

		# -----------------------------
		# Initial state snapshot
		# -----------------------------

		self.saveInitialState()

	def saveInitialState(self):
		self._initial_state = {
			parent: {
				"parent_state": parent.checkState(),
				"children": [cb.isChecked() for cb in children],
			}
			for parent, children in self.child_checkboxes.items()
		}
		self._initial_state["ui"] = {
			"sort_mode": self.sort_mode if hasattr(self, "sort_mode") else None,
			"secondary_sort": self.secondary_sort_combo.currentText(),
			"external_open_image": self.image_open_cmd.text(),
			"external_open_text": self.text_open_cmd.text(),
			"centered_arrow_zoom": self.centered_arrow_zoom_checkbox.isChecked(),
			"move_windows_up": self.move_windows_up_checkbox.isChecked(),
			"text_scale": self.text_scale_spin.value(),
		}

	def apply_action_button_action(self):
		self.saveInitialState();
		self.parent().apply_settings()
	def accept(self):
		self.apply_action_button_action()
		super().accept()
	def reject(self):
		# restore original checkbox states
		for parent, children in self.child_checkboxes.items():
			original = self._initial_state.get(parent)
			if not original:
				continue
			# restore parent
			parent.blockSignals(True)
			parent.setCheckState(original["parent_state"])
			parent.blockSignals(False)
			for cb, checked in zip(children, original["children"]):
				cb.blockSignals(True)
				cb.setChecked(checked)
				cb.blockSignals(False)

		ui = self._initial_state.get("ui", {})

		if "secondary_sort" in ui:
			self.secondary_sort_combo.setCurrentText(ui["secondary_sort"])

		if "external_open_image" in ui:
			self.image_open_cmd.setText(ui["external_open_image"])

		if "external_open_text" in ui:
			self.text_open_cmd.setText(ui["external_open_text"])			

		if "centered_arrow_zoom" in ui:
			self.centered_arrow_zoom_checkbox.setChecked(ui["centered_arrow_zoom"])
			
		if "move_windows_up" in ui:
			self.move_windows_up_checkbox.setChecked(ui["move_windows_up"])
			LinkedWindowMixin.toggle_window_raising(ui["move_windows_up"])

		if "text_scale" in ui:
			self.text_scale_spin.setValue(ui["text_scale"])

		self.parent().apply_settings() # This doesn't cancel apply, it cancels what's happened since
		super().reject()

	def build_filetype_hierarchy(self, parent_name: str, extensions: list[str],target_layout=None):
		if target_layout is None:
			target_layout = self.layout

		parent_cb = QCheckBox(parent_name)
		parent_cb.setChecked(True)
		self.parent_checkboxes[parent_name] = parent_cb  # optional: keep name mapping
		# self.layout.addWidget(parent_cb)
		target_layout.addWidget(parent_cb)

		children = []
		child_layout = QVBoxLayout()
		for ext in extensions:
			cb = QCheckBox(ext)
			cb.setChecked(True)
			children.append(cb)
			child_layout.addWidget(cb)

			# Connect child to update parent
			cb.stateChanged.connect(lambda _, p=parent_cb: self.update_parent_from_children(p))

		# Key by checkbox object, not string
		self.child_checkboxes[parent_cb] = children

		# Parent updates children
		parent_cb.stateChanged.connect(lambda state, p=parent_cb: self.on_parent_changed(p, state))

		# Indent children visually
		container = QWidget()
		container.setLayout(child_layout)
		container.setContentsMargins(20, 0, 0, 0)
		target_layout.addWidget(container)

	def on_parent_changed(self, parent_cb, state):
		"""Parent clicked: select/unselect children and enable/disable them."""
		parent_cb.setTristate(False)
		children = self.child_checkboxes[parent_cb]
		if state == 2:  # Checked
			for cb in children:
				cb.blockSignals(True)
				cb.setChecked(True)
				cb.setEnabled(True)  # Only parent click enables children
				cb.blockSignals(False)
		elif state == 0:  # Unchecked
			for cb in children:
				cb.blockSignals(True)
				cb.setChecked(False)
				cb.setEnabled(True)  # Keep children enabled for user to re-check
				cb.blockSignals(False)
		# No PartiallyChecked possible because tristate=False

	def update_parent_from_children(self, parent_cb):
		"""Children clicked: update parent to reflect partial state."""
		children = self.child_checkboxes[parent_cb]  # ? works now
		num_checked = sum(cb.isChecked() for cb in children)
				
		if num_checked == 0:
			parent_cb.setCheckState(Qt.Unchecked)
		elif num_checked == len(children):
			parent_cb.setCheckState(Qt.Checked)
		else:
			parent_cb.setCheckState(Qt.PartiallyChecked)
			if parent_cb.checkState()==Qt.Checked or parent_cb.checkState()==Qt.Unchecked: # bug fix, doesn't fire above until second click, for some reason, these two lines fix that.
				parent_cb.setCheckState(Qt.PartiallyChecked) # Without two here it doesn't work the first click! This is the fix! The conditional dampens the pain a bit.

	def allowed_extensions(self) -> set[str]:
		"""Return currently enabled extensions for scanning"""
		exts = set()
		for parent, children in self.child_checkboxes.items():
			if parent.checkState() != Qt.Unchecked:
				for cb in children:
					if cb.isChecked():
						exts.add(cb.text())
		return exts

# ---------------- Main ----------------
class ImageSorter():
	@staticmethod
	def main():
		app = QApplication(sys.argv)

		arg_path = Path(sys.argv[1]).expanduser().resolve()

		start_file = None

		if arg_path.is_file():
			start_file = arg_path
			root = arg_path.parent
		else:
			root = arg_path
	

		image_window = ImageWindow()
		auto_file = root / "arlons-file-sorter-session.json" # 6_5
		AUTO_RESTORE_ENABLED = "--no-autorestore" not in sys.argv
		control_window = ControlWindow(image_window, root,(AUTO_RESTORE_ENABLED and auto_file.exists()),start_file=start_file)
		
		app.installEventFilter(control_window) # key bindings when control window isn't in front
		
		if AUTO_RESTORE_ENABLED and auto_file.exists(): # 6_5
			try: # 6_5
				with open(auto_file, "r", encoding="utf-8") as f: # 6_5
					state = json.load(f) # 6_5
				control_window.apply_state(state) # 6_5
				print("Session auto-restored.") # 6_5
			except Exception as e: # 6_5
				print("Failed to auto-restore session:", e) # 6_5
				
		image_window.paired_window = control_window
		control_window.paired_window = image_window

		image_window.show()
		control_window.show()
		
		sys.exit(app.exec())

if __name__ == "__main__":
	ImageSorter.main()
