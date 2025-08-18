import mechanize
from tqdm import tqdm

try:
    from http.cookiejar import LWPCookieJar
except ImportError:
    from cookielib import LWPCookieJar
import html2text
from bs4 import BeautifulSoup
import os

# Settings (you can either specify these here or leave blank and you will be prompted later)
g_user = ""
g_pwd = ""
g_cookie_file = "all_cookies.txt"  # Default cookie file (Netscape format)

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

br.addheaders = [('User-agent', 'Chrome')]

dir_path = os.path.dirname(os.path.realpath(__file__))

def load_cookies_from_file(cookie_file_path):
    """Load cookies from a Netscape format file and add them to the browser"""
    try:
        with open(cookie_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line.startswith('#') or not line:
                    continue
                
                # Parse Netscape format: domain, domain_flag, path, secure, expiration, name, value
                parts = line.split('\t')
                if len(parts) >= 7:
                    domain, domain_flag, path, secure, expiration, name, value = parts[:7]
                    
                    # Only load gradescope cookies
                    if 'gradescope.com' in domain:
                        br._ua_handlers['_cookies'].cookiejar.set_cookie(
                            mechanize.Cookie(
                                version=0,
                                name=name,
                                value=value,
                                port=None,
                                port_specified=False,
                                domain=domain,
                                domain_specified=True,
                                domain_initial_dot=domain.startswith('.'),
                                path=path,
                                path_specified=True,
                                secure=secure.upper() == 'TRUE',
                                expires=None,
                                discard=True,
                                comment=None,
                                comment_url=None,
                                rest={}
                            )
                        )
        return True
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return False

print("Gradescope scraper, by Aaron Becker (also credit to YimengYang for original Python 2 implementation)")
print("Modified to support Netscape cookie authentication for SSO users")
print("------------------------")
print("This script will create one folder per class, containing all of the files you've submitted for that class.")
print("Your current directory (that all the class folders will be created in) is: {}".format(dir_path))
print("Place your exported cookies in 'all_cookies.txt' for SSO authentication")
print("------------------------")

# Try to use cookie file if it exists
use_cookies = False
if os.path.exists(g_cookie_file):
    print("Step 1) Loading cookies and getting class list...")
    if load_cookies_from_file(g_cookie_file):
        print("Cookies loaded successfully!")
        br.open('https://gradescope.com/account')
        use_cookies = True
    else:
        print("Failed to load cookies, falling back to username/password authentication")

if not use_cookies:
    print("Step 1) Logging into Gradescope and getting class list...\nYou will be prompted for your username and password")
    # The site we will navigate into, handling it's session
    br.open('https://gradescope.com/login')
    base_url = "https://gradescope.com"
    # View available forms
    for f in br.forms():
        # Select the second (index one) form (the first form is a search query box)
        br.select_form(nr=0)

        if not g_user:
            g_user = input("Enter your Gradescope username: ")
        if not g_pwd:
            g_pwd = input("Enter your Gradescope password: ")

        # User credentials
        br.form['session[email]'] = g_user
        br.form['session[password]'] = g_pwd

        # Login
        br.submit()
        break

base_url = "https://gradescope.com"
soup = BeautifulSoup(br.open('https://gradescope.com/account').read(), "html.parser")
    
# First, find instructor courses to skip
instructor_section = soup.find('h2', string='Instructor Courses')
instructor_courses = []
if instructor_section:
    # Get the next div after instructor header that contains course boxes
    current = instructor_section.find_next_sibling()
    while current:
        if current.name == 'h2' and 'Student Courses' in current.get_text():
            break
        if current.find('a', {'class':'courseBox'}):
            boxes = current.find_all('a', {'class':'courseBox'})
            for box in boxes:
                instructor_courses.append(box.find("h3").text)
        current = current.find_next_sibling()

# Now find student courses and organize by semester
course_data = {}
skipped_instructor_courses = instructor_courses.copy()

# Find the Student Courses section and parse by semester  
student_section = soup.find('h2', string='Student Courses')
if student_section:
    # Find the courseList div that contains all student courses
    course_list = student_section.find_next_sibling('div', {'class': 'courseList'})
    if course_list:
        # Find all term headers and their corresponding course containers
        term_divs = course_list.find_all('div', {'class': 'courseList--term'})
        
        for term_div in term_divs:
            semester_name = term_div.get_text().strip()
            course_data[semester_name] = {}
            
            # Find the next sibling which should be the courses for this term
            courses_container = term_div.find_next_sibling('div', {'class': 'courseList--coursesForTerm'})
            if courses_container:
                # Get all course boxes in this semester
                boxes = courses_container.find_all('a', {'class': 'courseBox'})
                for box in boxes:
                    course_name = box.find("h3").text
                    if course_name not in instructor_courses:
                        n_clean = course_name.replace("/", " ")
                        course_data[semester_name][n_clean] = box.get("href")

# Fallback: if no semester organization found, get all student courses
if not course_data:
    course_data = {"All Student Courses": {}}
    all_course_boxes = soup.find_all('a', {'class':'courseBox'})
    for box in all_course_boxes:
        course_name = box.find("h3").text
        if course_name not in instructor_courses:
            n_clean = course_name.replace("/", " ")
            course_data["All Student Courses"][n_clean] = box.get("href")

if skipped_instructor_courses:
    print("Found instructor courses, skipping:")
    for course in skipped_instructor_courses:
        print(f"  - {course}")

print("Student classes read from your Gradescope account:")
for semester, courses in course_data.items():
    if courses:  # Only show semesters with courses
        print(f"{semester}:")
        for course_name in courses.keys():
            print(f"  - {course_name}")

if not input("Do you want to continue and download all content? (yY/nN)").lower() == "y":
    print("Exiting. Have a good day :)")
    exit()

print("Step 2) Downloading all content (this may take a while)...")

# Create main backup directory
backup_dir = "gradescope_backup"
if not os.path.exists(backup_dir):
    os.mkdir(backup_dir)

# Process each semester
for semester, courses in course_data.items():
    if not courses:  # Skip empty semesters
        continue
    
    # Create semester directory
    semester_clean = semester.replace("/", "_").replace(" ", "_")
    semester_path = os.path.join(backup_dir, semester_clean)
    if not os.path.exists(semester_path):
        os.mkdir(semester_path)
    
    print(f"Processing {semester}...")
    
    # Process each course in this semester
    for k, v in courses.items():
        k_clean = k.replace(" ", "_")  # ensure that filename is valid
        course_path = os.path.join(semester_path, k_clean)
        
        if not os.path.exists(course_path):
            os.mkdir(course_path)
        else:
            print("Dir {} exists, skipping".format(course_path))
            continue
            
        course_soup = BeautifulSoup(br.open(base_url+ v).read(), "html.parser")
        os.chdir(course_path)
        assignment_table = course_soup.find('table', {'class':'table'})
        assignment_links = {}
        for head in assignment_table.find_all("th"):
            a_res = head.find("a")
            if a_res:
                assignment_links[a_res.get("aria-label").split(' ', 1)[1]] = a_res.get("href")

        if (len(assignment_links) == 0):
            print("No assignments found for {}".format(k))
            os.chdir(dir_path)  # Return to script directory
            continue

        print("{}'s assignments:".format(k))
        for aName in assignment_links.keys():
            print(aName)
        print("Now downloading all assignments in '{}' (this may take a while)...".format(k))

        for name, l in tqdm(assignment_links.items()):
            assignment_soup = BeautifulSoup(br.open(base_url+l).read(), "html.parser")
            a_res = assignment_soup.find_all("a", {"class": "actionBar--action"})
            download_link = base_url + l + ".pdf"
            for a in a_res:
                tmp = a.get("href")
                if tmp:
                    download_link = base_url + tmp
                    break
            orig_filename = download_link.split("/")[-1]
            extension = orig_filename.split(".")[-1]
            name = name.replace("/", " ")
            try:
                br.retrieve(download_link,'{}.{}'.format(name, extension))[0]
            except mechanize.HTTPError as e:
                print("\nGot error code {} while retreiving: {}".format(e.code, name))
        os.chdir(dir_path)  # Return to script directory
        print("Finished downloading all assignments for {}".format(k))

print("Finished downloading everything, have a good day :)")
