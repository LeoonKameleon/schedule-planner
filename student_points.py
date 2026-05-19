from random import randint, sample

from subject_lists import SubjectList
from config_loader import config


N_STUDENTS = config["N_STUDENTS"]
MIN_LIMIT_S = config["MIN_LIMIT_S"]
MAX_LIMIT_S = config["MAX_LIMIT_S"]
MAX_LIMIT_G = config["MAX_LIMIT_G"]

class StudentPoints():
    def __init__(self, subject_list: SubjectList):
        self.subject_list = subject_list
        self.points = {}
        self.generate()
    
    def generate(self):
        for student in range(1, N_STUDENTS+1):
            self.points[student] = {}
            for _, subject in self.subject_list.subjects.items():
                groups = subject.groups
                n_groups = subject.n_groups

                total_points = randint(MIN_LIMIT_S, min(MAX_LIMIT_S, n_groups*MAX_LIMIT_G))

                slots = sample(range(n_groups * MAX_LIMIT_G), total_points)
                pts = [0] * n_groups
                for s in slots:
                    pts[s // MAX_LIMIT_G] += 1

                for group, p in zip(groups, pts):
                    self.points[student][group.id] = p
    
    def __str__(self):
        lines = ["\n== Student Points:"]
        for student_id, groups in self.points.items():
            pts_str = ", ".join(f"g{group_id}: {points}" for group_id, points in groups.items())
            lines.append(f"Student {student_id}: {pts_str}")
        return "\n".join(lines)