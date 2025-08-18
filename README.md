# GradescopeScraper

Python script that downloads all your Gradescope submissions and feedback, organized by semester.

No idea why they don't have a "Download All" button it's really annoying.

Inspired by Python 2.x script written by YimengYang, found [here](https://github.com/YimengYang/gradescope)

## Quick Start

### Option 1: Cookie Authentication (Recommended for SSO users)

1. **Install dependencies:**
   ```bash
   pip3 install mechanize tqdm html2text bs4
   ```

2. **Export your browser cookies:**
   - Log into Gradescope via SSO in your browser
   - Install a cookie export extension:
     - **Chrome:** "Get cookies.txt CLEAN" extension
   - Export cookies to `all_cookies.txt` in the script directory

3. **Run the scraper:**
   ```bash
   python3 gradescope.py
   ```

### Option 2: Username/Password Authentication

1. **Install dependencies:**
   ```bash
   pip3 install mechanize tqdm html2text bs4
   ```

2. **Run the scraper:**
   ```bash
   python3 gradescope.py
   ```
   
3. **Enter credentials when prompted**

## Features

- **Automatic SSO support** - Works with institutional Single Sign-On
- **Smart organization** - Creates folder structure like:
  ```
  gradescope_backup/
  ├── Fall_2024/
  │   ├── CS_101/
  │   └── Math_200/
  ├── Spring_2024/
  │   └── Physics_150/
  └── [Other_Semesters]/
  ```
- **Instructor course filtering** - Only downloads your student courses
- **Progress tracking** - Shows download progress with progress bars
- **Error handling** - Graceful handling of network issues and missing files

## Notes

- The script automatically skips instructor courses and only downloads student submissions
- Cookies expire periodically, so you may need to re-export them
- All downloaded files include your submissions, feedback, and rubric annotations
- The script creates one folder per class with all submitted assignments
