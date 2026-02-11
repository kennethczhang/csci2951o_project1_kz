#ifndef SATINSTANCE_H
#define SATINSTANCE_H

#include <iostream>
#include <set>
#include <string>
#include <vector>

using namespace std;

class SATInstance {
public:
  int numVars;
  int numClauses;
  set<int> vars;
  vector<set<int>> clauses;

  SATInstance(int numVars, int numClauses);
  void addVariable(int literal);
  void addClause(const set<int> &clause);

  friend ostream &operator<<(ostream &os, const SATInstance &instance);
};

#endif // SATINSTANCE_H
