cmake_minimum_required(VERSION 3.15)
project(fasttext VERSION 0.9.2 LANGUAGES CXX)

include(GNUInstallDirs)

option(FASTTEXT_BUILD_CLI "Build fasttext command-line tool" OFF)

set(FASTTEXT_HEADERS
    src/args.h
    src/autotune.h
    src/densematrix.h
    src/dictionary.h
    src/fasttext.h
    src/loss.h
    src/matrix.h
    src/meter.h
    src/model.h
    src/productquantizer.h
    src/quantmatrix.h
    src/real.h
    src/utils.h
    src/vector.h)

set(FASTTEXT_SOURCES
    src/args.cc
    src/autotune.cc
    src/densematrix.cc
    src/dictionary.cc
    src/fasttext.cc
    src/loss.cc
    src/matrix.cc
    src/meter.cc
    src/model.cc
    src/productquantizer.cc
    src/quantmatrix.cc
    src/utils.cc
    src/vector.cc)

add_library(fasttext ${FASTTEXT_SOURCES} ${FASTTEXT_HEADERS})
target_compile_features(fasttext PUBLIC cxx_std_17)
target_include_directories(fasttext
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

find_package(Threads REQUIRED)
target_link_libraries(fasttext PUBLIC Threads::Threads)

set_target_properties(fasttext PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR})

if(MSVC)
    target_compile_definitions(fasttext PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

if(FASTTEXT_BUILD_CLI)
    add_executable(fasttext-bin src/main.cc)
    target_link_libraries(fasttext-bin PRIVATE fasttext)
    set_target_properties(fasttext-bin PROPERTIES OUTPUT_NAME fasttext)
    install(TARGETS fasttext-bin RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()

install(TARGETS fasttext
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(FILES ${FASTTEXT_HEADERS}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/fasttext)
