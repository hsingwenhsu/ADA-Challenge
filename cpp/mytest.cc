#include "absl/strings/match.h"
#include "google/protobuf/text_format.h"
#include "google/protobuf/wrappers.pb.h"
#include "ortools/base/commandlineflags.h"
#include "ortools/base/logging.h"
#include "ortools/base/timer.h"
#include "ortools/data/jobshop_scheduling.pb.h"
#include "ortools/data/jobshop_scheduling_parser.h"
#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model.pb.h"
#include "ortools/sat/model.h"
#include <iostream>
#include <string>
#include <vector>
#include <sstream>    // for stringstream
#include <fstream>    // for ifstream
#include <utility>    // for pair
#include <iostream>
#include <algorithm>

// using namespace std;

class Event {
    public:
        Event(){};
        Event(int t, int j, int o, bool s):time(t), job(j), op{o},is_start(s){}
        int time{};
        bool is_start{};
        int job{}, op{};
        // Use basic_string instead of vector for small-buffer optimization
        std::basic_string<uint8_t> slices;
        bool operator<(const Event &rhs) const {
            // Make sure to sort end events before start events
            return time != rhs.time ? time < rhs.time : is_start < rhs.is_start;
        }
};
class Operation {
    public:
        Operation(){
            startEvent = NULL;
            endEvent = NULL;
        }
        Operation(int s, int d, bool done): slices(s), duration(d), done(done){
            startEvent = NULL;
            endEvent = NULL;
        }

        int slices{};
        int duration{};
        int machine;
        std::vector<int> deps;
        bool done{};
        //double wd; //added by Hsu, for the algorithm
        int depend_t; //added by Hsu, this op should start after depend_t
        Event *startEvent, *endEvent;
        std::stringstream result(){
            std::stringstream ss;
            if(startEvent != NULL && endEvent != NULL){
                ss << std::to_string(startEvent -> time) << " ";
                size_t _size = startEvent -> slices.size();
                for (size_t i = 0; i < _size; i++){
                    ss << std::to_string(startEvent -> slices[i]) << " ";
                }
                ss << std::endl;
            }
            return ss;
        }
        /*bool operator > (const Operation& op) const{
            return (wd>op.wd);
        }*/
};

class Job {
    public:
        double weight{};
        std::vector<Operation> ops;
        std::stringstream result(){
            std::stringstream ss;
            size_t _size = ops.size();
            for (size_t i = 0; i < _size; i++)
                ss << ops[i].result().str();
            return ss;
        }
};

std::pair<int, std::vector<Job>> readTestCase( std::string testCase){
	std::ifstream infile(testCase);
    int l{}, N{}, m{};
    int s{}, d{}, dep{};
    std::string line;
    infile >> l;
    infile >> N;
    std::vector<Job> jobs;
    for(size_t i = 0; i < N; i++){
        Job now = Job();
        infile >> m;
        infile >> now.weight;
        std::getline(infile, line);
        for(size_t j = 0; j < m; j++){
            std::getline(infile, line);
            std::istringstream iss(line);
            iss >> s >> d;
            Operation op = Operation(s, d, false);
            while (iss >> dep)
                op.deps.push_back(dep);
            now.ops.push_back(op);
        }
        jobs.push_back(now);
    }
    return {l, jobs};
}

class JOB_SAT{
    public:
        std::vector < std::vector<Operation> > ops; //a job has multiple operations
        double weight;
};
class JOBS_DATA{
    public:
        std::vector <JOB_SAT> j_data;
        std::vector <double> weights; 
};

ABSL_FLAG(std::string, input, "", "Jobshop data file name.");
ABSL_FLAG(std::string, params, "", "Sat parameters in text proto format.");
ABSL_FLAG(bool, use_optional_variables, true,
          "Whether we use optional variables for bounds of an optional "
          "interval or not.");
ABSL_FLAG(bool, display_model, false, "Display jobshop proto before solving.");
ABSL_FLAG(bool, display_sat_model, false, "Display sat proto before solving.");

using operations_research::data::jssp::Job;
using operations_research::data::jssp::JobPrecedence;
using operations_research::data::jssp::JsspInputProblem;
using operations_research::data::jssp::Machine;
using operations_research::data::jssp::Task;
using operations_research::data::jssp::TransitionTimeMatrix;

namespace operations_research{
    namespace sat{
        int64 ComputeHorizon(JOBS_DATA jobs_data){
            //sum the duration
            int64 sum_of_duration = 0;
            for(size_t i = 0; i<jobs_data.j_data.size(); i++){//for each job
                for(size_t j = 0; j<jobs_data.j_data[i].ops.size(); j++){
                    int dtmp = jobs_data.j_data[i].ops[j][0].duration;//just take the first of each operations
                    sum_of_duration+=dtmp;
                }
            }//end for loop
            return sum_of_duration;
        }//end compute horizon

        //Solve flexible jobshop
        void Solve(JOBS_DATA jobs_data, int slices){
            CpModelBuilder cp_model;
            const int num_jobs = jobs_data.j_data.size();
            const int num_machines = slices;
            const int64 horizon = ComputeHorizon(jobs_data);
            std::vector<int> starts;
            std::vector<int> ends;
            const Domain all_horizon(0, horizon);
            const IntVar makespan = cp_model.NewIntVar(all_horizon);
            std::vector<std::vector<IntervalVar> > machine_to_intervals(num_machines);
            std::vector<std::vector<int> > machine_to_jobs(num_machines);
            std::vector<std::vector<IntVar> > machine_to_starts(num_machines);
            std::vector<std::vector<IntVar> > machine_to_ends(num_machines);
            std::vector<std::vector<BoolVar> > machine_to_presences(num_machines);
            std::vector <IntVar> job_starts(num_jobs);
            std::vector <IntVar> job_ends(num_jobs);
            std::vector < std::vector<IntVar> > all_starts;
            std::vector < std::vector<IntVar> > all_ends;
            std::vector <IntVar> task_starts;
            std::vector <IntVar> task_ends;
            int objective_offset = 0;
            std::vector <IntVar> objective_vars;
            std::vector <int64> objective_coeffs; //weight?
        
            //create empty start
            for(int i = 0; i<num_jobs; i++){
                std::vector <IntVar> intvar_vec;
                all_starts.push_back(intvar_vec);
                all_ends.push_back(intvar_vec);
                for(int j = 0; j<jobs_data.j_data[i].ops.size(); j++){
                    IntVar intvar_tmp;
                    all_starts[i].push_back(intvar_tmp);         
                }
            }
            const int num_alternatives = slices;//number of alternatives
            for(int i = 0; i<num_jobs; i++){//for each job
                for(int j = 0; j<jobs_data.j_data[i].ops.size(); j++){//for each operation
                    int dtmp = jobs_data.j_data[i].ops[j][0].duration;
                    const IntVar start = cp_model.NewIntVar(Domain(0, horizon));
                    const IntVar duration = cp_model.NewIntVar(Domain(dtmp, dtmp));
                    const IntVar end = cp_model.NewIntVar(Domain(0, horizon));
                    const IntervalVar interval = cp_model.NewIntervalVar(start, duration, end);
                    //store starts and ends of jobs for precedences
                    //job_starts[i] = start;
                    //jobs_ends[i] = end;
                    //task_starts.push_back(start);
                    //task_starts.push_back(end);
                    all_starts[i][j] = start;
                    all_ends[i][j] = end;
                    //if there is only one slice
                    if(num_alternatives==1){
                        const int m = 0;
                        machines_to_intervals[m].push_back(interval);
                        machines_to_jobs[m].push_back(i);
                        machines_to_starts[m].push_back(start);
                        machines_to_ends[m].push_back(end);
                        machines_to_presences[m].push_back(cp_model.TrueVar());
                    }else{//more than one alternatives
                        std::vector<BoolVar> presences;
                        for(int k = 0; k<num_alternatives; k++){
        
                            const BoolVar presence = cp_model.NewBoolVar();
                            const IntVar local_start = 
                                absl::GetFlag(FLAGS_use_optional_variables)
                                    ? cp_model.NewIntVar(Domain(0, horizon))
                                    : start;
                            const IntVar local_duration = cp_model.NewConstant(dtmp);
                            const IntVar local_end = 
                                absl::GetFlag(FLAGS_use_optional_variables)
                                    ? cp_model.NewIntVar(Domain(0, horizon))
                                    : end;
                            const InterVal local_interval = cp_model.NewOptionalIntervalVar(
                                local_start, local_duration, local_end, presence);
                            if(absl::GetFlag(FLAGS_use_optional_variables)){
                                cp_model.AddEquality(start, local_start).OnlyEnforceIf(presence);
                                cp_model.AddEquality(end, local_end).OnlyEnforceIf(presence);
                                cp_model.AddEquality(duration, local_duration).OnlyEnforceIf(presence);
                            }
                            //record relevant variables for later use
                            const m = k;
                            machine_to_intervals[m].push_back(local_interval);
                            machine_to_jobs[m].push_back(i);
                            machine_to_starts[m].push_back(local_start);
                            machine_to_ends[m].push_back(local_end);
                            machine_to_presences[m].push_back(presence);
                            //add cost if present
                            //objective_vars.push_back(presence);
                            //objective_coefficient.push_back(); //weight*duration*slices?
                            presences.push_back(presence);
                        }//end alternatives
                        int required_slices = jobs_data.j_data[i].ops[j][0].slices;
                        cp_model.AddEquality(Linear::BooleanSum(presences), required_slices);
                    }
                }
            }//end for each job
            //precedence
            for(int i = 0; i<jobs_data.j_data.size(); i++){//for each job
                for(int j = 0; j<jobs_data.j_data[i].ops.size(); j++){//for each op
                    for(int k = 0; k<jobs_data.j_data[i].ops[j][0].deps.size(); k++){
                        int dep_op = jobs_data.j_data[i].ops[j][0].deps[k];
                        cp_model.AddLessOrEqual(all_ends[i][dep_op-1], all_starts[i][j]);
                    }
                }
            }//end adding precedence
            //add no overlap
            for(int m = 0; m<num_machines; m++){
                cp_model.AddNoOverlap(machines_to_intervals[m]);
            }
            //add objective
            cp_model.AddMaxEquality(makespan, jobs_end);
            cp_model.Minimize(LinearExpr::ScalProd(job_ends, jobs_data.weights));
        }//end solve
    }
}

int main(int argc, char *argv[]){
    std::string testcase = "ada-final-public/00.in";
    //read input
    //const auto [slices, jobs] = readTestCase(argv[1]);

    const auto [slices, jobs] = readTestCase(testcase);
    std::cout<<"Slices: "<<slices<<std::endl;
    std::vector <Operation> ops;
    JOBS_DATA jobs_data;
    for(size_t i = 0; i < jobs.size(); i++){
        //for each job, create a job_sat object
        JOB_SAT job_sat_tmp;
        job_sat_tmp.weight = jobs[i].weight;
        jobs_data.weights.push_back(jobs[i].weight);
        std::cout << i << " weight: " << jobs[i].weight << std::endl;
        for(size_t j = 0; j < jobs[i].ops.size(); j++){
            //for each operation, create $num_machine alternative
            std::vector <Operation> op_vec_tmp;
            for(size_t k = 0; k<slices; k++){
                Operation op_tmp;
                op_tmp.duration = jobs[i].ops[j].duration;
                op_tmp.slices = jobs[i].ops[j].slices;
                op_tmp.machine = k;
                op_tmp.deps = jobs[i].ops[j].deps;
                op_vec_tmp.push_back(op_tmp);
            }
            job_sat_tmp.ops.push_back(op_vec_tmp);
            
            /*std::cout << jobs[i].ops[j].slices << " " << jobs[i].ops[j].duration;
            for(size_t k = 0; k < jobs[i].ops[j].deps.size(); k++){
                std::cout << " " << jobs[i].ops[j].deps[k];
            }*/
        }
        jobs_data.j_data.push_back(job_sat_tmp);
    }
    //test
    for(size_t i = 0; i<jobs_data.j_data.size(); i++){//for each job
        std::cout<<"Job id: "<<i<<std::endl;
        for(size_t j = 0; j<jobs_data.j_data[i].ops.size(); j++){//for each operation
            std::cout<<"Op id: "<<j<<std::endl;
            for(size_t k = 0; k<jobs_data.j_data[i].ops[j].size(); k++){
                std::cout<<"Duration: "<<jobs_data.j_data[i].ops[j][k].duration<<std::endl;
                std::cout<<"Machine: "<<jobs_data.j_data[i].ops[j][k].machine<<std::endl;
                std::cout<<"Slice: "<<jobs_data.j_data[i].ops[j][k].slices<<std::endl;
            }
        }
    }
    std::cout<<std::endl;
    //get horizon
    int64 Horizon = operations_research::sat::ComputeHorizon(jobs_data);
    std::cout<<"Horizon: "<<Horizon<<std::endl;
}