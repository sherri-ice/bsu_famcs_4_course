cmake_minimum_required(VERSION 3.20)
project (lab_3)

set(CMAKE_CXX_STANDARD 17)

# Add MPI Package to Project
find_package(MPI REQUIRED)
include_directories(SYSTEM ${MPI_INCLUDE_PATH})
add_executable(lab_3 main.cpp)
# Add libraries for code completion and compiling
target_link_libraries(lab_3 PUBLIC MPI::MPI_CXX)