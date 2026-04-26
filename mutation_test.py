from random import seed

from population import Population
from student_points import StudentPoints
from subject_lists import SubjectList


SUBJECT_NAMES = [
    "Fizyka",
    "Systemy operacyjne",
    "Sieci komputerowe",
    "Inzynieria oprogramowania",
    "Teoria obliczen i zlozonosci obliczeniowej",
    "Badania operacyjne",
    "Algorytmy geometryczne",
    "Metody obliczeniowe w nauce i technice",
    "Teoria kompilacji",
]

GROUPS_PER_SUBJECT = 20
N_MUTATIONS = 100
MAX_PARENT_ATTEMPTS = 100
MAX_INSTANCE_ATTEMPTS = 100
MUTATION_RATE = 0.10


def build_subject_list():
    subject_list = SubjectList()
    for subject in SUBJECT_NAMES:
        subject_list.add_subject(subject, GROUPS_PER_SUBJECT)
    return subject_list


def build_population(subject_list: SubjectList, points: StudentPoints):
    for _ in range(MAX_PARENT_ATTEMPTS):
        population = Population(subject_list, points)
        try:
            population.populate()
            return population
        except RuntimeError:
            continue
    raise RuntimeError("Could not generate a feasible parent population")


def build_feasible_parent():
    for _ in range(MAX_INSTANCE_ATTEMPTS):
        subject_list = build_subject_list()
        points = StudentPoints(subject_list)

        try:
            return build_population(subject_list, points)
        except RuntimeError:
            continue

    raise RuntimeError("Could not generate a feasible timetable instance")


def population_signature(population: Population):
    return [
        tuple(group.id for _, group in sorted(student.groups.items(), key=lambda item: item[0].name))
        for student in population.students
    ]


def evaluate_mutation(n_mutations: int, mutation_rate: float):
    parent = build_feasible_parent()
    parent_before = population_signature(parent)

    feasible_children = 0
    changed_children = 0

    for _ in range(n_mutations):
        child = parent.mutate(mutation_rate)
        if child is None:
            continue

        if child.is_feasible():
            feasible_children += 1

        if population_signature(child) != parent_before:
            changed_children += 1

        # Parent should not be modified by mutation.
        assert population_signature(parent) == parent_before

    feasible_rate = (feasible_children / n_mutations) * 100
    changed_rate = (changed_children / n_mutations) * 100
    return feasible_children, feasible_rate, changed_children, changed_rate


def test_zero_rate_keeps_population():
    parent = build_feasible_parent()
    parent_before = population_signature(parent)
    child = parent.mutate(0.0)

    assert child is not None
    assert child.is_feasible()
    assert population_signature(child) == parent_before
    assert population_signature(parent) == parent_before


def test_positive_rate_changes_population():
    parent = build_feasible_parent()
    parent_before = population_signature(parent)

    changed = False
    for _ in range(30):
        child = parent.mutate(0.20)
        if child is None:
            continue
        if population_signature(child) != parent_before:
            changed = True
            break

    assert changed, "Mutation with positive rate did not change any assignment"


def main():
    seed(123)

    test_zero_rate_keeps_population()
    test_positive_rate_changes_population()

    feasible_count, feasible_rate, changed_count, changed_rate = evaluate_mutation(
        N_MUTATIONS,
        MUTATION_RATE,
    )

    print("== Mutation Tests ==")
    print("All assertions passed")
    print(f"Feasible children: {feasible_count}/{N_MUTATIONS}")
    print(f"Feasible children rate: {feasible_rate:.2f}%")
    print(f"Changed children: {changed_count}/{N_MUTATIONS}")
    print(f"Changed children rate: {changed_rate:.2f}%")


if __name__ == "__main__":
    main()