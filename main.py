from schedule import Schedule
from solver import Solver
from student_points import StudentPoints
from subject_lists import SubjectList
from config_loader import config


POPULATION_SIZE = config["POPULATION_SIZE"]
GENERATIONS = config["GENERATIONS"]
PRESERVE_BEST = config["PRESERVE_BEST"]

def main():
    names = ["Fizyka", "Systemy operacyjne", "Sieci komputerowe", "Inżynieria oprogramowania", 
             "Teoria obliczeń", "Badania operacyjne", "Algorytmy geometryczne", 
             "Metody obliczeniowe", "Teoria kompilacji"]

    print("Looking for a feasible subject list...")
    while True:
        l = SubjectList()
        for name in names:
            l.add_subject(name, 20)
        
        p = StudentPoints(l)
        test_schedule = Schedule(l, p)
        try:
            test_schedule.populate()
            valid_subject_list = l
            valid_student_points = p
            break
        except RuntimeError:
            continue
    
    print("Subject list found")

    solver = Solver(valid_subject_list, valid_student_points, population_size=POPULATION_SIZE)
    best_plan = solver.run(generations=GENERATIONS, preserve_best=PRESERVE_BEST, mode="tournament")
    best_plan.view_schedule()

    print("\n== SATISFACTION STATISTICS")

    satisfaction = best_plan.calculate_satisfaction()
    total_earned = sum(
        sum(best_plan.student_points.points[i+1].get(g.id, 0) for g in s.groups.values())
        for i, s in enumerate(best_plan.students)
    )
    
    total_max = best_plan.total_max_points

    if total_max > 0:
        print(f"Average preference match: {satisfaction * 100:.2f}%")
        print(f"Total points: {total_earned:.0f} / {total_max:.0f}")

        total_span = 0.0
        active_days_count = 0 

        for student in best_plan.students:
            day_starts = {}
            day_ends = {}

            for group in student.groups.values():
                d = group.day
                if d not in day_starts or group.start < day_starts[d]:
                    day_starts[d] = group.start
                if d not in day_ends or group.end > day_ends[d]:
                    day_ends[d] = group.end

            for d in day_starts:
                total_span += (day_ends[d] - day_starts[d])
                active_days_count += 1

        if active_days_count > 0:
            avg_daily_span = total_span / active_days_count
            print(f"Average daily span (on active days): {avg_daily_span:.2f} hours")
        
        avg_fitness = sum(s.fitness for s in best_plan.students) / len(best_plan.students)
        print(f"Average fitness: {avg_fitness:.2f}")
    else:
        print("Error: Could not calculate statistics.")

    
if __name__ == "__main__":
    main()