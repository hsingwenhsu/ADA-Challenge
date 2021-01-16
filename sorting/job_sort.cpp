#include <string>
#include <vector>
#include <sstream>    // for stringstream
#include <fstream>    // for ifstream
#include <utility>    // for pair
#include <iostream>
#include <algorithm>
 //compile: g++ -std=c++17 op_sort.cpp -o op_sort
 //example usage: ./op_sort ada-final-public/02.in 
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
        std::vector<int> deps;
        bool done{};
        double wd; //added by Hsu, for the algorithm
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

bool comp_op(const Operation &a, const Operation &b){
    if(a.wd>b.wd) return true;
    if(a.wd<b.wd) return false;
    if(a.depend_t<b.depend_t) return true;
    if(a.depend_t>b.depend_t) return false;
}

class Job {
    public:
        double weight{};
        double wds;
        std::vector<Operation> ops;
        std::stringstream result(){
            std::stringstream ss;
            size_t _size = ops.size();
            for (size_t i = 0; i < _size; i++)
                ss << ops[i].result().str();
            return ss;
        }
        void set_wds(double in_wds){
            wds = in_wds;
        }
        //function
        bool operator<(const Job &tmp_job) const{
            return tmp_job.wds<wds;
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

//sort for operations


int main(int argc, char** argv){
    auto [slices, jobs] = readTestCase(argv[1]); //const took off
    for(size_t i = 0; i < jobs.size(); i++){
        //std::cout << i << " weight: " << jobs[i].weight << std::endl;
        double wds_tmp = 0;
        for(size_t j = 0; j < jobs[i].ops.size(); j++){
            Operation tmp = jobs[i].ops[j]; //the op to be pushed into the vector
            wds_tmp+=tmp.duration*tmp.slices; //weight*duration
            //std::cout << jobs[i].ops[j].slices <<" "<< jobs[i].ops[j].duration<<std::endl;;
        }
        //std::cout<<std::endl;
        wds_tmp = wds_tmp*jobs[i].weight;
        jobs[i].set_wds(wds_tmp);
    }

    std::sort(jobs.begin(), jobs.end()); //sort jobs
    for(size_t i = 0; i<jobs.size(); i++){ //handle each job's operations
        //std::cout<<jobs[i].wds<<std::endl;
    }
}

