from student_points import StudentPoints
from subject_lists import Group, Subject, SubjectList
from random import shuffle


class Student():
    def __init__(self, groups: dict[Subject, Group]):
        self.groups = groups

    def mutate(self):
        raise NotImplementedError
    
    def crossover(self):
        raise NotImplementedError
    

class Population():
    def __init__(self, subject_list: SubjectList, student_points: StudentPoints):
        self.subject_list = subject_list
        self.student_points = student_points
        self.students = []
    
    def populate(self):
        for student in self.student_points.points:
            given_groups = {}
            subjects = list(self.subject_list.subjects.values())
            shuffle(subjects)
            
            def backtrack(subjects, given_groups):
                if len(subjects) == len(given_groups):
                    return True
                
                subject = subjects[len(given_groups)]
                shuffle(subject.groups)

                for group in subject.groups:
                    if group.capacity > 0:
                        collides = False
                        for g in given_groups.values():
                            if group.collides(g):
                                collides = True
                                break
                        
                        if not collides:
                            given_groups[subject] = group
                            group.capacity -= 1

                            if backtrack(subjects, given_groups):
                                return True

                            given_groups.pop(subject)
                            group.capacity += 1
                return False

            if backtrack(subjects, given_groups):
                self.students.append(Student(given_groups))
            else:
                raise RuntimeError("Unable to assign schedule for all students")
    
    def __str__(self):
        lines = ["== Population:"]
        for i, student in enumerate(self.students):
            lines.append(f"  Student {i+1}:")
            for subject, group in student.groups.items():
                lines.append(f"    {subject.name} -> g{group.id} (day {group.day}, {group.start}:00)")
        return "\n".join(lines)
