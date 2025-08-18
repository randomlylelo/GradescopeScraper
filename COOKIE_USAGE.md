# Cookie Authentication Usage

This modified version of GradescopeScraper now supports cookie-based authentication using Netscape format cookie files, which is useful for SSO users.

## How to Use Cookie Authentication

### Step 1: Export Cookies from Your Browser

1. Log into Gradescope via SSO in your browser
2. Use a browser extension to export cookies in Netscape format to `all_cookies.txt`
   - Chrome: "Get cookies.txt CLEAN" extension
   - Firefox: "cookies.txt" extension

### Step 2: Run the Script

Simply run:
```bash
python gradescope.py
```

The script will automatically:
- Look for `all_cookies.txt` in the same directory
- If found, use cookie authentication
- If not found, fall back to username/password login

## Notes

- The script automatically filters for gradescope.com cookies
- If cookie authentication fails, it falls back to username/password
- Cookies expire, so you may need to refresh them periodically
- The script creates one folder per class with all your submitted files
- Works with any browser extension that exports Netscape format cookies