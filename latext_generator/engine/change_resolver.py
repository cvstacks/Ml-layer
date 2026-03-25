from copy import deepcopy


def resolve_text(original, improved, decision=None):
    """
    Returns the final text depending on user decision.

    decision:
        True  -> accept improved
        False -> reject change (keep original)
        None  -> default to improved
    """

    if decision is True:
        return improved

    if decision is False:
        return original

    return improved


def resolve_resume(resume_json, original_json=None, decisions=None):
    """
    Apply accept/reject decisions to entire resume.

    decisions example:
    {
        "summary": False,
        "projects.0.description.2": False,
        "experience.1.description.0": False,
        "achievements.0": False,
        "skills": False
    }

    original_json: the original resume before improvements.
                   Required if any decision is False (to restore original text).
    """

    if decisions is None:
        decisions = {}

    if original_json is None:
        original_json = {}

    resume = deepcopy(resume_json)

    # ---- Summary ----
    if "summary" in decisions:
        resume["summary"] = resolve_text(
            original=original_json.get("summary", ""),
            improved=resume["summary"],
            decision=decisions["summary"]
        )

    # ---- Skills ----
    if "skills" in decisions:
        resume["skills"] = resolve_text(
            original=original_json.get("skills", []),
            improved=resume["skills"],
            decision=decisions["skills"]
        )

    # ---- Projects ----
    original_projects = original_json.get("projects", [])

    for p_index, project in enumerate(resume.get("projects", [])):

        original_project = original_projects[p_index] if p_index < len(original_projects) else {}

        # Project title
        title_key = f"projects.{p_index}.title"
        if title_key in decisions:
            project["title"] = resolve_text(
                original=original_project.get("title", ""),
                improved=project["title"],
                decision=decisions[title_key]
            )

        # Project descriptions
        original_descs = original_project.get("description", [])
        new_desc = []

        for d_index, sentence in enumerate(project.get("description", [])):

            key = f"projects.{p_index}.description.{d_index}"

            decision = decisions.get(key, None)

            original_sentence = original_descs[d_index] if d_index < len(original_descs) else ""

            final_sentence = resolve_text(
                original=original_sentence,
                improved=sentence,
                decision=decision
            )

            new_desc.append(final_sentence)

        project["description"] = new_desc

    # ---- Experience ----
    original_exps = original_json.get("experience", [])

    for e_index, exp in enumerate(resume.get("experience", [])):

        original_exp = original_exps[e_index] if e_index < len(original_exps) else {}

        # Role
        role_key = f"experience.{e_index}.role"
        if role_key in decisions:
            exp["role"] = resolve_text(
                original=original_exp.get("role", ""),
                improved=exp["role"],
                decision=decisions[role_key]
            )

        # Descriptions
        original_descs = original_exp.get("description", [])
        new_desc = []

        for d_index, bullet in enumerate(exp.get("description", [])):

            key = f"experience.{e_index}.description.{d_index}"
            decision = decisions.get(key, None)

            original_bullet = original_descs[d_index] if d_index < len(original_descs) else ""

            final_bullet = resolve_text(
                original=original_bullet,
                improved=bullet,
                decision=decision
            )

            new_desc.append(final_bullet)

        exp["description"] = new_desc

    # ---- Achievements ----
    original_achievements = original_json.get("achievements", [])

    new_achievements = []
    for a_index, achievement in enumerate(resume.get("achievements", [])):

        key = f"achievements.{a_index}"
        decision = decisions.get(key, None)

        original_ach = original_achievements[a_index] if a_index < len(original_achievements) else ""

        final_ach = resolve_text(
            original=original_ach,
            improved=achievement,
            decision=decision
        )

        new_achievements.append(final_ach)

    resume["achievements"] = new_achievements

    return resume