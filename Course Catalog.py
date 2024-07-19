from webbrowser import Chrome
from Wrappers.Professors import Professors
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

class CourseCatalog:
    _driver = Chrome()
    def __init__(self):
        self._driver = webdriver.Chrome()
    def get_title(self, course_code):
        self._driver.get(f"https://catalog.depaul.edu/search/?search={course_code}")
        try:
            wait = WebDriverWait(self._driver, 10)
            title_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'courseblocktitle')))
            title = title_element.text
            return title.split('\n')[0]
        except Exception as e:
            print(f"Failed to get title for {course_code}: {e}")
            return None
    def get_description(self, course_code):
        self._driver.get(f"https://catalog.depaul.edu/search/?search={course_code}")
        try:
            wait = WebDriverWait(self._driver, 10)
            description_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'courseblockdesc')))
            description = description_element.text

            prereqs_element = self._driver.find_element(By.CLASS_NAME, 'courseblockextra')
            prereqs = prereqs_element.text if prereqs_element else "None"

            return description, prereqs
        except Exception as e:
            print(f"Failed to get description and prereqs for {course_code}: {e}")
            return None, None

    def getCourseData(self):
        all_professors = Professors.get_all(Professors.Cols.FACULTY_ID)
        for professor in all_professors:
            print(professor[Professors.Cols.FACULTY_ID])
            self.scrape_courses(FACULTY_ID)

    def scrape_courses(self, faculty_id):
        self._driver.get(f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={faculty_id}")
        wait = WebDriverWait(self._driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'facultyEvaluations')))
        faculty_courses = self._driver.find_element(By.ID, 'facultyEvaluations').find_elements(By.CLASS_NAME, 'facultyCourse')

        for course in faculty_courses:
            anchor = course.find_element(By.TAG_NAME, 'a')
            spans = anchor.find_elements(By.TAG_NAME, 'span')
            code_and_section = spans[0].get_attribute('innerText')
            code = code_and_section[:code_and_section.find('-')].strip()

            title = self.get_title(code)
            description, prereqs = self.get_description(code)

            print(f"Course Code: {code}")
            print(f"Course Title: {title}")
            print(f"Course Description: {description}")
            print(f"Prerequisites: {prereqs}")
            print("-------")

if __name__ == '__main__':
    catalog = CourseCatalog()
    catalog.get_course_data()



