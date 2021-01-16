import collections
import math

# Import Python wrapper for or-tools CP-SAT solver.
from ortools.sat.python import cp_model


def MinimalJobshopSat():
    """Minimal jobshop problem."""
    # Create the model.
    model = cp_model.CpModel()

    weight = [1.0, 1.0, 1.0]  # weight of each jobs
    jobs_data = [  # task = (slice, processing_time, last dependency).
        [(1, 10, 0), (1, 5, 1), (1, 7, 1)],  # Job1
        [(2, 5, 0)],  # Job2
        [(1, 7, 0)]  # Job3
    ]

    machines_count = 3  # 有三個slice

    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple(
        'task_type', 'start end interval')

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    intervals = []
    demands = []
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            duration = task[1]
            suffix = '_%i_%i' % (job_id, task_id)
            start_var = model.NewIntVar(0, horizon, 'start' + suffix)
            end_var = model.NewIntVar(0, horizon, 'end' + suffix)
            interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                                'interval' + suffix)
            all_tasks[job_id, task_id] = task_type(
                start=start_var, end=end_var, interval=interval_var)
            intervals.append(interval_var)
            demands.append(task[0])

    # constraints on max machine in the same time
    model.AddCumulative(intervals, demands, machines_count)
    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            if task[2]:
                model.Add(all_tasks[job_id, task_id].start >=
                          all_tasks[job_id, task[2]-1].end)

    # Makespan objective.
    obj_var = model.NewIntVar(0, horizon, 'makespan')

    model.AddMaxEquality(obj_var, [all_tasks[job_id, task_id].end for job_id, job in enumerate(jobs_data) for task_id, task in enumerate(
        job)])

    model.Minimize(cp_model.LinearExpr.ScalProd([all_tasks[job_id, task_id].end for job_id, job in enumerate(jobs_data) for task_id, task in enumerate(
        job)], [math.ceil(weight[job_id]) for job_id, job in enumerate(jobs_data) for task_id, task in enumerate(
            job)])+obj_var)

    # Solve model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                print('job_%i_%i' % (job_id, task_id), '[%i~%i]' % (solver.Value(
                    all_tasks[job_id, task_id].start), solver.Value(
                    all_tasks[job_id, task_id].start)+task[1]))


MinimalJobshopSat()
