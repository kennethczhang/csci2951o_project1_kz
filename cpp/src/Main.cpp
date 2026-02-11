#include "DimacsParser.h"
#include "SATInstance.h"
#include "Timer.h"
#include <iomanip>
#include <iostream>
#include <string>

std::string getFileName(const std::string &path) {
  size_t lastSlash = path.find_last_of("/\\");
  if (lastSlash != std::string::npos) {
    return path.substr(lastSlash + 1);
  }
  return path;
}

/**
 * Usage example: read a given cnf instance file to create
 * a simple sat instance object and print out its parameter fields.
 */
int main(int argc, char *argv[]) {
  if (argc < 2) {
    std::cout << "Usage: ./solver <cnf file>" << std::endl;
    return 1;
  }

  std::string input = argv[1];
  std::string filename = getFileName(input);

  Timer watch;
  watch.start();

  try {
    SATInstance *instance = DimacsParser::parseCNFFile(input);
    if (instance != nullptr) {
      std::cout << *instance;
      delete instance;
    }
  } catch (const std::exception &e) {
    std::cerr << e.what() << std::endl;
  }

  watch.stop();

  std::cout << "{\"Instance\": \"" << filename << "\", \"Time\": " << std::fixed
            << std::setprecision(2) << watch.getTime()
            << ", \"Result\": \"--\"}" << std::endl;

  return 0;
}
