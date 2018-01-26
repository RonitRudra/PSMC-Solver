#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from solver import read_instance
import sys
import re
from collections import Counter

def read_solution(filename):
    """
    Reads the solution file generated by the solver.py.
    [PARAMETERS]:
        filename (string): A .txt file of the solution
    [RETURNS]:
        k (int): The number of sets in the solution (S')
        Cost (int): The total cost of the solution
        Sets (list): The index of sets included in the solution
    [NOTE]:
        Exits the program if k does not match len(Sets)
    """
    
    try:
        file = open(filename)
    except Exception as error:
        print(error)
        exit()
    
    instance = file.read().split(' ')
    file.close()
    k = int(instance[0])
    Cost = int(instance[1])
    Sets = [int(i) for i in instance[2:]]
    
    if k != len(Sets):
        print("wrong format")
        exit()
    
    return k,Cost,Sets

def verify_costs(Sol_Set,Sol_Costs,C_dict):
    """
    Verifies the cost of solution in solution__.txt with costs in instance__.txt
    [PARAMETERS]:
        Sol_Set (list): List of Indices of sets included in solution (S')
        Sol_Costs (int): Total cost of soultion
        C_dict (dict): A Dictionary of Cost associated with each set B in S
    [RETURNS]:
        A flag (bool) which is True if costs match otherwise False.
    """
    # Calculate actual cost of soultion set.
    cost = 0
    for i in Sol_Set:
        cost += C_dict[i]
    
#    try:
#        assert cost == Sol_Costs, "Costs do not match"
#        return True
#    except Exception as error:
#        print("incorrect cost")
#        return False
     
    # Check if calculated cost is equal to stated cost.
    if cost == Sol_Costs:
        return True
    else:
        return False

def verify_covering_requirement(Re,Sol_Set,S,P_thresh):
    """
    Verifies if the covering requirement constraint, see equation (2) of LP instance,
    is satisfied by the solution set S'.
    [PARAMETERS]:
        Re (dict): A Dictionary of Covering Requirements of Each Element in E
        Sol_Set (list): List of Indices of sets included in solution (S')
        S (dict): A Dictionary of Sets in the instance. Each Entry is a list
                of the contents of the set itself.
        P_thresh (int): Integer specifying minimum number of covered elements required
    [RETURNS]:
        A flag (bool) which is True if covering requirement is met otherwise False.
    """
    
    # A counter is used to count the number of times an element E appears in the
    # solution set
    cov = Counter()
    req=0
    for i in Sol_Set:
        cov.update(S[i])
        
    # Check appearances against the covering requirements
    for i in cov:
        if cov[i]>=Re[i]:
            req+=1
#    try:
#        assert req >= P_thresh, "Requirements Failed"
#        return True
#    except Exception as error:
#        print("infeasible")
#        return False
    
    # Check if minimum number of elements have been covered.
    if req >= P_thresh:
        return True
    else:
        return False
        
def verify_minimal(Re,Sol_Set,S,P_thresh):
    """
    Verifies if the Solution Set S' is minimal or not by removing a set from S'
    and checking whether the solution is feasible or not by calling the function
    verify_covering_requirement. A solution is deemed infeasible if removal of a
    set from S' still satisfies the covering requirement constraint.
    S' is minimal if removal of all sets one at a time fails the covering requirement.
    [PARAMETERS]:
        Re (dict): A Dictionary of Covering Requirements of Each Element in E
        Sol_Set (list): List of Indices of sets included in solution (S')
        S (dict): A Dictionary of Sets in the instance. Each Entry is a list
                of the contents of the set itself.
        P_thresh (int): Integer specifying minimum number of covered elements required
    [RETURNS]:
        A flag (bool) which is True if covering requirement is met otherwise False.
    """
    # Remove one set from S' at a time and check covering requirement
    # If covering requirement fails for all removals then S' is minimal
    for i in Sol_Set:
        changed = Sol_Set.copy()
        changed.remove(i)
        flag = verify_covering_requirement(Re,changed,S,P_thresh)
        if flag:
            return False
        else:
            continue
    
    return True
        
           
def main():
    """
    Reads the instance and solution files and calls the above functions to
    test the solution. Outputs are returned as print statements to the command line
    or terminal.
    [COMMAND LINE INPUTS]:
        input_file : the filename for the instance text file.
        output_file : the filename for the solution text file
    [COMMAND LINE OUTPUTS]:
        'wrong format': If any discrepancy in the text files themselves. This includes
                        incorrect numbering such as passing instance01.txt and
                        solution02.txt
        'incorrect cost': If the cost provided in solution does not match the
                        cost calculated from the instance.
        'infeasible': If the solution does not satisfy the minimum covering
                        requirement.
        'not minimal': If the solution is not minimal i.e removal of a set still
                    satisfies the constraints. Cost is not checked again in this
                    case as it would naturally be lower.
        'everything is correct!': If the solution is the optimal.
        
        
    """
    if len(sys.argv)!=3:
        raise ValueError("Incorrect Number of Arguments")
        
    input_file = sys.argv[1]
    if not input_file.endswith(".txt"):
        raise AssertionError("Instance File is not a text file")
        
    output_file = sys.argv[2]
    if not output_file.endswith(".txt"):
        raise AssertionError("Solution File is not a text file")
        
    number_inst = re.findall('\d+',input_file)[0]
    number_sol = re.findall('\d+',output_file)[0]
    
    try:
        assert number_inst==number_sol,'Files do not match'
    except Exception as error:
        print("wrong format")
        exit()
        
    E,S,r,c,num_E,num_S,P = read_instance(input_file)
    k,Costs,Sets = read_solution(output_file)
    
    # Now check costs, covering requirement and feasibility
    # Cost
    cost_flag = verify_costs(Sets,Costs,c)
    if not cost_flag:
        print("incorrect cost")
        return 0
    # Covering Requirement Constraint
    # Solution is only feasible if covering requirement is met
    covering_flag = verify_covering_requirement(r,Sets,S,P)
    if not covering_flag:
        print("infeasible")
        return 0
    # Minimal Check
    # Removal of any set from soultion would render it infeasible
    minimal_flag = verify_minimal(r,Sets,S,P)
    if not minimal_flag:
        print("not minimal")
        return 0
    if cost_flag and covering_flag and minimal_flag:
        print("everything is correct!")
        return 0
    
if __name__ == "__main__":
    main()
    
    