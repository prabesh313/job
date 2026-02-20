"""
Points Scoring Engine for Job Portal

Scoring Rules:
- Exact required skill match:        +10 pts each
- Partial/related skill match:       +5  pts each
- Nice-to-have skill match:          +5  pts each
- Experience meets requirement:      +20 pts
- Experience exceeds requirement:    +30 pts
- Experience below requirement:      +5  pts (still shows effort)

Max possible score depends on job requirements.
"""


EXPERIENCE_YEARS = {
    'entry': (0, 2),
    'mid': (2, 5),
    'senior': (5, 10),
    'lead': (10, 99),
}


def _skills_overlap(candidate_skills: list, job_skills: list) -> dict:
    """Return exact and partial matches between candidate and job skills."""
    exact = []
    partial = []
    unmatched = []

    for job_skill in job_skills:
        if job_skill in candidate_skills:
            exact.append(job_skill)
        elif any(job_skill in cs or cs in job_skill for cs in candidate_skills):
            partial.append(job_skill)
        else:
            unmatched.append(job_skill)

    return {'exact': exact, 'partial': partial, 'unmatched': unmatched}


def calculate_score(candidate_profile, job_post) -> dict:
    """
    Calculate match score between a candidate and a job post.

    Returns a dict with:
        - total: int
        - breakdown: dict with labeled point categories
        - max_possible: int (for percentage display)
    """
    candidate_skills = candidate_profile.get_skills_list()
    required_skills = job_post.get_required_skills_list()
    nice_skills = job_post.get_nice_skills_list()

    breakdown = {}
    total = 0

    # --- Required Skills ---
    req_match = _skills_overlap(candidate_skills, required_skills)
    req_exact_pts = len(req_match['exact']) * 10
    req_partial_pts = len(req_match['partial']) * 5
    breakdown['required_skills_exact'] = {
        'label': f"Exact required skill matches ({len(req_match['exact'])})",
        'skills': req_match['exact'],
        'points': req_exact_pts,
    }
    breakdown['required_skills_partial'] = {
        'label': f"Partial required skill matches ({len(req_match['partial'])})",
        'skills': req_match['partial'],
        'points': req_partial_pts,
    }
    total += req_exact_pts + req_partial_pts

    # --- Nice-to-have Skills ---
    nice_match = _skills_overlap(candidate_skills, nice_skills)
    nice_pts = (len(nice_match['exact']) + len(nice_match['partial'])) * 5
    breakdown['nice_skills'] = {
        'label': f"Nice-to-have skill matches ({len(nice_match['exact']) + len(nice_match['partial'])})",
        'skills': nice_match['exact'] + nice_match['partial'],
        'points': nice_pts,
    }
    total += nice_pts

    # --- Experience ---
    candidate_years = candidate_profile.years_experience
    min_years = job_post.min_years_experience

    if candidate_years >= min_years + 3:
        exp_pts = 30
        exp_label = f"Experience significantly exceeds requirement ({candidate_years} vs {min_years}+ yrs)"
    elif candidate_years >= min_years:
        exp_pts = 20
        exp_label = f"Experience meets requirement ({candidate_years} vs {min_years}+ yrs)"
    else:
        exp_pts = 5
        exp_label = f"Experience below requirement ({candidate_years} vs {min_years}+ yrs)"

    breakdown['experience'] = {
        'label': exp_label,
        'points': exp_pts,
    }
    total += exp_pts

    # --- Max possible score (for percentage bar) ---
    max_possible = (len(required_skills) * 10) + (len(nice_skills) * 5) + 30
    max_possible = max(max_possible, 1)  # Avoid division by zero

    return {
        'total': total,
        'max_possible': max_possible,
        'percentage': min(100, round((total / max_possible) * 100)),
        'breakdown': breakdown,
        'missing_skills': req_match['unmatched'],
    }
