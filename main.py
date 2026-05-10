from subject_lists import SubjectList
from student_points import StudentPoints
from schedule import Schedule
from random import randint


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

while True:
    l = SubjectList()
    for subject in subject_names:
        l.add_subject(subject, randint(20, 20))

    p = StudentPoints(l)
    p.generate()

    schedule = Schedule(l, p)
    try:
        schedule.populate()
        break
    except RuntimeError:
        pass

print(schedule)
print(l)
schedule.view_schedule()