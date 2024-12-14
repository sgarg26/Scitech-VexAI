#include "main.h"
#include "lemlib/api.hpp" // IWYU pragma: keep
#include "lemlib/chassis/chassis.hpp"
#include "pros/abstract_motor.hpp"
#include "pros/misc.hpp"
#include "pros/motor_group.hpp"
#include "pros/rtos.hpp"
#include <cctype>
#include <iostream>
#include <string>
#include <vector>

// lemlib docs:
// https://lemlib.readthedocs.io/en/stable/tutorials/2_configuration.html
using namespace std;

char data_received[300] = {0};

/**
 * Initialize motors
 * TODO: add correct motor config
 */
pros::MotorGroup
    left_motors({1, -2, 3, -4},
                pros::MotorGearset::blue); // left motors on ports 1, 2, 3
pros::MotorGroup
    right_motors({-10, 9, -8, 7},
                 pros::MotorGearset::blue); // right motors on ports 4, 5, 6

/**
 * Drivetrain settings
 * TODO: add correct track width and wheel diameter.
 */
lemlib::Drivetrain drivetrain(&left_motors,               // left motor group
                              &right_motors,              // right motor group
                              12,                         // 10 inch track width
                              lemlib::Omniwheel::NEW_275, // using new 4" omnis
                              600, // drivetrain rpm is 360
                              2    // horizontal drift is 2 (for now)
);

/**
 * Odom settings
 */
pros::Imu imu(15);

/**
 * PID settings
 * TODO: need to tweak again, these are just placeholders.
 */
// lateral PID controller
lemlib::ControllerSettings
    lateral_controller(10,  // proportional gain (kP)
                       0,   // integral gain (kI)
                       3,   // derivative gain (kD)
                       3,   // anti windup
                       1,   // small error range, in inches
                       100, // small error range timeout, in milliseconds
                       3,   // large error range, in inches
                       500, // large error range timeout, in milliseconds
                       20   // maximum acceleration (slew)
    );

// angular PID controller
lemlib::ControllerSettings
    angular_controller(2,   // proportional gain (kP)
                       0,   // integral gain (kI)
                       10,  // derivative gain (kD)
                       3,   // anti windup
                       1,   // small error range, in degrees
                       100, // small error range timeout, in milliseconds
                       3,   // large error range, in degrees
                       500, // large error range timeout, in milliseconds
                       0    // maximum acceleration (slew)
    );

// odometry settings
lemlib::OdomSensors sensors(
    nullptr, // vertical tracking wheel 1, set to null
    nullptr, // vertical tracking wheel 2, set to nullptr as we are using IMEs
    nullptr, // horizontal tracking wheel 1
    nullptr, // horizontal tracking wheel 2, set to nullptr as we don't have a
             // second one
    &imu     // inertial sensor
);

// create the chassis
lemlib::Chassis chassis(drivetrain,         // drivetrain settings
                        lateral_controller, // lateral PID settings
                        angular_controller, // angular PID settings
                        sensors             // odometry sensors
);

/**
 * A callback function for LLEMU's center button.
 *
 * When this callback is fired, it will toggle line 2 of the LCD text between
 * "I was pressed!" and nothing.
 */
void on_center_button() {
    static bool pressed = false;
    pressed = !pressed;
    if (pressed) {
        pros::lcd::set_text(2, "I was pressed!");
    } else {
        pros::lcd::clear_line(2);
    }
}

/**
 * Runs initialization code. This occurs as soon as the program is started.
 *
 * All other competition modes are blocked by initialize; it is recommended
 * to keep execution time for this mode under a few seconds.
 */
void initialize() {
    pros::lcd::initialize();
    pros::lcd::set_text(1, "Hello PROS User!");

    pros::lcd::register_btn1_cb(on_center_button);
}

/**
 * Runs while the robot is in the disabled state of Field Management System or
 * the VEX Competition Switch, following either autonomous or opcontrol. When
 * the robot is enabled, this task will exit.
 */
void disabled() {}

/**
 * Runs after initialize(), and before autonomous when connected to the Field
 * Management System or the VEX Competition Switch. This is intended for
 * competition-specific initialization routines, such as an autonomous selector
 * on the LCD.
 *
 * This task will exit when the robot is enabled and autonomous or opcontrol
 * starts.
 */
void competition_initialize() {}

/**
 * Runs the user autonomous code. This function will be started in its own task
 * with the default priority and stack size whenever the robot is enabled via
 * the Field Management System or the VEX Competition Switch in the autonomous
 * mode. Alternatively, this function may be called in initialize or opcontrol
 * for non-competition testing purposes.
 *
 * If the robot is disabled or communications is lost, the autonomous task
 * will be stopped. Re-enabling the robot will restart the task, not re-start it
 * from where it left off.
 */
void autonomous() {}

vector<vector<int>> parse2DArray(string data) {
    vector<vector<int>> array;
    vector<int> row;
    string cur_coord;
    bool is_new_row = false;

    for (int i = 0; i < data.length() - 1; i++) {
        if (data[i] == '[') {
            is_new_row = false;
            row.clear();
        } else if (isdigit(data[i])) {
            cur_coord += data[i];
        } else if (data[i] == ',' && !is_new_row) {
            row.push_back(stoi(cur_coord));
            cur_coord.clear();
        } else if (data[i] == ']') {
            is_new_row = true;
            row.push_back(stoi(cur_coord));
            cur_coord.clear();
            array.push_back(row);
        }
    }

    return array;
}

/**
 * Reads stdin for information from RPI.
 *
 */
vector<vector<int>> read_from_pi() {
    string data;
    vector<vector<int>> array;
    cout << "waiting for data\n";
    getline(cin, data);
    cout << data;
    // printf("%s\n", data_received);
    if (data.length() > 1) {
        array = parse2DArray(data);
        return array;
    }
    return array;
}

/**
 * Runs the operator control code. This function will be started in its own task
 * with the default priority and stack size whenever the robot is enabled via
 * the Field Management System or the VEX Competition Switch in the operator
 * control mode.
 *
 * If no competition control is connected, this function will run immediately
 * following initialize().
 *
 * If the robot is disabled or communications is lost, the
 * operator control task will be stopped. Re-enabling the robot will restart the
 * task, not resume it from where it left off.
 */
void opcontrol() {
    chassis.calibrate();
    chassis.moveToPoint(10, 10, 20);

    while (true) {
        pros::Controller controller(pros::E_CONTROLLER_MASTER);
        // loop forever
        // while (!resp) {
        vector<vector<int>> array = read_from_pi();
        for (vector<int> row : array) {
            for (int i : row) {
                cout << i << " ";
            }
            cout << "\n";
        }
        pros::delay(25);
    }
}