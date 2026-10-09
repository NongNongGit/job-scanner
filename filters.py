def apply_filters(job, profile_config):
    filters = profile_config["filters"]

    # Remote-only filter
    if filters["remote_only"] and not job.get("remote", False):
        return False

    # Salary filter
    if job.get("salary", 0) < filters["min_salary"]:
        return False

    return True
