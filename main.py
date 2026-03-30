from subject_lists import SubjectList
from student_points import StudentPoints
from random import randint


subject_names = [
    "Fizyka",
    "Systemy operacyjne",
    "Sieci komputerowe",
    "Inżynieria oprogramowania",
    "Teoria obliczeń i złożoności obliczeniowej",
    "Badania operacyjne",
    "Algorytmy geometryczne"
]

l = SubjectList()
for subject in subject_names:
    l.add_subject(subject, randint(1, 2))

p = StudentPoints(l)
print(p)