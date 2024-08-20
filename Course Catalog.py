import logging
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Wrappers.Courses import Courses
from Wrappers.Professors import Professors
from courseEmbedings import generate_embeddings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File handler for logger to a file
file_handler = logging.FileHandler('course_catalog.log', mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))


# Add handlers to logger
logger.addHandler(file_handler)


options = Options()
# options.add_argument('--headless=new')


class CourseCatalog:
    def __init__(self):
        logger.info("Initializing the CourseCatalog class.")
        self._driver = Chrome(options=options)
        self._wait = WebDriverWait(self._driver, 10)
        self._obfuscated_courses = []  # courses that are no longer being actively taught

    def get_course_data(self):
        logger.info("Starting to get course data for all professors.")
        all_professors = Professors.get_all(Professors.Cols.FACULTY_ID)
        for professor in all_professors:
            logger.debug(f"Scraping courses for professor with FACULTY_ID: {professor[Professors.Cols.FACULTY_ID]}")
            self.scrape_courses(professor[Professors.Cols.FACULTY_ID])
        logger.info("Finished getting course data.")
        self._driver.close()

    def scrape_courses(self, faculty_id):
        logger.info(f"Scraping courses for faculty ID: {faculty_id}")
        self._driver.get(f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={faculty_id}")
        self.wait_for_element(By.ID, 'facultyEvaluations')
        faculty_courses = self.fetch_faculty_courses()

        position = 0
        while position < len(faculty_courses):
            course = faculty_courses[position]
            anchor = course.find_element(By.TAG_NAME, 'a')
            spans = anchor.find_elements(By.TAG_NAME, 'span')

            code = self.extract_course_code(spans)
            title = self.extract_course_title(spans)
            description = None
            prereqs = None

            logger.debug(f"Checking if course {code} exists in the database.")
            db_course = Courses.get_single_record({Courses.Cols.CODE: code}, Courses.Cols.CODE)

            if db_course:
                logger.debug(f"Skipping course {code} because it already exists in the database.")
                position += 1
                continue

            if code not in self._obfuscated_courses:
                description, prereqs = self.get_description_and_prereqs(code)
                if description and prereqs:
                    logger.debug(f"Inserting course {code} into the database.")
                    Courses.insert({Courses.Cols.CODE: code, Courses.Cols.PREREQS: prereqs,
                                    Courses.Cols.DESCRIPTION: description, Courses.Cols.TITLE: title,
                                    Courses.Cols.EMBEDDING: generate_embeddings(code, title, description, prereqs)})
            else:
                logger.debug(f"Skipping {code} because it is no longer taught.")

            faculty_courses = self.fetch_faculty_courses()
            position += 1

            logger.debug(f"Course Code: {code}")
            logger.debug(f"Course Title: {title}")
            logger.debug(f"Course Description: {description if description else 'N/A'}")
            logger.debug(f"Prerequisites: {prereqs if prereqs else 'N/A'}")
            logger.debug("-------")

    def fetch_faculty_courses(self):
        logger.debug("Fetching faculty courses.")
        self.wait_for_element(By.ID, 'facultyEvaluations')
        return self._driver.find_element(By.ID, 'facultyEvaluations').find_elements(By.CLASS_NAME, 'facultyCourse')

    def get_description_and_prereqs(self, course_code):
        logger.info(f"Fetching description and prerequisites for course {course_code}")
        self._driver.get(f"https://catalog.depaul.edu/search/?search={course_code}")
        WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.ID, 'fssearchresults')))
        search_results_div = self._driver.find_element(By.ID, "fssearchresults")

        try:
            search_course_result = search_results_div.find_element(By.CLASS_NAME, "search-courseresult")
            courseblock_elements = search_course_result.find_element(By.CLASS_NAME, "courseblock").find_elements(By.TAG_NAME, "p")
            description = courseblock_elements[1].text
            prereqs = courseblock_elements[-1].text

            if len(courseblock_elements) == 1 or description == prereqs:  # prereqs are embedded inside the description, parse and extract.
                description, prereqs = self.parse_description_for_prereqs(description)

            self._driver.back()
            logger.debug(f"Retrieved description and prerequisites for course {course_code}")
            return description, prereqs

        except NoSuchElementException:
            logger.warning(f"Course {course_code} not found, marking as obfuscated.")
            self._obfuscated_courses.append(course_code)
            self._driver.back()
            return None, None

    def wait_for_element(self, by: str, identifier: str) -> None:
        logger.debug(f"Waiting for element by {by} with identifier {identifier}")
        for try_count in range(1, 4):
            try:
                self._wait.until(EC.presence_of_element_located((by, identifier)))
                logger.debug(f"Element found by {by} with identifier {identifier}")
                return
            except (NoSuchElementException, TimeoutException) as e:
                logger.warning(f"Could not locate element, retrying {try_count}/3. Error: {e}")
                self._driver.refresh()
                time.sleep(1)

    @classmethod
    def parse_description_for_prereqs(cls, description: str) -> tuple[str, str]:
        logger.debug("Parsing description for prerequisites.")
        if description.find("TE(S):") == - 1:
            return description, "No prerequisites"
        prerequisite_location = description.find("TE(S):") + len("TE(S):") + 1
        prerequisites = description[prerequisite_location:]

        if prerequisites == "NONE.":
            prerequisites = "No prerequisites"

        return description, prerequisites

    @classmethod
    def extract_course_title(cls, spans):
        logger.debug("Extracting course title.")
        title = spans[1].get_attribute('innerText')
        return title

    @classmethod
    def extract_course_code(cls, spans):
        logger.debug("Extracting course code.")
        code_and_section = spans[0].get_attribute('innerText')
        code = code_and_section[:code_and_section.find('-')].strip()
        return code


if __name__ == '__main__':
    logger.info("Starting the course catalog scraper.")
    catalog = CourseCatalog()
    catalog.get_course_data()
    logger.info("Finished the course catalog scraping process.")
