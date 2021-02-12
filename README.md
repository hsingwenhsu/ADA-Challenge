# ADA Final Challenge 

## Usage

```
$ python3 main.py $input_file
```

## Introduction

- This is a walkthrough of our code for the final challenge of the course Algorithm Design and Analysis. We spent a lot of time on reading the docs of Google or-tools, and we hope that this walkthrough is helpful for anyone who is trying to understand the sample code provided by Google. 

- For Algorithm Design and Analysis's final challenge, we are tasked to solve a flexible job shop problem. However, the input and output format specifications are slightly different from the traditional flexible job shop problem. Therefore, we modified the sample code of the flexible jobshop problem: https://github.com/google/or-tools/blob/stable/examples/python/flexible_job_shop_sat.py

- According to the final challenge page: https://hackmd.io/6zxbedYCSLe8M8hW1Su0ww#Resources

  - The input format of the problem (This is an example. Also note that "slice" is equivalent to "machine" in traditional job shop problems. ):

    ```c
      3 //integer l -> # of slices available
      3 //integer n -> # of jobs
      3 //integer m1 -> #of operations in the job
      1.0 //real number w1 -> weight of the job
      1 10 0 // o1
      1 5 1 1 //o2
      1 7 1 1 //o3 
      1 //integer m2-> # of operation sin the job
      1.0 //real number w2 -> weight of the job
      2 5 0 //two slices, label them o4, o5
      1 //integer m3 -> #number of operations in the job
      1.0 //real number w3 -> #weight of the job
      1 7 0 //o6
    ```

  - The is the output format of the problem: 

    - For each job, there will be new lines of the same number of the job's operations. The first integer in each line specifies the starting time of the corresponding operation and the rest of the integers represent the machines that the operation used. 

    - Here's an example:

      ```c
      0 1 //the first job starts at time 0, machine 1 was used
      10 2 //the second job starts at time 10, machine 2 was used
      10 3 //the 
      0 2 3
      10 1
      ```

      

  - The Metric to Optimize:

    - $max_iC_i+\Sigma_i w_iC_i$

- To solve the problem, we adopted Google's OR-Tools, which is perfect for modeling constraint programming problems and scheduling problems. 

## Explanation of the Code

- For the explanation of the code, the example test case is used.

- Example test case:

  ```c
    3 //integer l -> # of slices available
    3 //integer n -> # of jobs
    3 //integer m1 -> #of operations in the job
    1.0 //real number w1 -> weight of the job
    1 10 0 // o1
    1 5 1 1 //o2
    1 7 1 1 //o3 
    1 //integer m2-> # of operation sin the job
    1.0 //real number w2 -> weight of the job
    2 5 0 //two slices, label them o4, o5
    1 //integer m3 -> #number of operations in the job
    1.0 //real number w3 -> #weight of the job
    1 7 0 //o6
  ```

### Input and Data Structure

- I am more comfortable with the term machine. So I will not be using the term "slice" for explanation, but `slice` is still used in the code. 

- To set up constraint for the problem with OR-Tools, having a data structure for jobs and operation is really important. The function: `read_input()`, read the input files and return three information that we  will need for the modeling of the problem. 

  ```
  jobs_data, weight, slice_num = read_input(name)
  ```

  - Format of `jobs_data`:

    ```python
    [[(1, 10, []), (1, 5, [1]), (1, 7, [1])], [(2, 5, [])], [(1, 7, [])]]
    ```

    - `(1, 10, [])` 
      - The first element represents the number of machines required for this operation (`1`). 
      - The second element represents the duration of the operation (`10`)
      - The third list represents the operation(s) that this operation depends on, in this case, the list is empty. 

  - Format of `weight`:

    ```python
    [1.0, 1.0, 1.0]
    ```

    - There are 3 jobs, and they all have the same weights (`1.0`).

  - `slice_num`

    - The number of machines we have. 

- Since this is a flexible job shop problem, we have to create alternatives for each operation. For example   `op1_1` (the first operation of job 1) could be on machine 1, 2, 3. The `convert2flexible()` function creates alternative for each job. 

  ```
  jobs = convert2flexible(jobs_data, slice_num)
  ```

  - The format of jobs:

    ```
    [[[(10, 0, [], 1), (10, 1, [], 1), (10, 2, [], 1)], [(5, 0, [1], 1), (5, 1, [1], 1), (5, 2, [1], 1)], [(7, 0, [1], 1), (7, 1, [1], 1), (7, 2, [1], 1)]], [[(5, 0, [], 2), (5, 1, [], 2), (5, 2, [], 2)]], [[(7, 0, [], 1), (7, 1, [], 1), (7, 2, [], 1)]]]
    ```

    - Let's take a closer look at the first operation of the first job: 

      ```
      [(10, 0, [], 1), (10, 1, [], 1), (10, 2, [], 1)]
      ```

      - The first integer represents the duration of the operation (10). According to the specification of the final challenge, each operation's duration does not vary for different machines
      - The second integer represents the machine that this operation is on. Since there are three machines, we have three alternatives (0, 1, 2). The index starts with 0 for the convenience of indexing the machines in a list, but machines' labels should start from 1 for the output file. 
      - The list represent the operations the operations that this operation depends on. In this case, the list is empty. 
      - The last term represent the number of machines required for this operation. 

### Flexible Job Shop

- Here's the explanation of the function `flexible_jobshop(jobs, weight, num_machines, filename)`

  - Arguments:
    - `jobs`: The data of jobs and operations. Explained in the previous section.
    - `weight`: A list containing the weights of each job. 
    - `num_machine`: The number of machines we have.
    - `filename` : The name of the input file. This is used to create a corresponding output file in the output folder. 

- At the very beginning, we specify the number of jobs, and machines

  ```python
  num_jobs = len(jobs) #3
  all_jobs = range(num_jobs) #For indexing purpose 0, 1, 2
  all_machines = range(num_machines) #For indexing purpose 0, 1, 2
  ```

- Create the constraint programming model with the OR-Tool's python module

  ```python
  model = cp_model.CpModel()
  ```

- Compute the horizon of the problem (The sum of duration of each operation)

  ```python
  horizon = 0
  for job in jobs:
  	for task in job:
  		horizon+=task[0][0] #sum the duration of each job's operation
  ```

  - For the example, `horizon = 34`

  - This is slightly different from the flexible job shop problem example code of OR-Tools because our operations' durations do not vary across different machines. 

- Setting up empty lists and dictionaries to store information 

  ```python
  intervals_per_resources = collections.defaultdict(list) 
  starts = {} 
  ends = {}
  presences = {}
  job_ends = []
  ```

  - `intervals_per_resources`
  - `starts`
    - indexed by `(job_id, op_id)`
    - Represents the starting time of the corresponding operation
  - `ends`
    - indexed by `(job_id, op_id)`
    - Represents the ending time of the corresponding operation
  - `presences`
    - indexed by `(job_id, op_id, machine_id-1)`
    - Represents whether or not the corresponding operation is on the machine
  - `job_ends`
    - store the ending time of each operation

- Creating intervals for each operation and alternatives (choices of machines)

  ```python
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
  ```

  

- Adding constraints for each machine (We don't want operations that should be on the same machine to run at the same time).

  ```python
  for machine_id in all_machines:
          intervals = intervals_per_resources[machine_id]
          if len(intervals)>1:
              model.AddNoOverlap(intervals)
  ```

  

- Adding constraints for each job. (The starting time of the next job should not be earlier than the ending time of the current job.)

  ```python
  for job_id in all_jobs:
          job = jobs[job_id]
          for task_id, task in enumerate(job):
              task = job[task_id]
              for dep in task[0][2]:
                  model.Add(starts[(job_id, task_id)]>=ends[(job_id, dep-1)])
  ```

- Specify the metric that we are optimizing according to the instruction of the final challenge:

  ```python
  #makespan objective 
  makespan = model.NewIntVar(0, horizon, 'makespan')
  model.AddMaxEquality(makespan, job_ends)
  #model.Minimize(makespan)
  model.Minimize(cp_model.LinearExpr.ScalProd([ends[(job_id, task_id)] for job_id, job in enumerate(jobs) for task_id, task in enumerate(
    job)], [math.ceil(weight[job_id]) for job_id, job in enumerate(jobs) for task_id, task in enumerate(
    job)])+makespan)
  ```

- Solve the model

  ```python
  solver = cp_model.CpSolver()
  solution_printer = SolutionPrinter()
  status = solver.SolveWithSolutionCallback(model, solution_printer)
  ```

## Reference:
- Google OR-Tools: https://developers.google.com/optimization
  

