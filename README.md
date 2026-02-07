# arlons-file-sorter
# Arlon's File Sorter (PySide6 / Qt)

Usage: arlons-file-sorter.py [path-to-image-folder]

A fast, keyboard- and mouse-driven photo sorting tool for Linux.

The program displays images from a directory one at a time, allows
zooming (persistent between images), and lets you quickly move images
into user-defined folders using buttons or number keys.

Designed for Linux, launched from the shell.

---
## License

This project is licensed under the GNU General Public License v3 (GPLv3).
See the [LICENSE](LICENSE) file for details.

## Features

- Displays images one at a time
- Persistent zoom (mouse wheel or keyboard)
- Next / Previous navigation
- Fast key-repeat navigation (hold arrow keys)
- Move images into folders instantly (buttons or number keys)
- Dynamic list of destination folders
- Image index overlay (e.g., `3 / 25`)
- Two windows: Image window + Control window (freely movable)
- Slideshow via mouse buttons, middle-click toggle, or holding (key-repeat) arrow buttons

---

# Why? Why This Program Exists ❓🤖

**Why make another program for viewing and sorting files?**  
Because **this one does both — better than anything else.** 🏆

---

## ⚡ Key Features

- **View & Sort Simultaneously 🖼️📂**  
  Flip through images or text files like a slideshow, and move them into folders **as you go**.

- **Fast Navigation ⏩**  
  Arrow keys, mouse buttons, or holding them down lets you zip through files **at lightning speed**.

- **Folder Shortcuts 🔤**  
  Assign letters to destination folders, then move files instantly as you browse. Sorting has never been this intuitive.

- **Hands-Free Slideshow 🎞️**  
  Press the mouse wheel to start an automatic slideshow — zoom works seamlessly **while running**.

- **Zoom & View 🔍**  
  Zoom works during both manual and automatic slideshows. Ctrl-drag lets you move the window if it goes off-screen.

- **Customizable Settings ⚙️**  
  Configure behavior to your workflow — everything is tweakable.

- **OS Integration 💻**  
  Open folders or files directly in the program. Use a secondary app for certain files with Ctrl+Right-Click. Double-click images to open instantly.

---

## 💡 Why It’s Unique

- No other program I know of lets you **advance through a folder and sort into multiple folders at the same time**.  
- Faster, smoother zoom than most image viewers.  
- Built with **intent, ferocity, and completion** — a “one giant anti-splosion” of functionality.  

---

## 🚀 TL;DR

**It’s easier. Faster. More capable.**  
If you want to browse, view, and sort files **without switching programs**, this is the tool you’ve been waiting for.  
There are minor trade-offs (like the title bar occasionally disappearing when zoomed in), but everything is predictable, tweakable, and intentional.  

---

## Usage / Controls

### Navigation
- **Left / Right arrow**: Previous / Next image
- **Hold arrow keys**: Rapid navigation (key-repeat)
- **Mouse wheel**: Zoom in / out (persistent between images)
- **Right-click**: Next image (hold for rapid slideshow)
- **Left-click**: Previous image (hold for rapid slideshow)

### Slideshow
- **Middle mouse button (rolly wheel click)** cycles:
  - Forward slideshow
  - Stop
  - Reverse slideshow
  - Stop
- Slideshow speed is controlled by the delay field (milliseconds)

### Sorting
- Click folder buttons or use number keys to move the current image
- Images are moved immediately (no copy)
- Folder list can be reordered with up/down arrows

### Auto-swap / Queue (if enabled)
- Checked folders participate in automatic swapping
- When the current folder is exhausted, the next checked folder is loaded automatically

---

## Window Layout

The application uses two independent windows:

- **Image Window** – displays the current image
- **Control Window** – folder controls, navigation, and status

The windows are intentionally decoupled so they can be placed on different monitors
or arranged freely without constraining workflow.

---

## Session Restore

The application automatically saves and restores session state, including:
- Selected folders
- Folder order
- Current image index
- UI state

Restarting the program will resume where you left off.

---

## Design Philosophy

This tool is intentionally:
- Fast
- Keyboard- and mouse-driven
- Minimalist

It is **not** a photo management database or catalog.
Files are moved directly on disk, and no metadata is written.

---
### XFCE Integration (Optional)

ImageSorter integrates with Thunar via a custom right-click action.

To enable:
1. Open Thunar
2. Edit → Configure custom actions
3. Add a new action:
   - Command: /home/knoppix/bin/image-sorter %f
   - Appearance: Directories
---
## Requirements

- Python 3.12+
- PySide6

---

## Installation

```bash
# System dependencies
sudo apt update
sudo apt install python3-venv python3-full libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install PySide6

More detailed installation:
# dnf:
# sudo dnf install libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 python3-venv python3-full;python3 -m venv venv;source venv/bin/activate;pip install PySide6

# apt:
# sudo apt install libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 python3-venv python3-full;python3 -m venv venv;source venv/bin/activate;pip install PySide6

Run:
$ source ~/all/docs/txt/programs/python/file-sorter-1/venv/bin/activate;python3 /home/knoppix/all/docs/txt/programs/python/file-sorter-1/arlons-file-sorter.py ~/Desktop/drone/100MEDIA/
```
---

## More:
New & Updated Features
🗂 Advanced Sorting

Primary sort options:

- Name

- Date modified

- Date created

- File size

- File type

Secondary (dual) sort:

Optional second-level sort applied after the primary sort

Enables combinations like Type → Name or Date modified → Name

Sorting updates immediately when settings are applied

Sort preferences are saved to and restored from the session JSON


---

## 🖼 Navigation & Viewing Features and Improvements

- Arrow-key navigation between images/files

- Arrow-key zooming with optional centered zoom behavior

- When enabled, zooming keeps the image center fixed on screen

- Configurable via Settings dialog

- Mouse-wheel zoom remains cursor-centered

- Optional preference for future window-movement behavior (ctrl-drag groundwork added)


---

## 📝 Text File Viewing Capabilities and Enhancements

- Text files are viewable alongside images

- Configurable text scale factor - Adjustable via Settings dialog

- Text scale preference is saved/restored per session


---

## 🔗 External Program Integration

Ctrl + Right Click on a file opens it in an external program

Separate configurable commands for:

- Image files

- Text files

Commands support arbitrary launch syntax
(e.g. wine /path/to/notepad++.exe)

Program paths are:

- Editable directly as text

- Selectable via file picker

- Settings are saved and restored via session JSON

⚙ Settings Dialog Improvements

Added Apply button (non-modal, live updates)

Cancel reliably restores all prior settings, including:

- Checkboxes

- Sort selections

- External program fields

- Numeric preferences

Settings are treated as UI state rather than mirrored object state where possible, reducing duplication and bugs


---

## 💾 Session Restore & Startup Behavior

Full session auto-restore support:

- Folder

- File index

- Sorting preferences

- View settings (zoom, scale, etc.)

Program can now be launched with:

- A folder path (original behavior)

- A file path

- Automatically opens the file’s parent folder

- Selects that file in the viewer

Overrides only the saved file index (not the rest of the session)


---

## 🖥 Desktop Integration (Linux)

Can be registered as a default image viewer

Launches correctly when opening an image from the file manager

Uses a wrapper script to activate the Python virtual environment automatically

---

# 🙏 Thank You for Trying! 🎉🖖

Thank you for **checking out Arlon’s File Sorter**!  
Whether you’re an image ninja 🥷, a text wizard 🧙‍♂️, or just a file organization enthusiast 📂✨, we hope this program makes your life **easier, faster, and more fun**.  

---

## 🌟 Contributions & Ideas Welcome 💡🛠️

- Think of a way to make navigation smoother?  
- Found a tiny bug 🐛?  
- Have a brilliant idea to add even more hands-on control?  

Feel free to **fork, tweak, or improve** the program!  
Even the tiniest improvement helps make **the handiest file sorting + image viewing program known to advanced civilization** 🚀🪐.  

---

## 🔗 Stay in Touch & Share

- Open issues, submit pull requests, or drop suggestions.  
- Spread the word if you love it ❤️ — the more people using it, the more epic it gets.  

---

### ⚡ TL;DR

**You tried it. You improved it. You mastered it.**  
Thanks for making this little slice of file-viewing greatness part of your workflow! 🌌✨🎉  


