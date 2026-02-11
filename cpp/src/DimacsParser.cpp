#include "DimacsParser.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>

SATInstance *DimacsParser::parseCNFFile(const std::string &fileName) {
  std::ifstream infile(fileName);
  if (!infile.is_open()) {
    throw std::runtime_error("Error: DIMACS file is not found " + fileName);
  }

  std::string line;
  std::string token;

  // Skip comments until the problem line is found
  while (std::getline(infile, line)) {
    if (line.empty())
      continue;
    std::stringstream ss(line);
    ss >> token;
    if (token != "c") {
      // Found the first non-comment line, which must be the problem line
      break;
    }
  }

  // Parse problem line: "p cnf <numVars> <numClauses>"
  std::stringstream problemLine(line);
  problemLine >> token;

  if (token != "p") {
    throw std::runtime_error(
        "Error: DIMACS file does not have problem line (found " + token + ")");
  }

  std::string format;
  problemLine >> format;
  if (format != "cnf") {
    std::cout << "Error: DIMACS file format is not cnf" << std::endl;
    return nullptr;
  }

  int numVars, numClauses;
  problemLine >> numVars >> numClauses;

  SATInstance *instance = new SATInstance(numVars, numClauses);

  // Parse clauses body
  std::set<int> currentClause;

  while (infile >> token) {
    // Check if the token indicates a comment start
    if (token == "c") {
      std::getline(infile, line); // Skip the rest of the comment line
      continue;
    }
    // Check for end of file marker
    if (token == "%")
      break;

    try {
      int literal = std::stoi(token);
      if (literal == 0) {
        // End of the current clause
        instance->addClause(currentClause);
        currentClause.clear();
      } else {
        // Add literal to the current clause
        currentClause.insert(literal);
        instance->addVariable(literal);
      }
    } catch (...) {
      // If parsing fails (e.g. non-integer), continue to next token
    }
  }

  return instance;
}
