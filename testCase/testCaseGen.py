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
                    
best_score = 0
for i in range(10):
    job_list = random_test_case(8, 8, 100)
    score = get_score(job_list)
    print(i, ': ', score)
    if(score > best_score):
        best_score = score
        best_list = job_list
write_file("test.in", best_list, 8)
            