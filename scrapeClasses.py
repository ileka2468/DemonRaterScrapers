import os
import time

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import StaleElementReferenceException
from supabase_client import create_client, Client
from dotenv import load_dotenv
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
url = os.environ.get("supabase_url")
key = os.environ.get("supabase_key")

supabase: Client = create_client(url, key)

def scrapeClasses():
    driver = Chrome()
    driver.get("https://catalog.depaul.edu/course-search/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "section__content")))
    # locate form
    form_section, form_section_second, = driver.find_elements(By.CLASS_NAME, "section__content")  # 2nd item in the list is the advanced search form
    form_groups = form_section_second.find_elements(By.CLASS_NAME, "form-group")

    college: WebElement = form_groups[0]
    subject: WebElement = form_groups[1]
    course_type: WebElement = form_groups[2]
    button: WebElement = form_section.find_element(By.TAG_NAME, 'button')

    college_select = Select(college.find_element(By.TAG_NAME, 'select'))
    subject_select = Select(subject.find_element(By.TAG_NAME, 'select'))
    course_type_select = Select(course_type.find_element(By.TAG_NAME, 'select'))

    college_select.select_by_visible_text("Jarvis College of Computing and Digital Media")
    subject_select.select_by_visible_text("Software Engineering")

    button.click()
    time.sleep(1)

    results = driver.find_elements(By.CLASS_NAME, "panel__content")[1]  # 2nd item is the results panel.
    class_results = results.find_element(By.CLASS_NAME, "panel__body").find_elements(By.CLASS_NAME, 'result')

    for rclass in class_results:
        time.sleep(.5)
        class_code = None
        class_title = None
        description = None
        prerequistes = None
        rclass.find_element(By.TAG_NAME, 'a').click()
        info_pannel = driver.find_elements(By.CLASS_NAME, "panel__content")[2]
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cols')))
        cols = info_pannel.find_element(By.CLASS_NAME, 'cols')
        cols_list = cols.find_elements(By.TAG_NAME, 'div')
        class_code = cols_list[0].text
        class_title = cols_list[1].text

        try:
            p_tags = info_pannel.find_elements(By.TAG_NAME, 'p')
            description = p_tags[1].text

            if len(p_tags) == 3:  # There is a prereq list if there is 3
                prerequistes = p_tags[2].text

            # Insert data into the database
            supabase.from_("Courses").insert({'code': class_code, 'title': class_title, 'description': description, 'prereqs': prerequistes}).execute()
        except StaleElementReferenceException:
            # Re-find the elements if they became stale
            info_pannel = driver.find_elements(By.CLASS_NAME, "panel__content")[2]
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cols')))
            cols = info_pannel.find_element(By.CLASS_NAME, 'cols')
            cols_list = cols.find_elements(By.TAG_NAME, 'div')
            class_code = cols_list[0].text
            class_title = cols_list[1].text

            p_tags = info_pannel.find_elements(By.TAG_NAME, 'p')
            description = p_tags[1].text

            if len(p_tags) == 3:  # There is a prereq list if there is 3
                prerequistes = p_tags[2].text

            # Insert data into the database
            supabase.from_("Courses").insert({'code': class_code, 'title': class_title, 'description': description, 'prereqs': prerequistes}).execute()

def main():
    scrapeClasses()

if __name__ == '__main__':
    main()
