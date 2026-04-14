# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/project/build/_deps/picotool-src"
  "/project/build/_deps/picotool-build"
  "/project/build/_deps"
  "/project/build/picotool/tmp"
  "/project/build/picotool/src/picotoolBuild-stamp"
  "/project/build/picotool/src"
  "/project/build/picotool/src/picotoolBuild-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/project/build/picotool/src/picotoolBuild-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/project/build/picotool/src/picotoolBuild-stamp${cfgdir}") # cfgdir has leading slash
endif()
