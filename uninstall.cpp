#include <iostream>
#include <cstdio>

int main() {
    const char* filePath = "launcher.exe";  
    
   
    if (remove(filePath) == 0) {
        std::cout << "文件删除成功: " << filePath << std::endl;
    } else {
        std::cerr << "文件删除失败: " << filePath << std::endl;
    }

    return 0;
}
