from schedule import Schedule
from solver import Solver
from student_points import StudentPoints
from subject_lists import SubjectList

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

    solver = Solver(valid_subject_list, valid_student_points, population_size=150)
    best_plan = solver.run(generations=350)
    best_plan.view_schedule()

    print("\n== SATISFACTION STATISTICS")

    satisfaction = best_plan.calculate_satisfaction()
    total_earned = sum(
        sum(best_plan.student_points.points[i+1].get(g.id, 0) for g in s.groups.values())
        for i, s in enumerate(best_plan.students)
    )
    
    total_max = best_plan.total_max_points

    if total_max > 0:
        print(f"Average Preference Match: {satisfaction * 100:.2f}%")
        print(f"Total Points: {total_earned:.0f} / {total_max:.0f}")
        
        avg_fitness = sum(s.fitness for s in best_plan.students) / len(best_plan.students)
        print(f"Average Fitness (including penalties): {avg_fitness:.2f}")
    else:
        print("Error: Could not calculate statistics.")

    
if __name__ == "__main__":
    main()