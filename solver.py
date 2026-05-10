from subject_lists import SubjectList
from student_points import StudentPoints
from schedule import Schedule
from tqdm import tqdm
import random

MUTATION_PROBABILITY = 0.15
MUTATION_RATE = 0.1

class Solver:
    def __init__(self, subject_list: SubjectList, student_points: StudentPoints, population_size: int = 20):
        self.subject_list = subject_list
        self.student_points = student_points
        self.population_size = population_size
        self.population: list[Schedule] = []

        pbar = tqdm(total=population_size, desc="Building Population")
        while len(self.population) < population_size:
            schedule = Schedule(self.subject_list, self.student_points)
            try:
                schedule.populate()
                self.population.append(schedule)
                pbar.update(1)
            except RuntimeError:
                pass
        pbar.close()


    def _tournament_selection(self, k: int = 5) -> Schedule:
        # randomly pick `k` schedules and return one with max value of fitness
        contestants = random.sample(self.population, k)
        return max(contestants, key=lambda s: s.calculate_schedule_fitness())
    
    def _roulette_selection(self) -> Schedule:
        population_fitnesses = [s.calculate_schedule_fitness() for s in self.population]

        # normalize fitnesses
        min_fit = min(population_fitnesses)
        if min_fit <= 0:
            offset = abs(min_fit) + 1
            adjusted_fitnesses = [f + offset for f in population_fitnesses]
        else:
            adjusted_fitnesses = population_fitnesses
            
        # get a pick from [0, total_fitness]
        total_fitness = sum(adjusted_fitnesses)
        pick = random.uniform(0, total_fitness)
        
        # increment by each schedule's fitness value until it reaches the picked value
        current = 0
        for i, f in enumerate(adjusted_fitnesses):
            current += f
            if current >= pick:
                return self.population[i]
        
        # return the last schedule in case of float op inaccuracy
        return self.population[-1]

    def run(self, generations: int, preserve_best: int = 5, mode: str = "tournament"):
        for gen in range(generations):
            self.population.sort(key=lambda s: s.calculate_schedule_fitness(), reverse=True)
            
            best_schedule = self.population[0]
            best_fitness = best_schedule.calculate_schedule_fitness()
            avg_fitness = best_fitness / len(self.population[0].students)

            print(f"Generation {gen:3}: Best fitness = {best_fitness:8.2f} | Avg fitness = {avg_fitness:5.2f}")

            # preserve the top `preserve_best` schedules
            new_generation = self.population[:preserve_best]

            while len(new_generation) < self.population_size:
                # select schedules to crossover
                if mode == "tournament":
                    p1 = self._tournament_selection(k=5)
                    p2 = self._tournament_selection(k=5)
                else:
                    p1 = self._roulette_selection()
                    p2 = self._roulette_selection()

                # parents should be unique
                if p1 == p2:
                    continue

                child = p1.reliable_crossover(p2)
                
                # mutate with given probability
                if child:
                    if random.random() < MUTATION_PROBABILITY:
                        child.reliable_mutation(mutation_rate=MUTATION_RATE)
                    new_generation.append(child)

            # swap out the previous population
            self.population = new_generation

        # return the best schedule
        self.population.sort(key=lambda s: s.calculate_schedule_fitness(), reverse=True)
        return self.population[0]
        