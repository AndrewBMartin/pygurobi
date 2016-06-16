"""
30 May 2016

A library of functions to analyze and modify Gurobi models.

"""
import csv
import json

import gurobipy as gp

#from compressed_model import compressedModel

# Assuming that constraints are of the form: 
# constraintName(index1,index2,...,indexN).
# Asuming that variables are of the form: 
# variableName[index1,index2,...,indexN] 
CON_BRACKET_L = "("
CON_BRACKET_R = ")"
VAR_BRACKET_L = "["
VAR_BRACKET_R = "]"

# Attributes of a Gurobi variable
VAR_ATTRS = ["LB", "UB", "Obj", "VType", "VarName", "X", "Xn", "RC",
             "BarX", "Start", "VarHintVal", "VarHintPri", "BranchPriority", 
             "VBasis", "PStart", "IISLB", "IISUB", "PWLObjCvx", 
             "SAObjLow", "SAObjUp", "SALBLow", "SALBUp", 
             "SAUBLow", "SAUBUp", "UnbdRay"]

# Attributes of a Gurobi constraint
CON_ATTRS = ["Sense", "RHS", "ConstrName", "Pi", "Slack",
             "CBasis", "DStart", "Lazy", "IISConstr", 
             "SARHSLow", "SARHSUp", "FarkasDual"]


def get_variable_attrs():
    """
    Return a list of variable attributes.
    
    Details of attributes found at the Gurobi
    website: 
    http://www.gurobi.com/documentation/6.5/refman/attributes.html
    """
    
    return VAR_ATTRS


def get_constraint_attrs()
    """
    Return a list of constraint attributes.
    
    Details of attributes found at the Gurobi
    website: 
    http://www.gurobi.com/documentation/6.5/refman/attributes.html
    """
    
    return CON_ATTRS

def list_constraints(model):
    """
    Print to screen the constraint sets in the model.
    Show the name of each constraint set along with the
    number of constraints in that set.

    A constraint set is composed of all constraints
    sharing the same string identifier before the indices:
        A[2,3,4] and A[1,2,3] are in the same constraint set, A;
        A[2,3,4] and B[2,3,4] are in constraint sets A and B, respectively
    """

    sets = {}
    constraints = model.getConstrs()
    
    # Assuming constraint set name separated from indicies by
    for c in constraints:
        name = c.constrName
        split_name = name.split(CON_BRACKET_L)
        set_name = split_name[0]

        if set_name not in sets:
            sets[set_name] = 1
        else:
            sets[set_name] += 1
    
    print "Constraint set, Number of constraints"
    print "\n".join(["{0}, {1}".format(name, number) for name, number
                            in sorted(sets.items())])


def list_variables(model):
    """
    Print to screen the variable sets in the model.
    Show the name of each variable set along with the
    number of variables in that set.

    A variable set is composed of all variables
    sharing the same string identifier before the indices:
        A[2,3,4] and A[1,2,3] are in the same variable set, A;
        A[2,3,4] and B[2,3,4] are in variable sets A and B, respectively
    """

    sets = {}
    variables = model.getVars()
    
    # Assuming constraint set name separated from indicies by
    for v in variables:
        name = v.varName
        split_name = name.split(VAR_BRACKET_L)
        set_name = split_name[0]

        if set_name not in sets:
            sets[set_name] = 1
        else:
            sets[set_name] += 1
    
    print "Variable set, Number of variables"
    print "\n".join(["{0}, {1}".format(name, number) for name, number
                            in sorted(sets.items())])


def get_variables_multiple(model, names_list, approx=False):
    """
    Return a list of variables from the model
    given by the names_list.
    """

    var_list = []
    for name in names_list:
        var_list.extend(get_variables(model, name, approx))
    
    return var_list


def get_variables(model, name="", approx=False):
    """
    Return a list of variables from the variable
    set given by name.
    Variables are checked by the variable set name. If
    approx is set to be true than check to see if
    each entry from names is "in" each variable set name
    otherwise, check using "==".

    If name not specified, then return a list of
    all model variables.
    """

    if not name:
        return model.getVars()

    if not approx:
        return [v for v in model.getVars() 
                if v.varName.split(VAR_BRACKET_L)[0] == name]
    else:
        return [v for v in model.getVars()
                if name in v.varName.split(VAR_BRACKET_L)[0]]


def get_variable_attr(attr, model="", name="", variables=""):
    """
    Return a dictionary of variables names for the given
    varaible set mapped to
    attribute values for the specified attribute.

    Can take a model object along with the variable set name, 
    or a list of variables as input.
    """

    if not attr:
        print "Error: No attributes specified"
        return
    
    # Make a list of attributes at the top and check against
    # them to make sure that the specified attribute belongs.

    if not model and not variables:
        print "Error: No model or variable list given"
        return 

    variables = variables_check(name, model, variables)

    return {v.varName: getattr(v, attr) for v in variables}


def print_variable_attr(attr, model="", name="", variables=""):
    """
    Print to screen a list of variable attribute values
    given by the variables specified in the names parameter.
    
    If a model is given then first get the variables from
    the model and then print the specified attributes.

    If a list of variables is given then print the 
    attributes of the variables to screen.

    If names not specified then return atttributes for all 
    variables.

    If attrs not specified return nothing. Same applies if
    neither model nor variables is given.
    """

    var_dict = get_variable_attr(attr, model=model,
                                 name=name, variables=variables)


    print "\n".join(["{0}, {1}".format(v, k) for v, k in 
                    sorted(var_dict.items())])


def print_variable_objective_coeffs(model="", name="", variables=""):
    """
    Print to screen a list of variable coefficients given
    by variables specified in the names parameter.

    If a model is given then first get the variables from
    the model and then print the coefficients.

    If a list of variables is given then print the 
    coefficients of the variables to screen.
    """
    print_variable_attr("Obj", model=model, 
                        name=name, variables=variables)


def print_variable_X(model="", name="", variables=""):
    """
    Print to screen a list of variable solution values given
    by variables specified in the names parameter.

    If a model is given then first get the variables from
    the model and then print the X values.

    If a list of variables is given then print the 
    X values of the variables to screen.
    """
    print_variable_attr("X", model=model, 
                        name=name, variables=variables)


def set_variable_objective_coeffs(val=1.0, name="", model="", variables=""):
    """
    Set the objective coefficients for the variables given
    by names.

    Can take either a model or a list of variables to set the
    objective coefficients of.

    Default value is 1.0 use the val kwarg to specify otherwise.

    Model is not updated in the function.
    """

    set_variable_attr("Obj", val=val, model=model, 
                      name=name, variables=variables)



def zero_all_objective_coeffs(model):
    """
    Set all objective coefficients in a model to zero.
    """

    if not model:
        print "Error: no model given"
        return

    for v in model.getVars():
        v.Obj = 0


def set_variable_bounds(lb="", ub="", model="", name="", variables=""):
    """
    Set the lower bound and/or upper bound for a set(s) of 
    variables.

    All variables will receive the same bounds.
    """

    if lb:
        set_variable_attr("lb", val=lb, model=model, 
                          name=name, variables=variables)

    if ub:
        set_variable_attr("ub", val=ub, model=model, 
                          name=name, variables=variables)


def set_variable_bounds_from_dict(bounds_dict, model="", 
                                  name="", variables=""):
    """
    Set the lower bound and/or upper bound for a set(s) of 
    variables from a dictionary specifying by variable
    the bounds to give it.
    """

    # 31 May 2016 - this is complicated, maybe don't jump on
    # it right away.
    pass


def remove_variables_from_model(model="", name="", variables=""):
    """
    Remove the variables given by names or the variables list
    from the model.

    Model update not performed after variable removal.
    """

    if not model and not variables:
        print "Error: no model or variables given"
        return
    if not model:
        print "Error: no model given"
        return

    variables = variables_check(name, model, variables)

    for v in variables:
        model.remove(v)


def set_variable_attr(attr, val, model="", name="", variables=""):
    """

    """
    if not attr or not val:
        print "Error: No attribute or value specified"
        return

    if not model and not variables:
        print "Error: No model or variables specified"
        return
    
    variables = variables_check(name, model, variables)

    for v in variables:
        setattr(v, attr, val)


def variables_check(name, model, variables):
    """
    Return the appropriate
    variables based on the information supplied.
    """

    if variables:
        return variables

    if model and name:
        variables = get_variables(model, name)
    if model and not name:
        variables = model.getVars()
    
    if not variables:
        print "No variables found for\nmodel: {0},\nname: {1}".format(
               model, name)

    return variables
    
    
def get_index_value(variable, index):
    """
    Return the value of the given index
    for a given variable.

    Variable names are assumed to be given
    as A[a,c,d, ....,f]
    """

    value = variable.varName.split(",")[index].strip()
    if "]" in value:
        value = value[:-1]
    elif "[" in value:
        value = value.split("[")[1]

    return value


def get_linexp_from_variables(variables):
    """
    Return a linear expression from the supplied list
    of variables.
    """
    
    linexp = gp.LinExpr()
    for v in variables:
        linexp += v

    return linexp

  


def sum_variables_by_index(index, model="", name="", variables=""):
    """
    Return a dictionary having keys of index names
    for the given variable index and values the sum
    of the solution values of all variables containing
    that index.
    """

    var_dict = get_variables_by_index(index, model=model, name=name,
                                      variables=variables)
    if not var_dict:
        print "Error: problem with inputs"
        return

    new_dict = {index_name: sum([v.X for v in index_vars])
                for index_name, index_vars in 
                sorted(var_dict.items())}

    return new_dict


def print_variable_dict(var_dict):
    """
    Print a variable dictionary to screen.
    """

    print "\n".join(["{0}, {1}".format(index_name, index_value)
                     for index_name, index_value in 
                     sorted(var_dict.items())])
                     
                     
def print_variables_sum_by_index(index, model="", name="", variables=""):
    """
    Print a dictionary of variables, summed by index.
    """
    
    var_dict = sum_variables_by_index(index, model=model,
                                         name=name, variables=variables)
    print_variable_dict(var_dict)


def get_variables_by_index(index, model="", name="", variables=""):
    """
    Return a dictionary of variables with keys
    of the specified index and values a list of
    variables having that index.
    """

    if not index:
        print "Error: no index given"
        return
    if not model and not variables:
        print "Error: no model or variables given"
        return
    
    if not (name and model) and not variables:
        print "Error: please specify the variables you want to print"
        return

    variables = variables_check(name, model, variables)

    var_dict = {}

    for v in variables:

        value = get_index_value(v, index)
        if value not in var_dict:
            var_dict[value] = [v]
        else:
            var_dict[value].append(v)

    return var_dict


def filter_variables_by_index_value(variables, index_values, exclude=False):
    """
    Return a filtered list of variables.
    index_values dictionary provides index numbers as keys
    and a list of index values as values.
    If exlude is False then return variables that match the filters.
    If exclude is True than return variables that do not match the filters.
    """

    if not variables:
        print "Error: variables not given"
        return
    if not index_values:
        print "Error: dictionary of index_values not given"
        return

    # If the index array separater is not "]" make the change here
    sep = "]"

    new_vars = []
    for index, value in index_values.iteritems():
        for v in variables:
            name = get_index_value(v, index)
            if value == name:
                new_vars.append(v)

    if not exclude:
        return new_vars
    else:
        # May want to adding sorting by varName here
        return [v for v in (set(variables)-set(new_vars))]
        
        
def get_variables_by_index_values(model, name, index_values, exclude=False):
    """
    Return a list of variables filtered by index values.
    
    If exlude is False then return variables that match the filters.
    If exclude is True than return variables that do not match the filters.
    """
    
    variables = get_variables(model, name)
    
    filtered_variables = filter_variables_by_index_value(
        variables, index_values, exclude)
    
    return filtered_variables


def get_linexp_by_index(index, model="", name="", variables=""):
    """
    Return a dictionary of index value and variables
    corresponding to that index value summed as a linear
    expression.
    """

    linexps = {}

    variables = variables_check(name, model, variables)

    for v in variables:

        value = get_index_value(v, index)
        
        if value not in linexps:
            linexps[value] = gp.LinExpr(v)
        else:
            linexps[value] += v
    
    return linexps
    

def get_constraints_multiple(model, names_list, approx=False):
    """
    Return a list of constraints given by the constraint
    set names in names_list.
    """
    
    cons_list = []
    for name in names_list:
        cons_list.extend(get_constraints(model, name, approx))

    return cons_list


def get_constraints(model, name="", approx=False):
    """
    Return a list of constraints from the model
    given by name of the constraint set.
    Constraints are checked by the constraint set name. If
    approx is set to be true than check to see if
    each entry from names is "in" each constraint set name
    otherwise, check using "==".

    If names not specified, then return a list of
    all model constraints.
    """

    if not name:
        return model.getConstrs()

    if not approx:
        return [c for c in model.getConstrs() 
                if c.constrName.split(CON_BRACKET_L)[0] == name]
    else:
        return [c for c in model.getConstrs()
                if name in c.constrName.split(CON_BRACKET_L)[0]]


def constraints_check(name, model, constraints):
    """
    Check to see whether the user specified a list 
    of constraints or expects them to be retrieved
    from the model.
    """
    
    if constraints:
        return constraints

    if model and name:
        constraints = get_constraints(model, name)
    elif model and not name:
        constraints = model.getConstrs()

    return constraints


def get_constraints_attr(attr, model="", name="", constraints=""):
    """
    Return a dictionary of constraint names and their
    corresponding attribute, specified by the attribute
    parameter.
    """

    if not attr:
        print "Error: No attributes specified"
        return

    # Check if the attr supplied is not a viable model attribute
    if not model and not constraints:
        print "Error: No model or constraint list given"
        return 

    constraints = constraints_check(name, model, constraints)

    return {c.constrName: getattr(c, attr) for c in constraints}


def print_constraints_attr(attr, model="", name="", constraints=""):
    """
    Print to screen a list of constraint attribute values
    given by the constraints specified in the names parameter.
    
    If a model is given then first get the constraints from
    the model and then print the specified attributes.

    If a list of constraints is given then print the 
    attributes of the constraints to screen.

    If names not specified then return atttributes for all 
    constraints.

    If attrs not specified return nothing. Same applies if
    neither model nor constraints is given.
    """

    constraints = get_constraints_attr(attr, model=model,
                                      name=name, constraints=constraints)

    print "\n".join(["{0}, {1}".format(c, k) 
                     for c, k in sorted(constraints.items())])


def print_constraint_slacks(model="", name="", constraints=""):
    """
    Print to screen a list of constraint slack values
    given by the constraints specified in the names parameter.
    
    If a model is given then first get the constraints from
    the model and then print the slacks.

    If a list of constraints is given then print the 
    slacks of the constraints to screen.

    If names not specified then return slacks for all 
    constraints.
    """

    print_constraint_attr("Slack", model=model,
                          name=name, constraints=constraints)


def print_constraint_duals(model="", name="", constraints=""):
    """
    Print to screen a list of constraint dual values
    given by the constraints specified in the names parameter.
    
    If a model is given then first get the constraints from
    the model and then print the duals.

    If a list of constraints is given then print the 
    duals of the constraints to screen.

    If names not specified then return duals for all 
    constraints.
    """

    print_constraint_attr("Pi", model=model,
                          name=name, constraints=constraints)


def set_constraint_attr(attr, val, model="", name="", constraints=""):
    """
    Set an attribute o a
    """

    if not attr or not val:
        print "Error: No attribute or value specified"
        return

    if not model and not constraints:
        print "Error: No model or constraints specified"
        return
    
    constraints = constraints_check(name, model, constraints)

    for c in constraints:
        setattr(c, attr, val)


def set_constraint_sense(val, model="", name="", constraints=""):
    """
    Set the constraint sense for a set of constraints.
    Must be either ">", "<", or "=".
    """

    if val not in ["<", ">", "="]:
        print "Error: value specified is not '<', '>', or '='"
        return

    set_constraint_attr("Sense", val, model=model,
                        name=name, constraints=constraints)


def set_constraint_rhs(val, model="", name="", constraints=""):
    """
    Set the right hand side value of a set of constraints.
    """

    set_constraint_attr("RHS", val, model=model, 
                        name=name, constraints=constraints)


def remove_constraints_from_model(model, name="", constraints=""):
    """
    Remove the specified constraints from the model.
    """

    # This is needed for the case where a list of 
    # constraints is provided because a model object 
    # must be provided
    if not constraints:
        constraints = constraints_check(name, model, constraints)

    for c in constraints:
        model.remove(c)


def get_grb_sense_from_string(sense):
    """
    Return the GRB constraint sense object
    corresponding to the supplied string.
    """

    if sense == "<":
        return gp.GRB.LESS_EQUAL
    elif sense == ">":
        return gp.GRB.GREATER_EQUAL
    elif sense == "=":
        return gp.GRB.EQUAL
    else:
        print "Error: constraint sense is not '<', '>', '='"
        return


def add_sum_constraint_constant(model, constant, sense="<", 
                                name="", variables="", con_name=""):
    """Add constraint to model that says the sum of 
    variables must equal a constant."""

    if not variables:
        variables = variables_check(name, model, variables)

    linexp = get_linexp_from_variables(variables)

    sense = get_grb_sense_from_string(sense)

    if not sense:
        return

    if not con_name:
        model.addConstr(linexp, sense, constant)
    else:
        model.addConstr(linexp, sense, constant, con_name)


def check_if_name_a_variable(name, model):
    """
    Check if the supplied name corresponds to
    a variable set name in the given model.
    """

    variables = get_variables(model, name)

    if not variables:
        return False

    return True


def check_if_name_a_constraint(name, model):
    """
    Check if the supplied name corresopnd to
    a cosntraint set name in the given model.
    """

    constraints = get_constraints(model, name)

    if not constraints:
        return False

    return True


def add_sum_constraint_variables(model, variables1, variables2, 
                                 sense="=", con_name=""):
    """Add constraint to model that says the sum of
    variables1 must equal the sum of variables2."""

    if not variables1 or not variables2:
        print "Error: variables list not provided"
        return

    linexp1 = get_linexp_from_variables(variables1)
    linexp2 = get_linexp_from_variables(variables2)

    sense = get_grb_sense_from_string(sense)

    if not sense:
        print "Error: please provide '<', '>', or '=' for constraint sense."
        return

    if not con_name:
        model.addConstr(linexp1, sense, linexp2)
    else:
        model.addConstr(linexp1, sense, linexp2, con_name)


def graph_by_index(model, variables, index, title="", y_axis="", x_axis=""):
    """
    Display a graph of the variable against the specified index
    using matplotlib. 

    Matplotlib must already be installed to use this.
    
    Crucially, the variable must be in the form x[a,b]
    where x is any identifier name and one of the indice
    sets a, or b, represent time period.
    """
    try:
        import matplotlib.pyplot as plot
    except ImportError:
        print "Error: Module Matplotlib not found."
        print "Please download and install Matplotlib to use this function."
        return
        
    fig = plot.figure()
    ax = fig.add_subplot(111)

    variables_sum = sum_variables_by_index(index, variables=variables)

    keys, values = zip(*variables_sum.items())

    y = range(len(variables_sum))
    
    if title:
        ax.set_title(title)
    if y_axis:
        ax.set_ylabel(y_axis)
    if x_axis:
        ax.set_xlabel(x_axis)
    ax.bar(y, values)
    #ax.legend(keys)

    plot.show()


def print_variables_to_csv(file_name, model="", name="",
                           variables="", headers=""):
    """
    Print the specified variables to a csv file
    given by the file_name parameter.

    If no variables specified than all model
    variables written.
    """

    if ".csv" not in file_name:
        print "Error: non csv file specified"
        return

    with open(file_name, "wb+") as write_file:
        writer = csv.writer(write_file)
        if headers:
            headers = headers.split(",")
            writer.writerow(headers)

        variables = variables_check(name, model, variables) 

        writer.writerows([ [v.varName, v.X] for v in variables])


def print_variables_to_csv_by_index(file_name, index, 
                                    model="", name="", variables="",
                                    headers=""):
    """
    Print the sums of variables by the specified index
    to a csv file.

    Default behaviour of the function is to overwrite
    the given file_name.
    """

    if ".csv" not in file_name:
        print "Error: non csv file specified"
        return

    with open(file_name, "wb+") as write_file:
        writer = csv.writer(write_file)

        if headers:
            headers = headers.split(",")
            writer.writerow(headers)

        variables_dict = sum_variables_by_index(index, model=model,
                                            name=name, variables=variables)

        if not variables_dict:
            print "Error: please specify the variables you want to print"
            return
        print "writing"

        writer.writerows([ [key, value] 
                        for key, value in sorted(variables_dict.items())])


def print_variables_to_json_by_index(file_name, index, model="",
                                    name="", variables="", index_alias=""):
    """
    Print the specified variables to a json file given by file_name
    organized by the specified index.

    Formatted for reading into nvD3 applications.

    If file_name does not contain json extension then it will
    be added.

    Default behaviour is to overwrite file if one exists in
    file_name's location.
    """

    if ".json" not in file_name:
        print "Error: non json file specified"
        return
        
    index_name = index
    if index_alias:
        index_name = index_alias

    var_dict = sum_variables_by_index(index, model=model, 
                                      name=name, variables=variables)

    data = {index_name: [{ index_name: var_dict }] }

    json.dump(data, open(file_name, "wb"))


def tune_model(name, model, timelimit=7200):
    """
    Tune a model.
    Write out the resulting parameter settings
    as .prm file with name given by name paramter.

    If model not supplied then read in the model
    using the name parameter.

    Timelimit defaults to 7200 seconds
    """
    if not model:
        print "Error: no model supplied"
        return

    if not name:
        print "Error: no name for the parameter file supplied"
        return 

    model.setParam('TuneTimeLimit', timelimit)
    model.tune()
    for i in range(model.tuneResultCount):
        model.getTuneResult(i)
        model.write("{0}_{1}.prm".format(name, str(i)))


def compress_model(model):
    """
    Remove everything except variable
    and constraint objects from a model.

    Warning: optimization and updates can no longer 
    be performed after a model has been
    compressed.

    Compression cannot be undone.

    All non modifying functions in this library
    will still work on a compressed model.
    """
    model = compressedModel(model)

    return model


def optimize_write_model(basis_name, model="", model_name="",):
    """
    Optimize a model and if solution is optimal
    write a basis file using model_name.
    """

    if ".bas" not in basis_name:
        print "Error: basis file name not specified"
        return

    if model:
        model.optimize()
    elif model_name:
        try:
            model = gp.read(model_name)
            model.optimize()
        except Exception, e:
            raise
    else:
        print "Error: neither model nor model_name given"
        return

    if model.status == gp.GRB.status.OPTIMAL:
        model.write(basis_name)
    else:
        print "Model status: ", model.status

