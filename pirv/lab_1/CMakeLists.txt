cmake_minimum_required(VERSION 3.10)

project(MyProject)

# Set C++ standard to 17
set(CMAKE_CXX_STANDARD 17)
# Enable the use of OpenMP
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp -m64")
# Make C++17 a required standard
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include the Google Test package
find_package(GTest REQUIRED)

# Add your source files (main.cpp) and executable here
add_executable(Matrix main.cpp src/matrix.h src/matrix.cpp src/timer.h src/timer.cpp)

# Add your test source files and test executable here
add_executable(Test src/matrix.h src/matrix.cpp src/timer.h src/timer.cpp tests/test_dummy.cpp tests/test_multiply.cpp)

# Link your test executable with Google Test
target_link_libraries(Test GTest::GTest GTest::Main)
