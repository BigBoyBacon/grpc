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
# cmake build file for C++ helloworld example.
# Assumes protobuf and gRPC have been installed using cmake.
# See cmake_externalproject/CMakeLists.txt for all-in-one cmake build
# that automatically builds all the dependencies before building helloworld.

cmake_minimum_required(VERSION 3.16)

project(HelloWorld C CXX)

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

# Proto file
get_filename_component(hw_proto "../../protos/helloworld.proto" ABSOLUTE)
get_filename_component(hw_proto_path "${hw_proto}" PATH)

# Generated sources
set(hw_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.pb.cc")
set(hw_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.pb.h")
set(hw_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.grpc.pb.cc")
set(hw_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.grpc.pb.h")
add_custom_command(
      OUTPUT "${hw_proto_srcs}" "${hw_proto_hdrs}" "${hw_grpc_srcs}" "${hw_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${hw_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${hw_proto}"
      DEPENDS "${hw_proto}")

# Include generated *.pb.h files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

# hw_grpc_proto
add_library(hw_grpc_proto
  ${hw_grpc_srcs}
  ${hw_grpc_hdrs}
  ${hw_proto_srcs}
  ${hw_proto_hdrs})
target_link_libraries(hw_grpc_proto
  absl::check
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

# Targets greeter_[async_](client|server)
foreach(_target
  greeter_client greeter_server
  greeter_callback_client greeter_callback_server
  greeter_async_client greeter_async_client2 greeter_async_server)
  add_executable(${_target} "${_target}.cc")
  target_link_libraries(${_target}
    hw_grpc_proto
    absl::check
    absl::flags
    absl::flags_parse
    absl::log
    absl::log_initialize
    ${_REFLECTION}
    ${_GRPC_GRPCPP}
    ${_PROTOBUF_LIBPROTOBUF})
endforeach()
