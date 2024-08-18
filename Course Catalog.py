import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome

from Wrappers.Courses import Courses
from Wrappers.Professors import Professors
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CourseCatalog:
    _driver = Chrome()

    def __init__(self):
        self._driver = Chrome()
        self.wait = WebDriverWait(self._driver, 10)
        self.obfuscated_courses = []  # courses that are no longer being actively taught

    def get_course_data(self):
        all_professors = Professors.get_all(Professors.Cols.FACULTY_ID)
        for professor in all_professors:
            self.scrape_courses(professor[Professors.Cols.FACULTY_ID])

    def scrape_courses(self, faculty_id):
        self._driver.get(f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={faculty_id}")
        time.sleep(1)

        self.wait.until(EC.presence_of_element_located((By.ID, 'facultyEvaluations')))
        faculty_courses = self.fetch_faculty_courses()
        position = 0
        print(faculty_id)
        while position < len(faculty_courses):
            course = faculty_courses[position]
            anchor = course.find_element(By.TAG_NAME, 'a')
            spans = anchor.find_elements(By.TAG_NAME, 'span')

            code = self.extract_course_code(spans)
            title = self.extract_course_title(spans)
            description = None
            prereqs = None

            db_course = Courses.get_single_record({Courses.Cols.CODE : code}, Courses.Cols.CODE)

            if db_course:
                print(f"Skipping course {code} because it already exists in the db as {db_course}.")
                position += 1
                continue

            if code not in self.obfuscated_courses:
                description, prereqs = self.get_description_and_prereqs(code)
            else:
                print(f"Skipping {code} because we know it's not taught anymore... ")

            faculty_courses = self.fetch_faculty_courses()
            position += 1

            print(f"Course Code: {code}")
            print(f"Course Title: {title}")
            print(f"Course Description: {description if description else 'N/A'}")
            print(f"Prerequisites: {prereqs if prereqs else 'N/A'}")
            print("-------")

    def fetch_faculty_courses(self):
        self.wait.until(EC.presence_of_element_located((By.ID, 'facultyEvaluations')))
        return self._driver.find_element(By.ID, 'facultyEvaluations').find_elements(By.CLASS_NAME, 'facultyCourse')

    def get_description_and_prereqs(self, course_code):
        self._driver.get(f"https://catalog.depaul.edu/search/?search={course_code}")
        WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.ID, 'fssearchresults')))
        search_results_div = self._driver.find_element(By.ID, "fssearchresults")

        try:
            search_course_result = search_results_div.find_element(By.CLASS_NAME, "search-courseresult")
            courseblock_elements = search_course_result.find_element(By.CLASS_NAME, "courseblock").find_elements(By.TAG_NAME, "p")
            description = courseblock_elements[1].text
            prereqs = courseblock_elements[-1].text

            # append to a list of courses that have already been inserted into the db
            self._driver.back()
            return description, prereqs

        except NoSuchElementException:
            self.obfuscated_courses.append(course_code)
            self._driver.back()
            return None, None

    @classmethod
    def extract_course_title(cls, spans):
        title = spans[1].get_attribute('innerText')
        return title

    @classmethod
    def extract_course_code(cls, spans):
        code_and_section = spans[0].get_attribute('innerText')
        code = code_and_section[:code_and_section.find('-')].strip()
        return code


if __name__ == '__main__':
    catalog = CourseCatalog()
    catalog.get_course_data()



