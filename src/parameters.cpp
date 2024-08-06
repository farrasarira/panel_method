#include "parameters.hpp"
#include <string>

bool Parameters :: parallel_comp = true;
int Parameters :: num_threads = 6;

int Parameters :: test_case = 
    // Uncomment one of the following test case.
    // 0 ; //cylinder
    1 ; // NACA 0012 Wing
    // 2 ; // Rotating Blade
    // 3 ; // Flapping Wing


double Parameters :: inversion_tolerance = 1e-12;

double Parameters :: farfield_factor = 10.0;

double Parameters :: trailing_edge_wake_shed_factor = 0.25;

bool Parameters :: unsteady_problem = false;

double Parameters :: static_wake_length = 1.0;

bool Parameters :: static_wake = false;

bool Parameters :: use_vortex_core_model = false;
