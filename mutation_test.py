from schedule import Schedule
from student_points import StudentPoints
from subject_lists import SubjectList
from random import seed

def main():
    seed(42) # Dla powtarzalności wyników
    print("Inicjalizacja problemu...")
    
    # 1. Tworzymy proste środowisko z 3 przedmiotami
    subject_list = SubjectList()
    subject_list.add_subject("Matematyka", 5)
    subject_list.add_subject("Fizyka", 5)
    subject_list.add_subject("Informatyka", 5)

    points = StudentPoints(subject_list)
    points.generate()

    # 2. Generujemy poprawny plan
    schedule = Schedule(subject_list, points)
    while True:
        try:
            schedule.populate()
            break
        except RuntimeError:
            pass

    if not schedule.is_feasible():
        print("BŁĄD: Wygenerowany początkowy plan jest niepoprawny!")
        return

    print("Początkowy plan wygenerowany i jest poprawny.")

    # 3. Zapisujemy stan przed mutacją (snapshot), aby sprawdzić co się zmieniło
    original_state = []
    for student in schedule.students:
        original_state.append(dict(student.groups))

    # 4. Odpalamy mutację
    mutation_rate = 0.1
    print(f"Uruchamianie mutacji (mutation_rate={mutation_rate})...")
    schedule.reliable_mutation(mutation_rate=mutation_rate)

    # 5. Weryfikacja po mutacji
    if not schedule.is_feasible():
        print("BŁĄD: Plan po mutacji przestał być poprawny! (Zepsute capacity lub kolizje)")
        return

    # 6. Liczenie zauważalnych zmian
    changes = 0
    for i, student in enumerate(schedule.students):
        for subject, group in student.groups.items():
            if original_state[i][subject].id != group.id:
                changes += 1

    # 7. Obliczenie statystyk
    total_genes = len(schedule.students) * len(schedule.subject_list.subjects)
    change_percentage = (changes / total_genes) * 100

    print("\n=== WYNIKI ===")
    print(f"Mutation rate (zaplanowany): {mutation_rate * 100:.1f}%")
    print(f"Liczba studentów: {len(schedule.students)}")
    print(f"Liczba przedmiotów: {len(schedule.subject_list.subjects)}")
    print(f"Całkowita liczba genów: {total_genes}")
    print(f"Faktyczne zmiany: {changes}/{total_genes} ({change_percentage:.2f}%)")

    if changes > 0:
        print("\nSUKCES: Mutacja działa, wprowadza zmiany i utrzymuje poprawność!")
    else:
        print("\nOSTRZEŻENIE: Mutacja nie zmieniła żadnego genu. Może to być wina zbyt ciasnego planu, lub złej logiki losowania.")

if __name__ == "__main__":
    main()
