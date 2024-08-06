#include "run.hpp"
#include "plot3d.hpp"
#include "vtk_writer.hpp"
#include "solver.hpp"
#include "wake.hpp"
#include "domain.hpp"

string mesh_folder = "./mesh_files/";

void cylinder(int argc, char** args)
{
    Parameters::unsteady_problem = true;

    // create surface object
    shared_ptr<Surface> surface(new Surface);

    // read mesh file
    PLOT3D mesh;
    string filename = "cylinder.x";
    string mesh_path = mesh_folder + filename;
    mesh.set_surface(surface);
    mesh.read_surface(mesh_path);

    //set free stream velocity
    vector3d free_stream_velocity(1,0,0);

    double time_step = 1.5;
    double fluid_density = 1.225;

    // set blade at AOA
    surface->rotate_surface(vector3d(0,0,0),false);

    // create wake object
    shared_ptr<Wake> wake(new Wake());
    wake->add_lifting_surface(surface);
    wake->initialize(free_stream_velocity,time_step);

    // create writer
    shared_ptr<vtk_writer> writer(new vtk_writer());
    Solver solver(argc,args);
    solver.add_surface(surface);
    solver.add_wake(wake);
    solver.add_logger(writer);
    solver.set_free_stream_velocity(free_stream_velocity);
    solver.set_reference_velocity(free_stream_velocity);
    solver.set_fluid_density(fluid_density);

    // solve
    for(int i = 0; i < 10; i++){
        solver.solve(time_step,i);
        solver.convect_wake(time_step);
        wake->shed_wake(free_stream_velocity,time_step);
        solver.finalize_iteration();
        cout << "Body Force Coefficients = " << solver.get_body_force_coefficients() << endl;
    }
}

void wing(int argc, char** args)
{
    Parameters::unsteady_problem = true;

    // create surface object
    shared_ptr<Surface> surface(new Surface);

    // read mesh file
    PLOT3D mesh;
    // string filename = "NACA0012_1.x";
    string filename = "flying_wing.x";
    // string filename = "rectangular_wing.x";
    string mesh_path = mesh_folder + filename;
    mesh.set_surface(surface);
    mesh.read_surface(mesh_path);

    //set free stream velocity
    vector3d free_stream_velocity(1,0,0);

    double time_step = 1.5;
    double fluid_density = 1.225;

    // set blade at AOA
    surface->rotate_surface(vector3d(0,-5.,0),false);

    // create wake object
    shared_ptr<Wake> wake(new Wake());
    wake->add_lifting_surface(surface);
    wake->initialize(free_stream_velocity,time_step);

    // create writer
    shared_ptr<vtk_writer> writer(new vtk_writer());
    Solver solver(argc,args);
    solver.add_surface(surface);
    solver.add_wake(wake);
    solver.add_logger(writer);
    solver.set_free_stream_velocity(free_stream_velocity);
    solver.set_reference_velocity(free_stream_velocity);
    solver.set_fluid_density(fluid_density);

    // solve
    for(int i = 0; i < 10; i++){
        solver.solve(time_step,i);
        solver.convect_wake(time_step);
        wake->shed_wake(free_stream_velocity,time_step);
        solver.finalize_iteration();
        cout << "Body Force Coefficients = " << solver.get_body_force_coefficients() << endl;
    }
}

void rotating_blade(int argc, char** args)
{
    Parameters::unsteady_problem = true;

    // create surface object
    shared_ptr<Surface> surface(new Surface);

    // read mesh file
    PLOT3D mesh;
    // string filename = "blade_5.5_modified.x";
    string filename = "prop.x";
    string mesh_path = mesh_folder + filename;
    mesh.set_surface(surface);
    mesh.read_surface(mesh_path);

    // set free stream velocity
    vector3d free_stream_velocity(0,7,0);

    //set angular velocity
    vector3d surface_angular_velocity(0,71.63,0);
    surface->set_angular_velocity(surface_angular_velocity,false);

    double time_step = 0.015;
    double fluid_density = 1.225;

    surface->compute_panel_components();
    shared_ptr<Wake> wake(new Wake());
    wake->add_lifting_surface(surface);
    wake->initialize(free_stream_velocity,time_step);

    shared_ptr<vtk_writer> writer(new vtk_writer());

    Solver solver(argc,args);
    solver.add_surface(surface);
    solver.add_wake(wake);
    solver.add_logger(writer);
    solver.set_free_stream_velocity(free_stream_velocity);
    solver.set_reference_velocity(free_stream_velocity);
    solver.set_fluid_density(fluid_density);

    vector3d angular_displacement = surface_angular_velocity * (2 * M_PI / 60.0) * time_step;

    //write coordinates of the collocation points to data variable
    vector<vector<double>> data (4,vector<double>(surface->n_panels()));
    for(int p = 0; p < surface->n_panels(); p++){
        const vector3d& point = surface->get_collocation_point(p);
        data[0][p] = point[0];
        data[1][p] = point[1];
        data[2][p] = point[2];
    }

    for(int i = 0; i < 90; i++){

        solver.solve(time_step,i);
        solver.convect_wake(time_step);
        surface->rotate_surface(angular_displacement,true);
        wake->shed_wake(free_stream_velocity,time_step);
        solver.finalize_iteration();
    }

    //write Cp values to data
    for(int p = 0; p < surface->n_panels(); p++){
        data[3][p] = solver.get_pressure_coefficient(p);
    }

    // write to file
    ofstream file("Output/pressure_data.csv");
    file << "x,y,z,cp" << endl;
    for(int p = 0; p < surface->n_panels(); p++){
        file << scientific << data[0][p] << "," << data[1][p]
             << "," << data[2][p] << "," << data[3][p] << endl;
    }
    file.close();

    cout << "Exiting program." << endl;
}

void flapping_wing(int argc, char** args)
{
    Parameters::unsteady_problem = true;

    // create surface object
    shared_ptr<Surface> surface(new Surface);

    // read mesh file
    PLOT3D mesh;
    string filename = "NACA0012_1.x";
    string mesh_path = mesh_folder + filename;
    mesh.set_surface(surface);
    mesh.read_surface(mesh_path);

    double time_step = 0.025;
    double fluid_density = 1.225;

    /* Refer Low Speed Aerodynamics - J. Katz, A. Plotkin
     * second edition, page 417-418
     */
    double chord_length = 1.;
    //set free stream velocity
    vector3d free_stream_velocity(0.009*chord_length/time_step,0,0);
    //compute amplitude and frequency
    double max_amplitude = 0.019 * chord_length;
    double reduced_frequency = 8.57;
    double omega = reduced_frequency * 2 * free_stream_velocity[0] / chord_length;

    // create wake object
    shared_ptr<Wake> wake(new Wake());
    wake->add_lifting_surface(surface);
    wake->initialize(free_stream_velocity,time_step);

    // create writer
    shared_ptr<vtk_writer> writer(new vtk_writer());

    // create solver
    Solver solver(argc,args);
    solver.add_surface(surface);
    solver.add_wake(wake);
    solver.add_logger(writer);
    solver.set_free_stream_velocity(free_stream_velocity);
    solver.set_reference_velocity(free_stream_velocity);
    solver.set_fluid_density(fluid_density);

    vector3d surface_velocity(0,0,0);

    double time = 0;

    // solve
    for(int i = 0; i < 60; i++){

        solver.solve(time_step,i);
        solver.convect_wake(time_step);

        surface_velocity = vector3d(0,0,max_amplitude*cos(omega*time));
        surface->set_linear_velocity(surface_velocity);
        surface->translate_surface(surface_velocity*time_step);

        wake->shed_wake(free_stream_velocity,time_step);
        solver.finalize_iteration();

        time += time_step;

    }

    cout << "Exiting program." << endl;
}

void run(int argc, char** args)
{
    switch (Parameters :: test_case)
    {
    case 0:
        cylinder(argc,args);
        break;
    case 1:
        wing(argc,args);
        break;
    case 2:
        rotating_blade(argc,args);
        break;
    case 3:
        flapping_wing(argc,args);
        break;
    
    default:
        break;
    }

}
