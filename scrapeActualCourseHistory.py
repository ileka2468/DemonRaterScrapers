import datetime

from selenium.common import NoSuchElementException, TimeoutException

from supabase_client import SupaBaseClient
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

supabase = SupaBaseClient.instance()
driver = Chrome()


def scrapeCoursesHistory(row: dict):
    driver.get(f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={row['faculty_id']}")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'facultyEvaluations')))
    facultyCourses = driver.find_element(By.ID, 'facultyEvaluations').find_elements(By.CLASS_NAME, 'facultyCourse')

    for course in facultyCourses:
        anchor = course.find_element(By.TAG_NAME, 'a')
        spans = anchor.find_elements(By.TAG_NAME, 'span')
        code_and_section = spans[0].get_attribute('innerText')
        code = code_and_section[:code_and_section.find('-')].strip()
        section = code_and_section[code_and_section.find('-') + 1:].strip()
        term_and_year = spans[2].get_attribute('innerText')
        first_num = [x.isdigit() for x in term_and_year].index(True)
        term = term_and_year[:first_num]
        refined_term = "Fall" if "Fall" in term else "Winter" if "Winter" in term else "Spring" if "Spring" in term else "Summer" if "Summer" in term else "Dec"
        year = term_and_year[first_num:] if len(term_and_year.split(' ')) == 0 else term_and_year.split(' ')[-1]

        # print(code, section, refined_term, year)

        start_year = year[:year.find('-')]
        end_year = year[year.find('-') + 1:]

        full_start_year = int(f"20{start_year}")
        full_end_year = int(f"20{end_year}")

        course_code_id = supabase.from_('Courses').select('course_id').eq('code', code).execute().data
        term_id = supabase.from_("Terms").select('term_id').eq('term', refined_term).execute().data[0]['term_id']

        # print(term_id)
        if len(course_code_id) == 0:
            print("Course is no longer being offered skipping record...")
            continue
        else:
            supabase.from_("Course History").insert({
                'course': course_code_id[0]['course_id'],
                'professor_id': row['professor_id'],
                'section': section,
                'term': term_id,
                'start_year': full_start_year,
                'end_year': full_end_year
            }).execute()
            print("Inserted record.")


def main():
    data = supabase.from_("Professors").select("*").order('professor_name').execute().data
    for row in data:
        print(row['professor_name'])
        scrapeCoursesHistory(row)


if __name__ == '__main__':
    main()
