from random import randint
from typing import Optional


N_STUDENTS = 300
START_HOURS = list(range(8, 15))
DURATION = 1
DAYS = list(range(1, 6))


class Subject():
    def __init__(self, name: str):
        self.name = name
        self.groups = []
        self.n_groups = 0
    
    def add_group(self, group: "Group"):
        self.groups.append(group)
        self.n_groups += 1

    def __str__(self):
        return f"Subject({self.name})"


class Group():
    def __init__(self, id: int, subject: Subject, capacity: int, day: int, start: int, end: int):
        self.id = id
        self.subject = subject
        self.max_capacity = capacity
        self.day = day
        self.start = start
        self.end = end

    def collides(self, other: "Group") -> bool:
        if not isinstance(other, Group):
            raise ValueError("Collision check with a non-group object")
        if self.day != other.day:
            return False
        if self.start < other.end and self.end > other.start:
            return True
        return False


class SubjectList():
    def __init__(self, subjects: Optional[dict[str, Subject]] = None):
        self.subjects = subjects if subjects else {}
        self.current_group_id = 1
    
    def add_subject(self, name: str, n_groups: int):
        new_subject = Subject(name)
    
        base_capacity = N_STUDENTS // n_groups
        remainder = N_STUDENTS % n_groups
        
        for i in range(n_groups):
            current_capacity = base_capacity + (1 if i < remainder else 0)
            start = START_HOURS[randint(0, len(START_HOURS)-1)]
            g = Group(
                id=self.current_group_id,
                subject=new_subject,
                capacity=current_capacity,
                day=randint(1, 5),
                start=start,
                end=start+DURATION
            )
            new_subject.add_group(g)
            self.current_group_id += 1

        self.subjects[name] = new_subject
        print(f"Added subject: {name}, {n_groups} group(s)")

    def remove_subject(self, name: str):
        if name in self.subjects:
            removed = self.subjects.pop(name)
            print(f"Removed {name}, {removed.n_groups} group(s)")
        else:
            print(f"Subject {name} does not exist")

    def __str__(self):
        result = [f"{name}: {subject.n_groups} group(s)" for name, subject in self.subjects.items()]
        return "\n== Subject List:\n"+"\n".join(result)
