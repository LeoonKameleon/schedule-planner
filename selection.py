from __future__ import annotations

from random import choices, random, sample
from typing import Iterable

from population import Population


def objective_function(population: Population, alpha: float = 1.0) -> float:
	"""
	Compute objective value:
	Z = sum_{i,j} P_ij * x_ij - alpha * sum_{i,d} (e_id - s_id)

	The first term rewards assigning students to preferred groups.
	The second term penalizes daily spread (first class start vs last class end).
	"""
	if alpha < 0:
		raise ValueError("alpha must be >= 0")

	preference_score = 0.0
	spread_penalty = 0.0

	for student_index, student in enumerate(population.students):
		student_id = student_index + 1
		points_for_student = population.student_points.points[student_id]

		daily_starts: dict[int, list[int]] = {}
		daily_ends: dict[int, list[int]] = {}

		for group in student.groups.values():
			preference_score += points_for_student.get(group.id, 0)
			daily_starts.setdefault(group.day, []).append(group.start)
			daily_ends.setdefault(group.day, []).append(group.end)

		# If student has no classes on day d, that day's contribution is 0.
		for day in range(1, 6):
			starts = daily_starts.get(day)
			if not starts:
				continue
			s_id = min(starts)
			e_id = max(daily_ends[day])
			spread_penalty += e_id - s_id

	return preference_score - alpha * spread_penalty


def _objective_values(populations: Iterable[Population], alpha: float) -> list[float]:
	return [objective_function(population, alpha=alpha) for population in populations]


def ranking_selection(
	populations: list[Population],
	n_selected: int,
	alpha: float = 1.0,
) -> list[Population]:
	"""
	Select populations by rank (higher objective => higher rank/selection chance).
	Selection is with replacement, returning a mating pool of size n_selected.
	"""
	if n_selected <= 0:
		raise ValueError("n_selected must be > 0")
	if not populations:
		raise ValueError("populations cannot be empty")

	scored = list(zip(populations, _objective_values(populations, alpha=alpha)))
	ranked = sorted(scored, key=lambda item: item[1], reverse=True)

	# Linear rank weights: best gets N, worst gets 1.
	n = len(ranked)
	rank_weights = list(range(n, 0, -1))
	ranked_populations = [item[0] for item in ranked]
	return choices(ranked_populations, weights=rank_weights, k=n_selected)


def tournament_selection(
	populations: list[Population],
	n_selected: int,
	tournament_size: int = 3,
	alpha: float = 1.0,
	p_best: float = 1.0,
) -> list[Population]:
	"""
	Tournament selection based on objective value.

	For each selected parent:
	- draw 'tournament_size' candidates,
	- sort by objective descending,
	- pick best with probability p_best, otherwise consider the next one, etc.
	"""
	if n_selected <= 0:
		raise ValueError("n_selected must be > 0")
	if not populations:
		raise ValueError("populations cannot be empty")
	if tournament_size <= 0:
		raise ValueError("tournament_size must be > 0")
	if not (0 < p_best <= 1):
		raise ValueError("p_best must be in range (0, 1]")

	scores = {id(population): objective_function(population, alpha=alpha) for population in populations}
	selected: list[Population] = []

	for _ in range(n_selected):
		if tournament_size <= len(populations):
			contestants = sample(populations, k=tournament_size)
		else:
			contestants = choices(populations, k=tournament_size)

		ordered = sorted(contestants, key=lambda population: scores[id(population)], reverse=True)

		winner = ordered[-1]
		for candidate in ordered:
			if random() < p_best:
				winner = candidate
				break

		selected.append(winner)

	return selected
