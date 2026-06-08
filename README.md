# Mobile Canvas Report & Image Processing Engine (`reshape_images.py`)

A high-performance, GUI-free report automation framework and image conversion system written in Python. This script is engineered specifically to execute flawlessly in headless server spaces and resource-constrained mobile IDEs (such as Pydroid 3 on Android) without triggering system layout frameworks or display-activation crashes.

## 🚀 Key Architectural Features

- **Undercover Headless Execution:** Employs a strict, background-locked mapping layer that loads `matplotlib` using custom undercover mechanics (`__import__`). By forcing the `Agg` backend at the absolute top of compilation, the module renders chart graphics entirely in-memory without ever demanding an interactive device frame or throwing backend runtime errors.
- **Pixel-Perfect Smart Wrapping Engine:** Features a dynamic text boundary layout loop utilizing PIL (Pillow) native pixel-width evaluation (`draw.textlength()`). Instead of blindly splitting lines based on hardcoded character counts—which chops words awkwardly—this system tracks the boundary constraints of your typography down to the exact pixel, ensuring sentences wrap naturally only at real spacing gaps.
- **Dynamic Structural Layout:** Supports multi-line title heights, image-embedded asset rendering, direct file-path parsing (`"bar.png"`), and elegant summary-only layout formatting. The canvas margins and divider markers dynamically slide down on the fly based on text volume to completely eliminate overlap risks.
- **Native Matrix System:** Includes a zero-dependency table rendering sub-block that builds structured data frames pixel-by-pixel using vector shapes, entirely removing heavy analysis libraries during visual slide assembly.
- **Format Conversion Framework:** Features a resilient image processing block (`convert_image`) that safely parses multi-format graphics (`PNG`, `JPG`, `JPEG`, `PDF`) into target color channels, dynamically purging alpha channels (`RGBA`/`P`) to output premium standalone files.

## 🛠️ Module API Overview

### 1. `JPEGReportBook` Class
The core rendering layout engine used to compile your slate-dark portfolio slides.

```python
from reshape_images import JPEGReportBook

# Initialize the layout manager
book = JPEGReportBook(output_dir="Reports", github_url="[https://github.com/Mpho048](https://github.com/Mpho048)")

# Slide Type A: Summary Text + Direct Image Path
book.add_graph_page(image_path="bar.png", title="Your Main Title", summary="Your analysis paragraph here...")

# Slide Type B: Text Only (The canvas shifts up automatically)
book.add_graph_page(image_path=None, title="Executive Overview", summary="This slide automatically centers text details...")

# Slide Type C: Native Data Matrix Grid
book.add_table_page(dataframe, title="Metrics Table", summary="Statistical matrix breakdown...")
