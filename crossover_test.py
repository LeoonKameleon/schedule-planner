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
N_CHILDREN = 200
MAX_PARENT_ATTEMPTS = 100
MAX_INSTANCE_ATTEMPTS = 100


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


def build_feasible_parents():
    for _ in range(MAX_INSTANCE_ATTEMPTS):
        subject_list = build_subject_list()
        points = StudentPoints(subject_list)

        try:
            parent_a = build_population(subject_list, points)
            parent_b = build_population(subject_list, points)
            return parent_a, parent_b
        except RuntimeError:
            continue

    raise RuntimeError("Could not generate a feasible timetable instance with two parents")


def evaluate_crossover(parent_a: Population, parent_b: Population, n_children: int):
    feasible_children = 0
    for _ in range(n_children):
        child = parent_a.crossover(parent_b)
        if child is not None and child.is_feasible():
            feasible_children += 1

    rate = (feasible_children / n_children) * 100
    return feasible_children, rate


def main():
    seed(42)

    parent_a, parent_b = build_feasible_parents()

    assert parent_a.is_feasible(), "Parent A should be feasible"
    assert parent_b.is_feasible(), "Parent B should be feasible"

    feasible_count, feasible_rate = evaluate_crossover(parent_a, parent_b, N_CHILDREN)

    print("== Crossover Benchmark ==")
    print(f"Parents feasible: A={parent_a.is_feasible()}, B={parent_b.is_feasible()}")
    print(f"Feasible children: {feasible_count}/{N_CHILDREN}")
    print(f"Feasible children rate: {feasible_rate:.2f}%")

    sample_child = parent_a.crossover(parent_b)
    if sample_child is None:
        print("Sample child: infeasible")
    else:
        print(f"Sample child feasible: {sample_child.is_feasible()}")


if __name__ == "__main__":
    main()
