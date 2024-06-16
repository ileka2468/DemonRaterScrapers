from supabase_client import SupaBaseClient
import unicodedata

def linkpfp():
    supabase = SupaBaseClient.instance()
    pid_list = [pid['professor_name'] for pid in supabase.table('Professors').select('professor_name').execute().data]
    print(pid_list)
    for name in pid_list:
        print(remove_accents(name))

    # if supabase.table('Professors')


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def main():
    linkpfp()


if __name__ == '__main__':
    main()