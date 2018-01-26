#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pulp
import sys
import re
import os

def read_instance(filename):
    """
    Reads the LP Problem Instance for PSMC from a text file and returns objects
    required to construct the solver.
    [PARAMETERS]:
        filename (string): A .txt file of the instance
    [RETURNS]:
        E (dict): A Dictionary of Elements in the instance
        S (dict): A Dictionary of Sets in the instance. Each Entry is a list
                of the contents of the set itself.
        r (dict): A Dictionary of Covering Requirements of Each Element in E
        c (dict): A Dictionary of Cost associated with each set B in S
        num_E (int): Number of elements in E
        num_S (int): Number of elements in S
        P (int): Integer specifying minimum number of covered elements required
    """
    
    try:
        file = open(filename)
    except Exception as error:
        print(error)
        exit()
        
    # parsing enclosed in try block as an error would mean the file is not in
    # the correct format    
    try:
        instance = file.read().split('\n')
        file.close()
        
        # Parse line 1
        num_E, num_S, P = [int(i) for i in instance[0].split()]
        E = [i for i in range(1,num_E+1)]
        E = {key+1:value for key,value in enumerate(E)}
        
        # Parse line 2
        r = [int(i) for i in instance[1].split()]
        if len(r)!=num_E:
            raise ValueError
        
        # Parse line 3
        c = [int(i) for i in instance[2].split()]
        if len(c)!=num_S:
            raise ValueError
        
        # Parse rest
        S = {}
        for j,k in enumerate(range(3,len(instance))):
            S[j+1] = [int(i) for i in instance[k].split()]
            
        if len(S)!= num_S:
            raise ValueError
            
        c = dict(zip(S,c))
        r = dict(zip(E,r))
        
        return E,S,r,c,num_E,num_S,P
    
    except Exception as error:
        print("wrong format")
        exit()

def create_Instance(E,S,r,c,num_E,num_S,P):
    """
    Creates an instance of LP Minimization using the values returned by read_instance.
    [PARAMETERS]:
        All outputs returned by read_instance
    [RETURNS]:
        PSMC (pulp.LpProblem): A Model of PSMC with the currently read instance.
        x (dict): A Dictionary of Solution Set Inclusion.
        y (dict): A Dictionary of Satisifed Covering
    """
    # Create a model which needs to be minimized
    PSMC = pulp.LpProblem("Partial Set Multi Cover",pulp.LpMinimize)
    # Create a binary variable x which is 1 for a B in S' or 0 if not included
    x = pulp.LpVariable.dict("x_%d",S,lowBound=0,upBound=1,cat='Integer')
    # Create a binary variable y which is 1 if an element E is covered else 0
    y = pulp.LpVariable.dict("y_%d",E,lowBound=0,upBound=1,cat='Integer')
    # Create objective function
    PSMC += sum( [c[i] * x[i] for i in S])
    # Create 1st constraint. See equation (1)
    PSMC += sum([y[i] for i in E]) >= P
    # Create constraints for covering each elements. See equation (2)
    for i in E:
        PSMC += sum([x[j] for j in S if i in S[j]]) - y[i]*r[i] >=0
    
    return PSMC,x,y

def solve_instance(instance):
    """
    Solves The generated PSMC instance using the GLPK Solver.
    [PARAMETERS]:
        Ouput returned by create_instance
    [RETURNS]:
        nothing. Solving is in-place. The instance is directly modified.
    [NOTE]:
        Use options parameter in function call to adjust GLPK cmd params
        for help type glpsol --help in the command prompt/terminal
    """
    # Solves the instance using GLPK with a process limit of 10 minutes
    instance.solve(solver=pulp.solvers.GLPK_CMD(msg=1,options=['--tmlim','600']))
    #instance.solve()
    
def main():
    """
    Reads the instance file, calls the above functions to create and solve the
    LP minimization problem and writes the results to a text file.
    [COMMAND LINE INPUTS]:
        input_file : the filename for the instance text file.
    [OUTPUTS]:
        output_file : ta text file containing the solution
    """
    if (len(sys.argv)) != 2:
        raise ValueError("Incorrect Number of Arguments")
    input_file = sys.argv[1]
    if not input_file.endswith(".txt"):
        raise AssertionError("File is not a text file")
    
    # get number from instance i.e instance01.txt has number 01
    # this is necessary to create the appropriate output file    
    number = re.findall('\d+',input_file)[0]
    output_file = "solution"+str(number)+".txt"
    
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Read text file
    E,S,r,c,num_E,num_S,P = read_instance(input_file)
    # Generate instance
    PSMC,x,y = create_Instance(E,S,r,c,num_E,num_S,P)
    #Solve instance
    solve_instance(PSMC)
    # Create string to write to file
    cost = 0
    k = 0
    sets = []
    for i in x:
        if x[i].value() == 1:
            cost += c[i]
            k+=1
            sets.append(i)
    # write solution to file
    file = open(output_file,mode='x')
    lines = str(k)+" "+str(cost)+''.join([" %s" % i for i in sets])
    file.write(lines)
    file.close()
    

if __name__ == "__main__":
    main()
    
    
    
    