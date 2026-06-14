def calculate_mrr(results, target_job_id):
    for i, res in enumerate(results):
        if res['id'] == target_job_id:
            return 1 / (i + 1)
    return 0