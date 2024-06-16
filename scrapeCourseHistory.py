import random
import time

from selenium.common import NoSuchElementException, TimeoutException

from supabase_client import SupaBaseClient
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

supabase = SupaBaseClient.instance()
driver = Chrome()


def scrapeCoursesHistory(row: dict):
    # time.sleep(random.randint(0, 4))
    driver.get(f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={row['faculty_id']}")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'facultyCourses')))
    facultyCourses = driver.find_element(By.ID, 'facultyCourses').find_elements(By.CLASS_NAME, 'facultyCourse')

    index = 0
    while index < len(facultyCourses):
        course = facultyCourses[index]
        anchor = course.find_element(By.TAG_NAME, 'a')
        spans = anchor.find_elements(By.TAG_NAME, 'span')
        course_code = spans[0].get_attribute('textContent')
        course_code_id = supabase.from_('Courses').select('course_id').eq('code', course_code).execute().data
        if len(course_code_id) == 0:
            status = insertUnknownClass(anchor.get_attribute('href'))
            if status == 'error':
                print(course_code, 'no longer exits and timed out...')
                index += 1
            else:
                print("added class to db and retrying...")
            # Re-fetch the elements after coming back
            driver.get(f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={row['faculty_id']}")
            wait.until(EC.presence_of_element_located((By.ID, 'facultyCourses')))
            facultyCourses = driver.find_element(By.ID, 'facultyCourses').find_elements(By.CLASS_NAME, 'facultyCourse')
            # Continue with the same index to avoid reprocessing
        else:
            # Move to the next course if no need to insert
            supabase.from_("Courses Taught").insert({'course_code_id': course_code_id[0]['course_id'], 'professor_id': row['professor_id']}).execute()
            print("Record inserted.")
            index += 1


def insertUnknownClass(anchor):
    driver.get(anchor)

    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'PageTitle')))
        info = driver.find_element(By.CLASS_NAME, 'PageTitle').text
        course_code = info[:info.find(':')].strip()
        title = info[info.find(':') + 1:].strip()
        contentarea = driver.find_element(By.ID, 'ctl00_ctl59_g_50f24079_ef2e_419b_a791_15cbeadc76ee')
        description = contentarea.find_element(By.TAG_NAME, 'p').text
        try:
            prereqs = contentarea.find_element(By.TAG_NAME, 'b').text
        except NoSuchElementException:
            prereqs = None
        supabase.from_("Courses").insert({'code': course_code, 'title': title, 'description': description, 'prereqs': prereqs}).execute()
    except TimeoutException:
        return 'error'
    driver.back()


def main():
    data = supabase.from_("Professors").select("*").order('professor_name').execute().data
    for row in data:
        print(row['professor_name'])
        scrapeCoursesHistory(row)


if __name__ == '__main__':
    main()




