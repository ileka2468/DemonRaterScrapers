from openai import OpenAI
from supabase_client import SupaBaseClient

supabase = SupaBaseClient.instance()
client = OpenAI()


def generate_embeddings(code: str, title: str, description: str, prereqs: str) -> list[float]:
    input_text = f"Course code: {code}\nCourse title: {title}\nCourse description: {description}\nCourse prereqs: {prereqs}"
    # print(input_text)
    response = client.embeddings.create(
        input=input_text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding


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
