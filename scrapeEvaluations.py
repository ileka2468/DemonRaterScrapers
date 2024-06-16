from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from supabase_client import SupaBaseClient
from normalize import calculate_weighted_average
from EvaluationScoring import calculate_penalized_score_with_min
import concurrent.futures

supabase = SupaBaseClient.instance()
driver = Chrome()

COURSE_OBJECTIVES_INDEX = 2
ASSIGNMENTS_EFFECTIVE_INDEX = 3
INSTRUCTOR_PRESENTATION_INDEX = 6
FAIR_GRADING_INDEX = 4
INSTRUCTOR_ENGAGEMENT_INDEX = 8
INSTRUCTOR_RESPECT_INDEX = 5
WORKLOAD_INDEX = 10
MATERIAL_ORGANIZATION_INDEX = 7
COURSE_CHALLENGE_INDEX = 12
INSTRUCTOR_RESPONSIVENESS_INDEX = 9
GRADING_SPEED_INDEX = 11

OLD_COURSE_OBJECTIVES_INDEX = 0
OLD_ASSIGNMENTS_EFFECTIVE_INDEX = 7
OLD_INSTRUCTOR_PRESENTATION_INDEX = 13
OLD_FAIR_GRADING_INDEX = 8
OLD_INSTRUCTOR_ENGAGEMENT_INDEX = 17
OLD_INSTRUCTOR_RESPECT_INDEX = 18
OLD_WORKLOAD_INDEX = 4
OLD_MATERIAL_ORGANIZATION_INDEX = 2
OLD_COURSE_CHALLENGE_INDEX = 3
OLD_INSTRUCTOR_RESPONSIVENESS_INDEX = 19
OLD_GRADING_SPEED_INDEX = 9

ALL_EVALUATION_SUM = 0
ALL_RESPONSES_SUM = 0
EVALUATION_COUNT = 0


def scrapeEvaluation(row):
    driver.get(f"https://www.cdm.depaul.edu/Faculty-and-Staff/Pages/faculty-info.aspx?fid={row['faculty_id']}")
    wait = WebDriverWait(driver, 99999)
    wait.until(EC.presence_of_element_located((By.ID, 'facultyEvaluations')))
    facultyCourses = driver.find_element(By.ID, 'facultyEvaluations').find_elements(By.CLASS_NAME, 'facultyCourse')
    index = 0

    while index < len(facultyCourses):
        course = facultyCourses[index]
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
        print(code)

        if len(course_code_id) == 0:
            pass
            # print("Course is no longer being offered skipping record...")
        else:
            data = supabase.from_('Course History').select('ch_id') \
                .eq('course', course_code_id[0]['course_id']) \
                .eq('professor_id', row['professor_id']) \
                .eq('term', term_id) \
                .eq('section', section) \
                .eq('start_year', full_start_year)\
                .eq('end_year', full_end_year)\
                .execute().data

            # print(data)
            result = parseSurvey(anchor, data[0]['ch_id'])
            if result == 'skip':
                break
            driver.back()

        wait.until(EC.presence_of_element_located((By.ID, 'facultyEvaluations')))
        facultyCourses = driver.find_element(By.ID, 'facultyEvaluations').find_elements(By.CLASS_NAME, 'facultyCourse')
        index += 1


def parseSurvey(anchor, ch_id):
    driver.get(anchor.get_attribute('href'))

    try:
        driver.find_element(By.ID, 'newNewStyle')
        handleNew(ch_id)
    except NoSuchElementException:
        # print('Page is not the new evaluation, trying old one...')
        try:
            driver.find_element(By.ID, 'newStyle')
            handleOld(ch_id)
        except NoSuchElementException:
            # print('Page is not the old evaluation either,must be old old evaluation. moving on to next professor!')
            return 'skip'


def handleNew(ch_id):
    global ALL_EVALUATION_SUM
    global ALL_RESPONSES_SUM
    global EVALUATION_COUNT
    questions = driver.find_element(By.ID, 'newNewStyle').find_elements(By.CLASS_NAME, 'questionContainer')
    expectdQuestions = [
        'The instructor conveyed the goals of the course',
        'The instructor used activities or assignments that helped me to achieve the goals of the course',
        'The instructor was able to effectively present and explain the course content',
        'The instructor’s evaluation criteria were an appropriate measure of whether I achieved the goals of the course',
        'The instructor encouraged participation from the students',
        'The instructor maintained an atmosphere of respect in this course',
        'The amount of work I performed outside scheduled class time was:',
        'The course material was clear and organized',
        'Compared to other courses I took at DePaul, I found this course to be',
        'The instructor was responsive in answering questions outside the scheduled class time',
        'Homework and exams were graded in reasonable time'

    ]

    for question in questions:
        title = question.find_element(By.CLASS_NAME, 'questionTitle').text
        if title in expectdQuestions:
            expectdQuestions.remove(title)

    if len(expectdQuestions) != 0:
        quit()
    else:
        course_objectives = questions[COURSE_OBJECTIVES_INDEX]
        assignments_effective = questions[ASSIGNMENTS_EFFECTIVE_INDEX]
        instructor_presentation = questions[INSTRUCTOR_PRESENTATION_INDEX]
        fair_grading = questions[FAIR_GRADING_INDEX]
        instructor_engagement = questions[INSTRUCTOR_ENGAGEMENT_INDEX]
        instructor_respect = questions[INSTRUCTOR_RESPECT_INDEX]
        workload = questions[WORKLOAD_INDEX]
        material_organization = questions[MATERIAL_ORGANIZATION_INDEX]
        course_challenge = questions[COURSE_CHALLENGE_INDEX]
        instructor_responsiveness = questions[INSTRUCTOR_RESPONSIVENESS_INDEX]
        grading_speed = questions[GRADING_SPEED_INDEX]

        course_objectives_rating = round(float(
            course_objectives.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        assignments_effective_rating = round(float(
            assignments_effective.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        instructor_presentation_rating = round(float(
            instructor_presentation.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        fair_grading_rating = round(float(
            fair_grading.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        instructor_engagement_rating = round(float(
            instructor_engagement.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        instructor_respect_rating = round(float(
            instructor_respect.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        workload_rating = round(
            float(workload.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        material_organization_rating = round(float(
            material_organization.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        course_challenge_rating = round(float(
            course_challenge.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        instructor_responsiveness_rating = round(float(
            instructor_responsiveness.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)
        grading_speed_rating = round(float(
            grading_speed.find_element(By.CLASS_NAME, 'rankPercentage').get_attribute('innerText')), 2)

        total_eval_sum = sum([course_objectives_rating, assignments_effective_rating, instructor_presentation_rating,
                              fair_grading_rating, instructor_engagement_rating, instructor_respect_rating,
                              material_organization_rating, instructor_responsiveness_rating,
                              grading_speed_rating])

        evaluation_average_score = total_eval_sum / 9
        # print("Evaluation Average: ", evaluation_average_score)
        num_responses = int(driver.find_element(By.CLASS_NAME, 'evalResponses').get_attribute('innerText'))
        adjusted_score = calculate_penalized_score_with_min(evaluation_average_score, num_responses)
        # print(f"Responses: {num_responses}\nEvaluation Score: {evaluation_average_score}\nPenalized Score: {adjusted_score}\n\n")
        supabase.from_("Evaluations").insert({
            'course_objectives': course_objectives_rating,
            'assignments_effective': assignments_effective_rating,
            'instructor_presentation': instructor_presentation_rating,
            'fair_grading': fair_grading_rating,
            'instructor_engagement': instructor_engagement_rating,
            'instructor_respect': instructor_respect_rating,
            'workload': workload_rating,
            'material_organization': material_organization_rating,
            'course_challenge': course_challenge_rating,
            'instructor_responsiveness': instructor_responsiveness_rating,
            'grading_speed': grading_speed_rating,
            'responses': num_responses,
            'score': round(evaluation_average_score, 2),
            'adjusted_score': round(adjusted_score, 2),
            'ch_id': ch_id
        }).execute()


def handleOld(ch_id):
    global ALL_EVALUATION_SUM
    global ALL_RESPONSES_SUM
    global EVALUATION_COUNT

    questions = driver.find_element(By.ID, 'newStyle').find_elements(By.CLASS_NAME, 'questionContainer')
    expectdQuestions = [
        'The course objectives were clearly defined:',
        'The assignments for this course contributed effectively to my overall learning experience:',
        "I found the instructor's ability to present and explain the material to be:",
        "Homework and exams were graded fairly:",
        "When appropriate, the instructor encouraged participation from the students:",
        "The instructor's attitude towards students was fair and impartial:",
        "The amount of work I performed outside scheduled class time was:",
        "The course material was presented in an organized manner:",
        "I found the course material to be:",
        "I found the accessibility of the instructor outside of scheduled class time to be:",
        "Homework and exams were graded in reasonable time:"
    ]

    for question in questions:
        title = question.find_element(By.CLASS_NAME, 'questionTitle').text
        if title in expectdQuestions:
            expectdQuestions.remove(title)
    if len(expectdQuestions) != 0:
        quit()
    else:
        course_objectives = questions[OLD_COURSE_OBJECTIVES_INDEX]
        assignments_effective = questions[OLD_ASSIGNMENTS_EFFECTIVE_INDEX]
        instructor_presentation = questions[OLD_INSTRUCTOR_PRESENTATION_INDEX]
        fair_grading = questions[OLD_FAIR_GRADING_INDEX]
        instructor_engagement = questions[OLD_INSTRUCTOR_ENGAGEMENT_INDEX]
        instructor_respect = questions[OLD_INSTRUCTOR_RESPECT_INDEX]
        workload = questions[OLD_WORKLOAD_INDEX]
        material_organization = questions[OLD_MATERIAL_ORGANIZATION_INDEX]
        course_challenge = questions[OLD_COURSE_CHALLENGE_INDEX]
        instructor_responsiveness = questions[OLD_INSTRUCTOR_RESPONSIVENESS_INDEX]
        grading_speed = questions[OLD_GRADING_SPEED_INDEX]

        evaluation_average_score, mapping = handleOldQuestion(
            [course_objectives, assignments_effective, instructor_presentation, fair_grading, instructor_engagement,
             instructor_respect, workload, material_organization, course_challenge, instructor_responsiveness,
             grading_speed])
        # print("Evaluation Average: ", evaluation_average_score)

        num_responses = int(driver.find_element(By.CLASS_NAME, 'evalResponses').get_attribute('innerText'))
        adjusted_score = calculate_penalized_score_with_min(evaluation_average_score, num_responses)
        # print(f"Responses: {num_responses}\nEvaluation Score: {evaluation_average_score}\nPenalized Score: {adjusted_score}\n\n")
        # print(mapping)
        supabase.from_("Evaluations").insert({
            'course_objectives': mapping[0],
            'assignments_effective': mapping[1],
            'instructor_presentation': mapping[2],
            'fair_grading': mapping[3],
            'instructor_engagement': mapping[4],
            'instructor_respect': mapping[5],
            'workload': mapping[6],
            'material_organization': mapping[7],
            'course_challenge': mapping[8],
            'instructor_responsiveness': mapping[9],
            'grading_speed': mapping[10],
            'responses': num_responses,
            'score': round(evaluation_average_score, 2),
            'adjusted_score': round(adjusted_score, 2),
            'ch_id': ch_id
        }).execute()


def handleOldQuestion(old_questions):
    mapping = {}
    evaluation_total = 0
    for index, question in enumerate(old_questions):
        rank_containers = question.find_element(By.CLASS_NAME, 'graphContainer').find_elements(By.CLASS_NAME,
                                                                                               'rankContainer')
        responses = {}
        for rank_container in rank_containers:
            try:
                percentage = rank_container.find_element(By.CLASS_NAME, 'barContainer').find_element(By.CLASS_NAME,
                                                                                                     'rankPercentage').get_attribute(
                    'innerText')
            except NoSuchElementException:
                percentage = 0

            if percentage != 0:
                percentage = round(float(percentage[:percentage.find('%')]), 2)

            if rank_container.find_element(By.CLASS_NAME, 'rankDescription').get_attribute(
                    'innerText') != 'N/A':  # exclude non answers from the scoring
                responses[rank_container.find_element(By.CLASS_NAME, 'rankDescription').get_attribute(
                    'innerText')] = percentage

        if index not in (6, 8):  # Ignore subjective questions
            evaluation_total += round(calculate_weighted_average(responses), 2)
            # print(question.find_element(By.CLASS_NAME, 'questionTitle').text,
            #       round(calculate_weighted_average(responses), 2))
        mapping[index] = round(calculate_weighted_average(responses), 2)

    return evaluation_total / 9, mapping


def process_chunk(data_chunk):
    for row in data_chunk:
        print(row['professor_name'])
        scrapeEvaluation(row)


def main():
    data = supabase.from_("Professors").select("*").execute().data
    num_workers = 25  # Set the number of workers (processes) to a higher number
    chunk_size = len(data) // num_workers  # Calculate the chunk size based on the number of workers
    data_chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        executor.map(process_chunk, data_chunks)


if __name__ == '__main__':
    main()

