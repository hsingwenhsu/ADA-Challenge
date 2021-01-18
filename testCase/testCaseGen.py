import random
from random import randint

class job:
    def __init__(self, idx, weight):
        self.idx = idx
        self.op = []
        self.weight = weight
class op:
    def __init__(self, duration, slice_require):
        self.duration = duration
        self.slice_require = slice_require
        self.dependency = []

def random_test_case(slice_limit, job_limit, op_limit):
    slice_num = slice_limit
    job_num = 0
    total_op = 0
    job_list = []
    while(job_num < job_limit and total_op < op_limit):
        now_job = job(job_num ,round(random.uniform(0, 64), 6))
        job_num += 1
        op_num = randint(1, op_limit - total_op)
        now_op_num = 0
        while(now_op_num < op_num):
            now_op = op(randint(1, 96), randint(1,8))
            dep_num = randint(0, now_op_num)
            now_dep_num = 0
            while(now_dep_num < dep_num):
                dep = randint(1, now_op_num)
                if(not(dep in now_op.dependency)):
                    now_op.dependency.append(dep)
                    now_dep_num += 1
            now_op_num += 1
            now_job.op.append(now_op)
        total_op += op_num
        job_list.append(now_job)
    return job_list

def write_file(file_name, job_list, slice_num):
    f= open(file_name,"w+")
    f.write(f"{slice_num}\n{len(job_list)}\n")
    for j in job_list:
        f.write(f"{len(j.op)}\n{j.weight}\n")
        for op in j.op:
            f.write(f"{op.slice_require} {op.duration} {len(op.dependency)}")
            for d in op.dependency:
                f.write(f" {d}")
            f.write(f"\n")
    f.close()
def calculate(job_list):
    sum = 0
    for j in job_list:
        for op in j.op:
            sum += op.slice_require*op.duration
    return float(sum/8)
    
def get_score(job_list):
    score = 0
    num = 0
    for j in job_list:
        for op in j.op:
            for d in op.dependency:
                if(op.slice_require > j.op[d - 1].slice_require):
                    score += (op.slice_require - j.op[d - 1].slice_require)*j.op[d - 1].duration*j.weight
                    num += 1
    return float(score/num)

import collections
import math
import sys

# Import Python wrapper for or-tools CP-SAT solver.
from ortools.sat.python import cp_model

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0

    def on_solution_callback(self):
        """Called at each new solution."""
        print('Solution %i, time = %f s, objective = %i' %
              (self.__solution_count, self.WallTime(), self.ObjectiveValue()))
        self.__solution_count += 1

def read_input(filename):
    slice_num = 0 # l
    job_num = 0 # 
    cnt = 0
    jobs = []
    weights = []
    with open(filename) as input:
        while True:
            if cnt==0:
                slice_num = int(input.readline())
                cnt = cnt+1 
            elif cnt==1:
                job_num = int(input.readline())
                cnt = cnt+1
            else: 
                for i in range(job_num):
                    job_tmp = []
                    op_num = int(input.readline()) #number of operations for this job
                    weight = float(input.readline())
                    weights.append(weight)
                    for j in range(op_num):
                        op = input.readline()
                        print(op)
                        op = op.split(' ')
                        info_cnt = 0
                        op_slice = 0
                        op_dur = 0
                        depend_num = 0
                        op_depend = []
                        for op_info in op:
                            if info_cnt==0:
                                op_slice = int(op_info)
                                info_cnt = info_cnt+1
                            
                            elif info_cnt==1:
                                op_dur = int(op_info)
                                info_cnt = info_cnt+1
                            
                            elif info_cnt==2:
                                depend_num = int(op_info)
                                info_cnt = info_cnt+1
                                
                            else:
                                for k in range(depend_num):
                                    op_depend.append(int(op[3+k]))
                                break
        
                        job_tmp.append((op_slice, op_dur, op_depend))
                    jobs.append(job_tmp)
                break
            
    input.close()
    #print(jobs)
    return jobs, weights, slice_num



import collections
import math
import sys

# Import Python wrapper for or-tools CP-SAT solver.
from ortools.sat.python import cp_model

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0

    def on_solution_callback(self):
        """Called at each new solution."""
        #print('Solution %i, time = %f s, objective = %i' %
        #      (self.__solution_count, self.WallTime(), self.ObjectiveValue()))
        self.__solution_count += 1

def read_input(filename):
    slice_num = 0 # l
    job_num = 0 # 
    cnt = 0
    jobs = []
    weights = []
    with open(filename) as input:
        while True:
            if cnt==0:
                slice_num = int(input.readline())
                cnt = cnt+1 
            elif cnt==1:
                job_num = int(input.readline())
                cnt = cnt+1
            else: 
                for i in range(job_num):
                    job_tmp = []
                    op_num = int(input.readline()) #number of operations for this job
                    weight = float(input.readline())
                    weights.append(weight)
                    for j in range(op_num):
                        op = input.readline()
                        #print(op)
                        op = op.split(' ')
                        info_cnt = 0
                        op_slice = 0
                        op_dur = 0
                        depend_num = 0
                        op_depend = []
                        for op_info in op:
                            if info_cnt==0:
                                op_slice = int(op_info)
                                info_cnt = info_cnt+1
                            
                            elif info_cnt==1:
                                op_dur = int(op_info)
                                info_cnt = info_cnt+1
                            
                            elif info_cnt==2:
                                depend_num = int(op_info)
                                info_cnt = info_cnt+1
                                
                            else:
                                for k in range(depend_num):
                                    op_depend.append(int(op[3+k]))
                                break
        
                        job_tmp.append((op_slice, op_dur, op_depend))
                    jobs.append(job_tmp)
                break
            
    input.close()
    #print(jobs)
    return jobs, weights, slice_num

def convert2flexible(jobs_data, machine_num):
    jobs = []
    for job_data in jobs_data:
        job = []
        for op in job_data:
            op_alternative = []
            for i in range(machine_num):
                op_alternative.append((op[1], i, op[2], op[0]))
                #op_alternative.append((op[1], i))
            job.append(op_alternative)
        jobs.append(job)
    return jobs

def flexible_jobshop(jobs, weight, num_machines, filename):
    num_jobs = len(jobs)
    all_jobs = range(num_jobs)
    all_machines = range(num_machines)

    model = cp_model.CpModel()

    #compute horizon
    horizon = 0
    for job in jobs:
        for task in job:
            horizon+=task[0][0] #just add the duration
    
    intervals_per_resources = collections.defaultdict(list)
    starts = {}
    ends = {}
    presences = {}
    job_ends = []
    #for all the jobs
    for job_id in all_jobs:
        job = jobs[job_id]
        num_tasks = len(job)
        for task_id in range(num_tasks):
            task = job[task_id]
            num_alternatives = len(task) #number of entries for an op
            all_alternatives = range(num_alternatives) 
            dur = task[0][0] #duration of this op
            #create main interval for tasks
            suffix_name = '_j%i_t%i' % (job_id, task_id)
            start = model.NewIntVar(0, horizon, 'start'+suffix_name)
            duration = model.NewIntVar(dur, dur, 'duration'+suffix_name) #dur<=duration<=duration
            end = model.NewIntVar(0, horizon, 'end'+suffix_name)
            
            interval = model.NewIntervalVar(start, duration, end, 'interval'+suffix_name)
            #Store starts, ends
            starts[(job_id, task_id)] = start
            ends[(job_id, task_id)] = end
            if num_alternatives > 1:
                l_presences = []
                for alt_id in all_alternatives:
                    alt_suffix = '_j%i_t%i_a%i' % (job_id, task_id, alt_id)
                    l_presence = model.NewBoolVar('presence'+alt_suffix)
                    l_start = model.NewIntVar(0, horizon, 'start'+alt_suffix)
                    #l_duration = model.NewIntVar(dur, dur, 'duration'+alt_suffix)
                    l_duration = dur
                    l_end = model.NewIntVar(0, horizon, 'end'+alt_suffix)
                    l_interval = model.NewOptionalIntervalVar(
                        l_start, l_duration, l_end, l_presence,
                        'interval'+alt_suffix)
                    l_presences.append(l_presence)
                    model.Add(start==l_start).OnlyEnforceIf(l_presence)
                    model.Add(duration==l_duration).OnlyEnforceIf(l_presence)
                    model.Add(end==l_end).OnlyEnforceIf(l_presence)
                    #add the local interval to the right machine
                    intervals_per_resources[task[alt_id][1]].append(l_interval)
                    presences[(job_id, task_id, alt_id)] = l_presence
                
                required_slice = task[0][3] #slice is in the third entry
                model.Add(sum(l_presences)==required_slice)
                #model.Add(sum(l_presences)==1)
            else:
                intervals_per_resources[task[0][1]].append(interval)
                presences[(job_id, task_id, 0)] = model.NewConstant(1)

            job_ends.append(end)
            #end for all the jobs
    #create machines constraints
    for machine_id in all_machines:
        intervals = intervals_per_resources[machine_id]
        if len(intervals)>1:
            model.AddNoOverlap(intervals)
    
    for job_id in all_jobs:
        job = jobs[job_id]
        for task_id, task in enumerate(job):
            task = job[task_id]
            for dep in task[0][2]:
                model.Add(starts[(job_id, task_id)]>=ends[(job_id, dep-1)])
    
    #makespan objective 
    makespan = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(makespan, job_ends)
    #model.Minimize(makespan)
    model.Minimize(cp_model.LinearExpr.ScalProd([ends[(job_id, task_id)] for job_id, job in enumerate(jobs) for task_id, task in enumerate(
        job)], [math.ceil(weight[job_id]) for job_id, job in enumerate(jobs) for task_id, task in enumerate(
        job)])+makespan)

    # Solve model.
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter()
    status = solver.SolveWithSolutionCallback(model, solution_printer)

    # Print final solution
    """
    for job_id in all_jobs:
        print('Job %i:' % job_id)
        for task_id in range(len(jobs[job_id])):
            start_value = solver.Value(starts[(job_id, task_id)])
            machine = -1
            duration = -1
            selected = -1
            for alt_id in range(len(jobs[job_id][task_id])):
                print('presences: ')
                ptmp = solver.Value(presences[(job_id, task_id, alt_id)])
                print(ptmp)
                if solver.Value(presences[(job_id, task_id, alt_id)])==1:
                    duration = jobs[job_id][task_id][alt_id][0]
                    machine = jobs[job_id][task_id][alt_id][1]
                    selected = alt_id
                    print(
                        '  task_%i_%i starts at %i (alt %i, machine %i, duration %i)' %
                        (job_id, task_id, start_value, selected, machine, duration))
        
    print('Solve status: %s' % solver.StatusName(status))
    print('Optimal objective value: %i' % solver.ObjectiveValue())
    print('Statistics')
    print('  - conflicts : %i' % solver.NumConflicts())
    print('  - branches  : %i' % solver.NumBranches())
    print('  - wall time : %f s' % solver.WallTime())
    #try to output the format of ada challenge
    """
    filename = filename.split('/')[-1]
    filename = filename.split('.')[0]+'.out'
    f = open('output/'+filename, "w")
    #print('ADA Challenge OUTPUT')
    fintime = 0
    for job_id in all_jobs:
        for task_id in range(len(jobs[job_id])):
            start_val = solver.Value(starts[(job_id, task_id)])
            machine = -1
            duration = -1
            duration = -1
            selected = -1
            ans = str(start_val)
            for alt_id in range(len(jobs[job_id][task_id])):
                if solver.Value(presences[(job_id, task_id, alt_id)])==1:
                    machine = jobs[job_id][task_id][alt_id][1]
                    duration = jobs[job_id][task_id][alt_id][0]
                    tmp = start_val+duration
                    if fintime<tmp:
                        fintime = tmp
                    ans = ans+' '+str(machine+1)
            print(ans)
            ans = ans+'\n'
            f.write(ans)
    f.close()
    #print information
    print('Optimal objective value: %i' % solver.ObjectiveValue())
    print('Finish time: '+str(fintime))
    return fintime




# best_score = 0
# for i in range(10):
#     job_list = random_test_case(8, 8, 100)
#     score = get_score(job_list)
#     print(i, ': ', score)
#     if(score > best_score):
#         best_score = score
#         best_list = job_list
# write_file("../ada-final-public/loop.in", best_list, 8)

ideal_time = []
for i in range(10):
    job_list = random_test_case(8, 8, 100)
    # score = get_score(job_list)
    # print(i, ': ', score)
    # if(score > best_score):
    #     best_score = score
    #     best_list = job_list
    ideal_time.append(coculate(job_list))
    write_file("../ada-final-public/my" + i + ".in", best_list, 8)

best_util = 0
idx = 0
path = 'ada-final-public/'
for i in range(10):
    name = path + "my" + i + ".in"
    jobs_data, weight, slice_num = read_input(name)
    jobs = convert2flexible(jobs_data, slice_num)
    #print(jobs)
    time_cost = flexible_jobshop(jobs, weight, slice_num, name)
    util = float(ideal_time[i]/time_cost)
    print(i, " : ", util)
    if(util > best_util):
        best_util = util
        idx = i
print("best", i)