from subject_lists import SubjectList
from student_points import StudentPoints
from population import Population
from random import random, seed

from selection import objective_function, ranking_selection, tournament_selection


subject_names = [
    "Fizyka",
    "Systemy operacyjne",
    "Sieci komputerowe",
    "Inżynieria oprogramowania",
    "Teoria obliczeń i złożoności obliczeniowej",
    "Badania operacyjne",
    "Algorytmy geometryczne",
    "Metody obliczeniowe w nauce i technice",
    "Teoria kompilacji"
]

GROUPS_PER_SUBJECT = 20
GA_POPULATION_SIZE = 10
GENERATIONS = 20
ELITE_COUNT = 2
CROSSOVER_RATE = 0.90
GENE_MUTATION_RATE = 0.02
SELECTION_METHOD = "tournament"  # "tournament" or "ranking"
TOURNAMENT_SIZE = 3
TOURNAMENT_P_BEST = 1.0
ALPHA = 0.0
MAX_POPULATE_ATTEMPTS = 120
MAX_INSTANCE_ATTEMPTS = 50


def build_subject_list() -> SubjectList:
    subject_list = SubjectList()
    for subject in subject_names:
        subject_list.add_subject(subject, GROUPS_PER_SUBJECT)
    return subject_list


def build_feasible_population(
    subject_list: SubjectList,
    points: StudentPoints,
    max_attempts: int = MAX_POPULATE_ATTEMPTS,
) -> Population:
    for _ in range(max_attempts):
        population = Population(subject_list, points)
        try:
            population.populate()
            return population
        except RuntimeError:
            continue

    raise RuntimeError("Unable to create a feasible population")


def initialize_ga_population(
    subject_list: SubjectList,
    points: StudentPoints,
    population_size: int,
) -> list[Population]:
    if population_size <= 0:
        raise ValueError("population_size must be > 0")

    base = build_feasible_population(subject_list, points)
    individuals = [base]

    attempts_left = population_size * 80
    while len(individuals) < population_size and attempts_left > 0:
        attempts_left -= 1

        parent = individuals[-1]
        candidate = parent.mutate(mutation_rate=0.10)

        if candidate is None:
            try:
                candidate = build_feasible_population(subject_list, points, max_attempts=10)
            except RuntimeError:
                continue

        if candidate.is_feasible():
            individuals.append(candidate)

    if len(individuals) < population_size:
        raise RuntimeError("Unable to initialize requested GA population size")

    return individuals


def build_initial_instance(population_size: int) -> tuple[SubjectList, StudentPoints, list[Population]]:
    for _ in range(MAX_INSTANCE_ATTEMPTS):
        subject_list = build_subject_list()
        points = StudentPoints(subject_list)
        try:
            initial_population = initialize_ga_population(
                subject_list,
                points,
                population_size=population_size,
            )
            return subject_list, points, initial_population
        except RuntimeError:
            continue

    raise RuntimeError("Unable to create a feasible initial GA instance")


def select_parents(populations: list[Population]) -> list[Population]:
    if SELECTION_METHOD == "ranking":
        return ranking_selection(populations, n_selected=2, alpha=ALPHA)

    if SELECTION_METHOD == "tournament":
        return tournament_selection(
            populations,
            n_selected=2,
            tournament_size=TOURNAMENT_SIZE,
            alpha=ALPHA,
            p_best=TOURNAMENT_P_BEST,
        )

    raise ValueError(f"Unknown selection method: {SELECTION_METHOD}")


def run_genetic_algorithm(
    populations: list[Population],
    generations: int,
) -> tuple[Population, float]:
    if not populations:
        raise ValueError("Initial GA population cannot be empty")

    current = populations[:]

    for generation in range(1, generations + 1):
        scored = [(individual, objective_function(individual, alpha=ALPHA)) for individual in current]
        scored.sort(key=lambda item: item[1], reverse=True)

        best_score = scored[0][1]
        avg_score = sum(score for _, score in scored) / len(scored)
        print(f"Generation {generation:02d}: best={best_score:.2f}, avg={avg_score:.2f}")

        next_generation = [individual for individual, _ in scored[:ELITE_COUNT]]

        while len(next_generation) < len(current):
            parent_a, parent_b = select_parents(current)

            child = None
            if random() < CROSSOVER_RATE:
                child = parent_a.crossover(parent_b)

            if child is None:
                score_a = objective_function(parent_a, alpha=ALPHA)
                score_b = objective_function(parent_b, alpha=ALPHA)
                child = parent_a if score_a >= score_b else parent_b

            mutated = child.mutate(mutation_rate=GENE_MUTATION_RATE)
            if mutated is not None:
                child = mutated

            next_generation.append(child)

        current = next_generation

    final_scored = [(individual, objective_function(individual, alpha=ALPHA)) for individual in current]
    final_scored.sort(key=lambda item: item[1], reverse=True)
    return final_scored[0]


def verify_solution(population: Population, score: float):
    feasible = population.is_feasible()

    print("\n== Verification ==")
    print(f"Feasible timetable: {feasible}")
    print(f"Objective value Z: {score:.2f}")

    if not feasible:
        raise RuntimeError("Final GA solution is not feasible")

def main():
    seed(32)

    print("Building initial GA population...")
    subject_list, _, initial_population = build_initial_instance(GA_POPULATION_SIZE)

    best_population, best_score = run_genetic_algorithm(
        initial_population,
        generations=GENERATIONS,
    )

    verify_solution(best_population, best_score)

    print("\n== Best Population (preview first 5 students) ==")
    for i, student in enumerate(best_population.students[:5], start=1):
        assignments = ", ".join(
            f"{subject.name}:g{group.id}"
            for subject, group in sorted(student.groups.items(), key=lambda item: item[0].name)
        )
        print(f"Student {i}: {assignments}")

    print(subject_list)
    subject_list.view_schedule()


if __name__ == "__main__":
    main()