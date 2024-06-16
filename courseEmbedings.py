from openai import OpenAI
from dotenv import load_dotenv
from supabase_client import SupaBaseClient

supabase = SupaBaseClient.instance()
client = OpenAI()

# courses = supabase.from_('Courses').select("*").execute().data
#
# for course in courses:
#     input_text = f"Course code: {course['code']}\nCourse title: {course['title']}\nCourse description: {course['description']}\nCourse prereqs: {course['prereqs']}"
#     print(input_text)
#     response = client.embeddings.create(
#         input=input_text,
#         model="text-embedding-3-large"
#     )
#     embedding = response.data[0].embedding
#     supabase.from_('Courses').update({'embedding': embedding}).eq('course_id', course['course_id']).execute()


def test():
    query = "If I want to take CSC 301 list all the prequisites that would be needed to do that?"
    query_embedding = client.embeddings.create(
        input=query,
        model="text-embedding-3-large"
    ).data[0].embedding
    print(query_embedding)

    result = supabase.rpc('match_documents', {'query_embedding': query_embedding, 'similarity_threshold': .10, 'count': 10}).execute().data

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chatbot assistant for a web app called DemonRater an app for rating"
                                          " Depaul CDM professors and finding professor matches. Be slightly perky and jolly when responsing."},
            {"role": "system",
             "content": f"Here are text embeddings that are realvent to the current querry use them as a knowled base. Embeddings: {result}"},
            {"role": "user", "content": query}

        ]
    )

    print(response.choices[0].message.content)

test()