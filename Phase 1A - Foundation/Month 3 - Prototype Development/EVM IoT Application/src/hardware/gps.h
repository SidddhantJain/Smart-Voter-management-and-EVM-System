// GPS Driver Header (C++)
#pragma once
#include <string>

class GPS {
public:
    bool initialize();
    std::string getLocation();
};
