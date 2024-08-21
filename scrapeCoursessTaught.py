from selenium.webdriver import Chrome

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from Wrappers.Courses import Courses
from Wrappers.CoursesTaught import CoursesTaught
from Wrappers.Professors import Professors

driver = Chrome()
wait = WebDriverWait(driver, 10)


def process_professor(professorId, facultyId):
    url = f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={facultyId}"
    driver.get(url)
    wait.until(ec.presence_of_element_located((By.CLASS_NAME, "Faculty--Courses")))
    courses = driver.find_element(By.CLASS_NAME, "Faculty--Courses")
    course_elements = courses.find_element(By.ID, "facultyCourses").find_elements(By.CLASS_NAME, "facultyCourse")
    for course in course_elements:
        course_code = course.find_elements(By.TAG_NAME, "span")[0].get_attribute("innerText")
        pid = professorId
        cid = Courses.get_single_record({Courses.Cols.CODE: course_code}, Courses.Cols.COURSE_ID)[Courses.Cols.COURSE_ID]
        print(pid, cid)

        if not cid:
            continue

        print(pid, cid)
        CoursesTaught.insert({
            CoursesTaught.Cols.Foreign.PROFESSOR_ID: pid,
            CoursesTaught.Cols.Foreign.COURSE_CODE_ID: cid
        })


def main():
    professors = Professors.get_all(Professors.Cols.PROFESSOR_ID, Professors.Cols.FACULTY_ID)
    for professor in professors:
        print(professor)
        process_professor(professor[Professors.Cols.PROFESSOR_ID], professor[Professors.Cols.FACULTY_ID])


if __name__ == '__main__':
    main()
