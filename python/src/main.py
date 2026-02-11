import json
from pathlib import Path
from argparse import ArgumentParser
from dimacs_parser import DimacsParser
from model_timer import Timer
from sat_instance import SATInstance

def unit_propagation(instance):
    ''' Returns: instance, result, solution'''
    solution = dict()

    # Initial set of unit literals
    unit_literals = set()
    for clause in instance.clauses:
        if len(clause) == 1: 
            unit_literals.add(next(iter(clause)))
    
    # Remove clauses until no more unit literals are found
    while unit_literals:
        literal = unit_literals.pop()
        # Assign the literal to True and simplify the instance
        # Remove clauses satisfied by this literal
        instance.clauses = [clause for clause in instance.clauses if literal not in clause]
        # Remove the negation of the literal from remaining clauses
        for clause in instance.clauses:
            if -literal in clause:
                clause.remove(-literal)
                # Check 0 and 1 case
                if len(clause) == 0:
                    # If we have an empty clause, the instance is unsatisfiable
                    return None, "UNSAT", None
                elif len(clause) == 1:
                    # If we have a new unit clause, add it to the set of unit literals
                    unit_literals.add(next(iter(clause)))

        solution[abs(literal)] = literal > 0

        instance.vars.remove(abs(literal))
        instance.numClauses = len(instance.clauses)
        instance.numVars = len(instance.vars) # should be just -1 from before

    return instance, None, solution


def pure_literal_elimination(instance):
    ''' Returns: instance, result, solution'''
    solution = dict()

    cur_literals = set.union(*instance.clauses) if instance.clauses else set()
    one_polarity_literals = {lit for lit in cur_literals if -lit not in cur_literals}
    while one_polarity_literals:
        literal = one_polarity_literals.pop()
        # Assign the literal to True and remove clauses satisfied by this literal
        instance.clauses = [clause for clause in instance.clauses if literal not in clause]
        instance.vars.remove(abs(literal)) 
        instance.numClauses = len(instance.clauses)
        instance.numVars = len(instance.vars) # should be just -1 from before

        solution[abs(literal)] = literal > 0

        if not one_polarity_literals:
            # Recompute the set of literals and one-polarity literals after simplification
            cur_literals = set.union(*instance.clauses) if instance.clauses else set()
            one_polarity_literals = {lit for lit in cur_literals if -lit not in cur_literals}

    return instance, None, solution
    

def reduce_with_literal(instance, literal):
    ''' Assume var is removed from instance.vars by caller'''
    ''' Doesn't mutate instance, returns a copy'''
    ''' Returns: instance, result, solution'''

    # Copy vars and drop the assigned variable
    new_vars = set(instance.vars)
    new_vars.discard(abs(literal))

    # Deep-copy clauses (copy each set!)
    new_clauses = []
    for clause in instance.clauses:
        if literal in clause:
            # clause satisfied -> drop it
            continue

        new_clause = set(clause)  # copy
        new_clause.discard(-literal)

        if len(new_clause) == 0:
            return None, "UNSAT", None

        new_clauses.append(new_clause)

    new_instance = SATInstance(
        numVars=len(new_vars),
        numClauses=len(new_clauses),
        vars=new_vars,
        clauses=new_clauses,
    )

    return new_instance, None, {abs(literal): literal > 0}


def sat_solver(instance):
    solution = dict()
    if len(instance.clauses) == 0:
        return "SAT", solution

    # Run UP and PLE while possible
    while True: 
        instance, result, up_solution = unit_propagation(instance)
        if result == "UNSAT":
            return "UNSAT", None
        solution.update(up_solution)
        if len(instance.clauses) == 0:
            return "SAT", solution
        
        # if up_solution:
            # print("After UP:" + str(up_solution))
            # print("Remaining instance: " + str(instance))

        instance, result, ple_solution = pure_literal_elimination(instance)
        solution.update(ple_solution)
        if len(instance.clauses) == 0:
            return "SAT", solution
        
        # if ple_solution:
            # print("After PLE:" + str(ple_solution))
            # print("Remaining instance: " + str(instance))
        
        if not up_solution and not ple_solution:
            break
        # print(up_solution)
        # print(ple_solution)
        

    # Search for a variable to assign and backtrack if necessary
    
    orig_instance = instance
    var = instance.vars.pop()
    # print(f"Trying variable: {var}")
    # print(instance)
    
    # Try positive
    instance, result, _ = reduce_with_literal(orig_instance, var)
    # print(f"After assigning {var}: positive")

    if result != "UNSAT":
        var_p_result, var_p_solution = sat_solver(instance)
        if var_p_result == "SAT":
            solution[var] = True
            solution.update(var_p_solution)
            return "SAT", solution
        
    # If no sol, try negative
    instance, result, _ = reduce_with_literal(orig_instance, -var)
    # print(f"After assigning {var}: negative")
    # print(instance)

    if result != "UNSAT":
        var_n_result, var_n_solution = sat_solver(instance)
        if var_n_result == "SAT":
            solution[var] = False
            solution.update(var_n_solution)
            return "SAT", solution

    return "UNSAT", None

def main(args):
    input_file = args.input_file
    
    if not input_file:
        print("Usage: python3 src/main.py <cnf file>")
        return

    path = Path(input_file)
    filename = path.name
    
    timer = Timer()
    timer.start()
    
    try:
        instance = DimacsParser.parse_cnf_file(input_file)
        if instance:
            print(instance, end="")
    except Exception as e:
        print(f"Error: {e}")

    # TODO: call your solver here and get the result
    result, solution = sat_solver(instance)
    
    timer.stop()
    
    printSol = {
        "Instance": filename,
        "Time": f"{timer.getTime():.2f}",
        "Result": result,
        "Solution": solution,
    }
    
    print(json.dumps(printSol))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()
    main(args)
