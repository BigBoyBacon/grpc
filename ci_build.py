import os
import shutil
import sys
import subprocess
import argparse
import platform
import shlex


def run_command(command, shell_type=True):
    """执行命令并实时打印输出，严格检查返回码"""
    print(f"\n\033[1;34m执行命令:\033[0m \033[1;33m{command}\033[0m")
    
    # 在Windows上使用原生shell，在Linux上使用/bin/bash
    executable = None
    if platform.system() != "Windows" and shell_type:
        executable = "/bin/bash"
    
    # 使用二进制模式读取输出，避免编码问题
    process = subprocess.Popen(
        command,
        shell=shell_type,
        executable=executable,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    # 实时打印输出，处理编码问题
    encoding = 'utf-8' if platform.system() != "Windows" else 'gbk'
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            try:
                # 尝试使用系统默认编码
                print(output.decode(encoding).rstrip())
            except UnicodeDecodeError:
                # 如果默认编码失败，尝试utf-8并忽略错误
                print(output.decode('utf-8', errors='ignore').rstrip())
    
    return_code = process.poll()
    if return_code != 0:
        print(f"\n\033[1;31m错误: 命令执行失败 (返回码 {return_code})\033[0m")
        sys.exit(return_code)
    
    return return_code

def prompt_delete_build_dir(build_dir):
    """提示用户是否删除已存在的build目录"""
    print(f"\n\033[1;33m警告: 构建目录 '{build_dir}' 已存在\033[0m")
    response = input("是否删除现有构建目录并继续？(y/n): ").strip().lower()
    if response == 'y':
        print(f"删除目录: {build_dir}")
        try:
            if platform.system() == "Windows":
                # 使用更可靠的删除方式
                subprocess.run(f'rmdir /s /q "{build_dir}"', shell=True, check=True)
            else:
                shutil.rmtree(build_dir)
            return True
        except Exception as e:
            print(f"\033[1;31m删除目录失败: {str(e)}\033[0m")
            return False
    else:
        print("\n\033[1;31m构建已取消\033[0m")
        return False

def main():
    parser = argparse.ArgumentParser(description='Grpc跨平台构建脚本')
    parser.add_argument('--build-type', choices=['Release', 'Debug'], default='Release',
                        help='构建类型: Release 或 Debug (默认: Release)')
    args = parser.parse_args()

    build_type = args.build_type
    current_dir = os.getcwd()
    

    
    # 1. 检查并处理build目录
    build_dir = os.path.join(current_dir, "build_ci")
    if os.path.exists(build_dir):
        if not prompt_delete_build_dir(build_dir):
            sys.exit(0)
    
    # 创建build目录
    os.makedirs(build_dir, exist_ok=True)
    os.chdir(build_dir)
    
    try:
        
        # 2. CMake配置
        cmake_configure_cmd = [
            "cmake", "..",
            f"-DCMAKE_BUILD_TYPE={build_type}",
            f"-DgRPC_INSTALL=ON",
            f"-DgRPC_BUILD_TESTS=OFF",
            f"-DCMAKE_CXX_STANDARD=17",
            # linux下路径拼接
            # 已经配置安装路径
            # f"-DCMAKE_INSTALL_PREFIX={build_dir}\\install"
        ]
        run_command(cmake_configure_cmd, shell_type=False)
        
        
        # 3. 构建项目
        build_cmd = ["cmake", "--build", ".", "--config", build_type]
        run_command(build_cmd, shell_type=False)
        
        # 4. 安装项目
        install_cmd = ["cmake", "--install", ".", "--config", build_type]
        run_command(install_cmd, shell_type=False)
        
        print(f"\n\033[1;32m构建成功完成! \033[0m")
    
    except Exception as e:
        print(f"\n\033[1;31m构建过程出错: {str(e)}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()