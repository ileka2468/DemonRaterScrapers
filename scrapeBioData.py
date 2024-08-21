
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from Wrappers.Professors import Professors
from openai import OpenAI

driver = Chrome()
wait = WebDriverWait(driver, 10)
client = OpenAI()


def summarize_bio(bio_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize this Bio data. Keep it short and avoid direct copying."},
                {"role": "user", "content": bio_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:

        print(e)


def scrape_professor_info(faculty_id):

    url = f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={faculty_id}"
    driver.get(url)
    try:
        wait.until(presence_of_element_located((By.ID, "facultyBio")))
        bio_element = driver.find_element(By.ID, "facultyBio")
        description_element = bio_element.find_element(By.ID, "ogOverrideDescription")
        description = description_element.text
        if description == "Not available":
            return description, description
        research_element = bio_element.find_element(By.CLASS_NAME, "additionalInfo")
        if research_element.text == "":
            return summarize_bio(description), "Not available"
        research = research_element.find_elements(By.TAG_NAME, "div")
        return summarize_bio(description), research[0].text

    except (NoSuchElementException, TimeoutException) as e:
        raise RuntimeError(e)


def update_professor_data(faculty_id, bio, research_area):

    try:
        Professors.update({Professors.Cols.Bio: bio, Professors.Cols.RESEARCH_AREA: research_area},
                          Professors.Cols.FACULTY_ID, faculty_id)

    except Exception as e:
        raise RuntimeError(e)


def main():
    try:
        all_professors = Professors.get_all(Professors.Cols.FACULTY_ID)
        for professor in all_professors:
            faculty_id = professor[Professors.Cols.FACULTY_ID]

            bio, research_area = scrape_professor_info(faculty_id)
            print(bio, research_area)
            #if bio and research_area:
                #update_professor_data(faculty_id, bio, research_area)

    finally:
        driver.quit()


if __name__ == '__main__':
    main()

