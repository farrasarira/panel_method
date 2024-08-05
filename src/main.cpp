#include <iostream>
#include <run.hpp>
#include "parameters.hpp"
#include <omp.h>

int main(int argc, char** args){
    
    omp_set_num_threads(Parameters :: num_threads);
    
    run(argc,args);
    
    return 0;
}
