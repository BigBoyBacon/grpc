# Copyright 2018 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# cmake build file for C++ route_guide example.
# Assumes protobuf and gRPC have been installed using cmake.
# See cmake_externalproject/CMakeLists.txt for all-in-one cmake build
# that automatically builds all the dependencies before building route_guide.

cmake_minimum_required(VERSION 3.16)

project(RouteGuide C CXX)


# 宏定义：获取向上N层后进入指定目录的路径
# 参数：
#   input_path: 起始路径
#   up_levels: 向上层数
#   sub_dir: 目标子目录（如"x/y/z"）
#   output_var: 输出变量名
macro(get_relative_path input_path up_levels sub_dir output_var)
    set(temp_path "${input_path}")
    # 向上N层
    foreach(_ RANGE ${up_levels})
        get_filename_component(temp_path "${temp_path}" DIRECTORY)
    endforeach()
    # 拼接子目录
    get_filename_component(${output_var} "${temp_path}/${sub_dir}" ABSOLUTE)
endmacro()

# 使用示例
get_relative_path(${CMAKE_CURRENT_SOURCE_DIR} 4 "3dParty/install/grpc" grpc_path)
message("目标路径: ${grpc_path}")

# 获取当前CMakeLists.txt所在目录的上两级目录
# get_filename_component(PARENT_DIR ${CMAKE_CURRENT_LIST_DIR} DIRECTORY)
# get_filename_component(GRANDPARENT_DIR ${PARENT_DIR} DIRECTORY)
# 设置 CMake 查找路径
# set(CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH} "G:\\zpg\\gitContent\\z-bacon\\3dParty\\install\\grpc")
set(CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH} ${grpc_path})


include(../cmake/common.cmake)

# Find absl package
find_package(absl CONFIG REQUIRED)

# Proto file
get_filename_component(rg_proto "../../protos/route_guide.proto" ABSOLUTE)
get_filename_component(rg_proto_path "${rg_proto}" PATH)

# Generated sources
set(rg_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/route_guide.pb.cc")
set(rg_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/route_guide.pb.h")
set(rg_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/route_guide.grpc.pb.cc")
set(rg_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/route_guide.grpc.pb.h")
add_custom_command(
      OUTPUT "${rg_proto_srcs}" "${rg_proto_hdrs}" "${rg_grpc_srcs}" "${rg_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${rg_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${rg_proto}"
      DEPENDS "${rg_proto}")

# Include generated *.pb.h files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

# rg_grpc_proto
add_library(rg_grpc_proto
  ${rg_grpc_srcs}
  ${rg_grpc_hdrs}
  ${rg_proto_srcs}
  ${rg_proto_hdrs})
target_link_libraries(rg_grpc_proto
  absl::absl_log
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

# route_guide_helper
add_library(route_guide_helper
  "helper.h"
  "helper.cc")
target_link_libraries(route_guide_helper
  rg_grpc_proto
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

# Targets route_guide_(client|server)
foreach(_target
  route_guide_client route_guide_server
  route_guide_callback_client route_guide_callback_server)
  add_executable(${_target}
    "${_target}.cc")
  target_link_libraries(${_target}
    rg_grpc_proto
    route_guide_helper
    absl::flags_parse
    absl::absl_log
    absl::log_initialize
    absl::log_globals
    ${_REFLECTION}
    ${_GRPC_GRPCPP}
    ${_PROTOBUF_LIBPROTOBUF})
endforeach()
