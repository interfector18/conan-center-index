#include <ctranslate2/types.h>
#include <iostream>

int main() {
    auto device = ctranslate2::Device::CPU;
    std::cout << "CTranslate2 test_package OK, device: "
              << static_cast<int>(device) << std::endl;
    return 0;
}
