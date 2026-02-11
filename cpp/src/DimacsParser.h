#ifndef DIMACSPARSER_H
#define DIMACSPARSER_H

#include "SATInstance.h"
#include <string>

class DimacsParser {
public:
  static SATInstance *parseCNFFile(const std::string &fileName);
};

#endif // DIMACSPARSER_H
