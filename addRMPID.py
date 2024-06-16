import ratemyprofessor as rmp
from supabase_client import SupaBaseClient


def main():
    supabase = SupaBaseClient.instance()
    query = supabase.from_("Professors").select("*").execute()

    for row in query.data:
        rmp_name = row["rmp_profile_name"]
        prof_name = row["professor_name"]
        if not rmp_name:
            professors = rmp.get_professors_by_school_and_name(rmp.School(1389), prof_name)
        else:
            professors = rmp.get_professors_by_school_and_name(rmp.School(1389), rmp_name)

        hasRMP = False
        hasDup = False
        professors_so_far: list[tuple[str, rmp.Professor]] = []
        choice = None
        for professor in professors:
            if professor.school.name == "DePaul University":
                professor.get_ratings()
                hasRMP = True
                if hasDuplicate(professors_so_far, professor):
                    hasDup = True
                    choice = handleDuplicateProfessor(professors_so_far, professor)
                    print("choosing duplicate with most reviews...")
                else:
                    choice = professor
                professors_so_far.append((professor.name, professor))

        query = None

        if hasRMP and hasDup:
            print(choice, "had duplicate profiles, profile with ", choice.num_ratings, "reviews was chosen.")
            query = supabase.table("Professors").update({"rmp_profile_id": choice.id}).eq("professor_id", row["professor_id"]).execute()
        elif hasRMP and not hasDup:
            print(choice, "had no duplicate profiles their only profile was chosen.")
            query = supabase.table("Professors").update({"rmp_profile_id": choice.id}).eq("professor_id",
                                                                                          row["professor_id"]).execute()
        if not hasRMP:
            print(f"{prof_name} Has No RMP Profile.")


def hasDuplicate(professor_list: list[tuple[str, rmp.Professor]], professor: rmp.Professor) -> bool:
    for prof in professor_list:
        name, profobj = prof[0], prof[1]
        if professor.name == profobj.name:
            return True
    return False


def handleDuplicateProfessor(professor_list: list[tuple[str, rmp.Professor]], professor: rmp.Professor) -> rmp.Professor:
    max_professor = professor
    for prof in professor_list:
        name, profobj = prof[0], prof[1]
        if professor.name == profobj.name:
            if professor.num_ratings >= profobj.num_ratings:
                max_professor = professor
            else:
                max_professor = profobj

    return max_professor


if __name__ == '__main__':
    main()
