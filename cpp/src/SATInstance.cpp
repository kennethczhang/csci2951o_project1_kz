#include "SATInstance.h"
#include <cmath>

SATInstance::SATInstance(int nVars, int nClauses)
    : numVars(nVars), numClauses(nClauses) {}

void SATInstance::addVariable(int literal) { vars.insert(abs(literal)); }

void SATInstance::addClause(const set<int> &clause) {
  clauses.push_back(clause);
}

ostream &operator<<(ostream &os, const SATInstance &instance) {
  os << "Number of variables: " << instance.numVars << endl;
  os << "Number of clauses: " << instance.numClauses << endl;

  os << "Variables: [";
  bool first = true;
  for (int v : instance.vars) {
    if (!first)
      os << ", ";
    os << v;
    first = false;
  }
  os << "]" << endl;

  for (size_t i = 0; i < instance.clauses.size(); ++i) {
    os << "Clause " << i << ": [";
    first = true;
    for (int lit : instance.clauses[i]) {
      if (!first)
        os << ", ";
      os << lit;
      first = false;
    }
    os << "]" << endl;
  }
  return os;
}
