from student_points import StudentPoints
from subject_lists import Group, Subject, SubjectList
from random import random, shuffle


class Student():
    def __init__(self, groups: dict[Subject, Group]):
        self.groups = groups


class Schedule():
    def __init__(self, subject_list: SubjectList, student_points: StudentPoints):
        self.subject_list = subject_list
        self.student_points = student_points
        self.students = []
    
    def populate(self):
        # Rebuild this schedule from scratch on fresh capacities.
        self.students = []
        
        capacity_left = {}
        for subject in self.subject_list.subjects.values():
            for group in subject.groups:
                capacity_left[group.id] = group.max_capacity

        for _ in self.student_points.points:
            given_groups = {}
            subjects = list(self.subject_list.subjects.values())
            shuffle(subjects)
            
            def backtrack(subjects, given_groups):
                if len(subjects) == len(given_groups):
                    return True
                
                subject = subjects[len(given_groups)]
                shuffle(subject.groups)

                for group in subject.groups:
                    if capacity_left[group.id] > 0:
                        # Reject groups that collide with already chosen classes for this student.
                        collides = False
                        for g in given_groups.values():
                            if group.collides(g):
                                collides = True
                                break
                        
                        if not collides:
                            given_groups[subject] = group
                            capacity_left[group.id] -= 1

                            if backtrack(subjects, given_groups):
                                return True

                            given_groups.pop(subject)
                            capacity_left[group.id] += 1
                return False

            if backtrack(subjects, given_groups):
                self.students.append(Student(given_groups))
            else:
                raise RuntimeError("Unable to assign schedule for all students")

    def _points_for(self, student_index: int, group_id: int):
        student_id = student_index + 1
        return self.student_points.points[student_id].get(group_id, 0)

    @staticmethod
    def _collides_with_plan(plan: dict[str, Group], candidate: Group, skip_subject: str | None = None):
        for subject_name, group in plan.items():
            if skip_subject is not None and subject_name == skip_subject:
                continue
            if candidate.collides(group):
                return True
        return False

    def is_feasible(self):
        # Validate the full schedule: complete assignments, no collisions, no overflow.
        subject_names = list(self.subject_list.subjects.keys())
        if len(self.students) != len(self.student_points.points):
            return False

        group_loads = {}
        for subject in self.subject_list.subjects.values():
            for group in subject.groups:
                group_loads[group.id] = 0

        for student in self.students:
            if len(student.groups) != len(subject_names):
                return False

            assigned_names = {subject.name for subject in student.groups}
            if assigned_names != set(subject_names):
                return False

            chosen_groups = list(student.groups.values())
            for i in range(len(chosen_groups)):
                for j in range(i + 1, len(chosen_groups)):
                    if chosen_groups[i].collides(chosen_groups[j]):
                        return False

            for group in chosen_groups:
                group_loads[group.id] += 1

        group_limits = {}
        for subject in self.subject_list.subjects.values():
            for group in subject.groups:
                group_limits[group.id] = group.max_capacity

        for group_id, load in group_loads.items():
            if load > group_limits[group_id]:
                return False

        return True

    def crossover(self, other: "Schedule"):
        if self.subject_list is not other.subject_list:
            raise ValueError("Parents must share the same SubjectList instance")
        if len(self.students) != len(other.students):
            raise ValueError("Parents must have the same number of students")

        # Work on free seats counters, independent from mutable Group.capacity state.
        subject_names = list(self.subject_list.subjects.keys())
        capacity_left = {}
        occupants = {}
        for subject in self.subject_list.subjects.values():
            for group in subject.groups:
                capacity_left[group.id] = group.max_capacity
                occupants[group.id] = set()

        # Convert student plans to subject-name keys to simplify lookups during repair.
        parent_a = []
        parent_b = []
        for student in self.students:
            parent_a.append({subject.name: group for subject, group in student.groups.items()})
        for student in other.students:
            parent_b.append({subject.name: group for subject, group in student.groups.items()})

        child_by_name = [dict() for _ in self.students]
        unresolved = []

        def assign(student_index: int, subject_name: str, group: Group):
            # Centralized assign keeps all bookkeeping structures consistent.
            child_by_name[student_index][subject_name] = group
            capacity_left[group.id] -= 1
            occupants[group.id].add(student_index)

        def unassign(student_index: int, subject_name: str):
            old_group = child_by_name[student_index].pop(subject_name)
            capacity_left[old_group.id] += 1
            occupants[old_group.id].discard(student_index)

        # First pass: inherit from parents where possible, if not, mark for repair in unresolved.
        for student_index in range(len(self.students)):
            plan = child_by_name[student_index]
            for subject_name in subject_names:
                group_a = parent_a[student_index][subject_name]
                group_b = parent_b[student_index][subject_name]

                # Order because if one fail we try the other before marking as unresolved.
                candidate_order = [group_a] if group_a.id == group_b.id else ([group_a, group_b] if random() < 0.5 else [group_b, group_a])

                chosen = None
                for candidate in candidate_order:
                    if capacity_left[candidate.id] <= 0:
                        continue
                    if self._collides_with_plan(plan, candidate):
                        continue
                    chosen = candidate
                    break

                if chosen is not None:
                    assign(student_index, subject_name, chosen)
                else:
                    # Leave unresolved genes for the repair phase.
                    unresolved.append((student_index, subject_name))

        # Repair pass: greedy assignment with one-step ejection chains.
        for student_index, subject_name in unresolved:
            # Sanity check - make sure this subject is not assinged
            if subject_name in child_by_name[student_index]:
                continue


            # Sort groups by candidate's preference and try to assign in that order.
            subject = self.subject_list.subjects[subject_name]
            plan = child_by_name[student_index]
            ranked_groups = sorted(
                subject.groups,
                key=lambda g: self._points_for(student_index, g.id),
                reverse=True
            )

            placed = False

            # Try to assing to groups with free capacity.
            for candidate in ranked_groups:
                if capacity_left[candidate.id] <= 0:
                    continue
                if self._collides_with_plan(plan, candidate):
                    continue
                assign(student_index, subject_name, candidate)
                placed = True
                break

            if placed:
                continue

            # No free seats, try to find a swap within ranked groups to free a spot in a preferred group.
            for target in ranked_groups:
                if self._collides_with_plan(plan, target):
                    continue

                # One-step ejection chain: move one occupant elsewhere to free target.
                displaced_students = list(occupants[target.id])
                shuffle(displaced_students)
                for displaced_index in displaced_students:
                    displaced_plan = child_by_name[displaced_index]

                    alternatives = sorted(
                        subject.groups,
                        key=lambda g: self._points_for(displaced_index, g.id),
                        reverse=True
                    )

                    moved = False
                    for alt in alternatives:
                        if alt.id == target.id:
                            continue
                        if capacity_left[alt.id] <= 0:
                            continue
                        if self._collides_with_plan(displaced_plan, alt, skip_subject=subject_name):
                            continue

                        # Perform the swap only after confirming a valid alternative.
                        unassign(displaced_index, subject_name)
                        assign(displaced_index, subject_name, alt)
                        assign(student_index, subject_name, target)
                        moved = True
                        placed = True
                        break

                    if moved:
                        break

                if placed:
                    break

            if not placed:
                # This crossover attempt failed to repair all conflicts.
                return None

        child = Schedule(self.subject_list, self.student_points)
        for assignment in child_by_name:
            child.students.append(
                Student({self.subject_list.subjects[name]: group for name, group in assignment.items()})
            )

        if not child.is_feasible():
            return None
        return child
    
    

    def view_schedule(self):
        from subject_lists import START_HOURS, DAYS
        
        def format_hour(h: float) -> str:
            hours = int(h)
            minutes = int((h % 1) * 60)
            return f"{hours:02}:{minutes:02}"
        
        names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        width = 25
        
        # Oblicz zajętość dla tego konkretnego osobnika
        group_loads = {}
        for subject in self.subject_list.subjects.values():
            for group in subject.groups:
                group_loads[group.id] = 0
                
        for student in self.students:
            for group in student.groups.values():
                group_loads[group.id] += 1
                
        slots = {}
        for subject in self.subject_list.subjects.values():
            for group in subject.groups:
                load = group_loads[group.id]
                slots[(group.day, group.start)] = slots.get((group.day, group.start), []) + [f"{subject.name[:15]} ({load}/{group.max_capacity})"]
        
        print(f"{'':6}|" + "|".join(f"{d:^{width}}" for d in names))
        print("-" * (7 + (width+1) * 5))
        for hour in START_HOURS:
            n = max(len(slots.get((day, hour), [])) for day in DAYS)
            if n == 0:
                continue
            for i in range(n):
                row = f"{format_hour(hour):6}|" if i == 0 else f"{'':6}|"
                row += "|".join(f"{slots.get((day, hour), [])[i] if i < len(slots.get((day, hour), [])) else '':^{width}}" for day in DAYS)
                print(row)
            print("-" * (7 + (width+1) * 5))

    def __str__(self):
        lines = ["== Schedule:"]
        for i, student in enumerate(self.students):
            lines.append(f"Student {i+1}:")
            for subject, group in student.groups.items():
                lines.append(f"{subject.name} -> g{group.id} (day {group.day}, {group.start}:00)")
        return "\n".join(lines)
