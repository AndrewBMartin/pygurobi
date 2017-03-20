"""
15 July 2016

A library of functions to analyze and modify Gurobi models.

"""
import csv
import json

import gurobipy as gp


# Assuming that constraints are of the form: 
# constraintName(index1,index2,...,indexN).
# Asuming that variables are of the form: 
# variableName[index1,index2,...,indexN] 
CON_BRACKET_L = "("
CON_BRACKET_R = ")"
VAR_BRACKET_L = "["
VAR_BRACKET_R = "]"


# 13 July 2016 - Need to sort out capitalization here for attributes

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


def read_model(filename):
    """
    Read a model using gurobipy.
    """

    m = gp.read(filename)
    
    return m
    
    
def reoptimize(m):
    """
    Update, reset, and optimize
    a model.
    """
    
    m.update()
    m.reset()
    m.optimize()


def get_variable_attrs():
    """
    Return a list of variable attributes.
    
    Details of attributes found at the Gurobi
    website: 
    http://www.gurobi.com/documentation/6.5/refman/attributes.html
    """
    
    return VAR_ATTRS


def get_constraint_attrs():
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
        A(2,3,4) and A(1,2,3) are in the same constraint set, A;
        A(2,3,4) and B(2,3,4) are in constraint sets A and B, respectively
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


def get_variables(model, name="", approx=False, filter_values={}, exclude=False):
    """
    Return a list of variables from the variable
    set given by name.
    Variables are checked by the variable set name. If
    approx is set to be true than check to see if
    each entry from names is "in" each variable set name
    otherwise, check using "==".

    If filter_values specified as a dicitonary of index to value to filter 
    for. Exclude means when filtering return variables that match the index
    or return values that do not match the index.

    If name not specified, then return a list of
    all model variables.
    """

    if not name:
        return model.getVars()
    
    variables = []
    if not approx:
        variables = [v for v in model.getVars() 
                if v.varName.split(VAR_BRACKET_L)[0] == name]
    else:
        variables = [v for v in model.getVars()
                if name in v.varName.split(VAR_BRACKET_L)[0]]

    if filter_values:
        variables = filter_variables(filter_values, variables=variables, 
                exclude=exclude)

    return variables


def check_attr(attr, attributes):
    """
    Check if the attr string is contained in a list of athe attr string is contained 
    in a list of attributes.

    The check is case-insensitive.
    """
    for a in attributes:

        if attr == a:
            return True
        if attr.lower() == a.lower():
            return True

    return False


def check_variable_attr(attr):
    """
    Check if a string corresponds to a variable attribute.

    Case-insensitive.
    """

    var_attrs = get_variable_attrs()

    return check_attr(attr, var_attrs)


def check_constraint_attr(attr):
    """
    Check if a string corresponds to a variable attribute.

    Attributes are case-insensitive.
    """

    con_attrs = get_constraint_attrs()

    return check_attr(attr, con_attrs)


def get_variables_attr(attr, model="", name="", variables=""):
    """
    Return a dictionary of variables names for the given
    varaible set mapped to
    attribute values for the specified attribute.

    Can take a model object along with the variable set name, 
    or a list of variables as input.
    """

    if not attr:
        raise AttributeError("No attributes specified")
    
    if not check_variable_attr(attr):
        raise AttributeError("{0}\n{1}\n{2}".format(
        "Attribute: {0} not a variable attribute.".format(attr),
        "Get list of all variables attributes with the",
        "get_variable_attrs() method.")
    
    # Make a list of attributes at the top and check against
    # them to make sure that the specified attribute belongs.

    if not model and not variables:
        raise ValueError("No model or variable list given")

    variables = variables_check(model, name, variables)

    return {v.varName: getattr(v, attr) for v in variables}


def print_variables_attr(attr, model="", name="", variables=""):
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

    var_dict = get_variables_attr(attr, model=model,
                                 name=name, variables=variables)


    print "\n".join(["{0}, {1}".format(v, k) for v, k in 
                    sorted(var_dict.items())])


def set_variables_attr(attr, val, model="", name="", variables=""):
    """
    Set the attribute of a variable.

    """
    if not attr or not val:
        raise AttributeError("No attribute or value specified")
        return
    
    if not check_variable_attr(attr):
        raise AttributeError("{0}\n{1}\n{2}".format(
        "Attribute: {0} not a variable attribute.".format(attr),
        "Get list of all variables attributes with the",
        "get_variable_attrs() method.")

    if not model and not variables:
        raise ValueError("No model or variables specified")
    
    variables = variables_check(model, name, variables)

    for v in variables:
        setattr(v, attr, val)


def zero_all_objective_coeffs(model):
    """
    Set all objective coefficients in a model to zero.
    """

    if not model:
        raise ValueError("No model given")
    
    for v in model.getVars():
        v.Obj = 0


def set_variables_bounds(lb="", ub="", model="", name="", variables=""):
    """
    Set the lower bound and/or upper bound for a set(s) of 
    variables.

    All variables will receive the same bounds.
    """

    if lb:
        set_variables_attr("lb", val=lb, model=model, 
                          name=name, variables=variables)

    if ub:
        set_variables_attr("ub", val=ub, model=model, 
                          name=name, variables=variables)


def remove_variables_from_model(model, name="", variables=""):
    """
    Remove the variables given by names or the variables list
    from the model.

    Model update not performed after variable removal.
    """

    if not model and not variables:
        raise ValueError("No model or variables given")

    if not model:
        raise ValueError("No model given")

    variables = variables_check(model, name, variables)

    for v in variables:
        model.remove(v)


def variables_check(model, name, variables):
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
    
    
def get_variable_index_value(variable, index):
    """
    Return the value of the given index
    for a given variable.

    Variable names are assumed to be given
    as A[a,c,d, ....,f]
    """

    value = variable.varName.split(",")[index].strip()
    if VAR_BRACKET_R in value:
        value = value[:-1]
    elif VAR_BRACKET_L in value:
        value = value.split(VAR_BRACKET_L)[1]
    
    # Not expecting many variable index values to
    # to be floats
    if value.isdigit:
        try: 
            value = int(value)
        except ValueError:
            pass
            
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
        raise ValueError("No variables found".format(index))

    new_dict = {index_name: sum([v.X for v in index_vars])
                for index_name, index_vars in 
                sorted(var_dict.items())}

    return new_dict


def print_dict(dictionary):
    """
    Print a dictionary to screen.
    """

    print "\n".join(["{0}, {1}".format(index_name, index_value)
                     for index_name, index_value in 
                     sorted(dictionary.items())])
                     
                     
def print_variables_sum_by_index(index, model="", name="", variables=""):
    """
    Print a dictionary of variables, summed by index.
    """
    
    var_dict = sum_variables_by_index(index, model=model,
                                         name=name, variables=variables)
    print_dict(var_dict)


def get_variables_by_index(index, model="", name="", variables=""):
    """
    Return a dictionary of variables with keys
    of the specified index and values a list of
    variables having that index.
    """

    if index != 0 and not index:
        raise IndexError("No index given")
    
    if not model and not variables:
        raise ValueError("No model or variables given")
    
    if not (name and model) and not variables:
        raise ValueError("No variables specified")

    variables = variables_check(model, name, variables)

    var_dict = {}

    for v in variables:

        value = get_variable_index_value(v, index)
        if value not in var_dict:
            var_dict[value] = [v]
        else:
            var_dict[value].append(v)

    return var_dict


def filter_variables(variables, filter_values, exclude=False):
    """
    Return a filtered list of variables.
    index_values dictionary provides index numbers as keys
    and a list of index values as values.
    If exlude is False then return variables that match the filters.
    If exclude is True than return variables that do not match the filters.
    """

    if not variables:
        raise ValueError("variables not given")
    
    if not filter_values:
        raise ValueError("Dictionary of filter values not given")

    new_vars = []
    for v in variables:
        add = True
        for index, value in filter_values.iteritems():
            key = pg.get_variable_index_value(v, index)
            if key != value:
                add = False
                break
        if add:
            new_vars.append(v)

    if not exclude:
        return new_vars
    else:
        # May want to add sorting by varName here
        return [v for v in (set(variables)-set(new_vars))]
        




def get_variables_by_index_values(index_values, model="", name="", exclude=False):
    """
    Return a list of variables filtered by index values.
    
    If exlude is False then return variables that match the filters.
    If exclude is True than return variables that do not match the filters.
    """

    
    if not variables:
        variables = pg.get_variables(model, name)

    new_vars = []
    for v in variables:
        add = True
        for index, value in index_values.iteritems():
            key = pg.get_variable_index_value(v, index)
            if key != value:
                add = False
                break
        if add:
            new_vars.append(v)

    return new_vars
        
def get_variables_by_index_values(model, name, index_values, exclude=False):
    
    variables = get_variables(model, name)
    
    filtered_variables = filter_variables_by_index_value(
        variables, index_values, exclude)
    
    return filtered_variables
    
    
def get_variables_by_two_indices(index1, index2, model="", name="", variables=""):
    """
    Return a dictionary having keys of index1 names for the given
    variables and the given variables and values dictionaries
    of the given variable by index2.
    """
    
    two_indices_dict = {}
    index1_dict = get_variables_by_index(index1, model=model, name=name,
                                      variables=variables)
    for key, value in index1_dict.iteritems():
        two_indices_dict[key] = get_variables_by_index(index2, variables=value)
        
    return two_indices_dict
    
    
def sum_variables_by_two_indices(index1, index2, model="", name="", variables=""):
    """
    Return a dictionary having keys of index1 names
    for the given variable  and values dictionaries
    of the given variables summed over index2.
    """

    two_indices_dict = get_variables_by_two_indices(index1, index2,
                                        model=model, name=name, variables=variables)
    if not two_indices_dict:
        raise ValueError("Inputs did not match with model variables")
        
    new_dict = {}
    for key, var_dict in two_indices_dict.iteritems():
        new_dict[key] = {index_name: sum([v.X for v in index_vars])
                for index_name, index_vars in 
                sorted(var_dict.items())}

    return new_dict
 
 
def print_two_indices_dict(indices_dict):
    """
    Print to screen a nested dictionary of 
    two indices.
    """
    
    for key, value in indices_dict.iteritems():
        print "\n{0}".format(key)
        print_dict(value)


def get_linexp_by_index(index, model="", name="", variables=""):
    """
    Return a dictionary of index value and linear expressions
    corresponding to that index value summed as a linear
    expression.
    """

    linexps = {}

    variables = variables_check(model, name, variables)

    for v in variables:

        value = get_variable_index_value(v, index)
        
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
        raise AttributeError("No attributes specified")
        
    if not check_constraint_attr(attr):
        raise AttributeError("{0}\n{1}\n{2}".format(
        "Attribute: {0} not a constraint attribute.".format(attr),
        "Get list of all variables attributes with the",
        "get_constraint_attrs() method.")

    # Check if the attr supplied is not a viable model attribute
    if not model and not constraints:
        raise ValueError("No model or constraint list given")

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


def set_constraints_attr(attr, val, model="", name="", constraints=""):
    """
    Set an attribute of a model constraint.
    """

    if not attr or not val:
        raise AttributeError("No attribute or value specified")
    
    if not check_constraint_attr(attr):
        raise AttributeError("{0}\n{1}\n{2}".format(
        "Attribute: {0} not a variable attribute.".format(attr),
        "Get list of all variables attributes with the",
        "get_variable_attrs() method.")

    if not model and not constraints:
        raise ValueError("No model or constraints specified")
    
    constraints = constraints_check(name, model, constraints)

    for c in constraints:
        setattr(c, attr, val)


def set_constraints_rhs_as_percent(percent, model="", name="", constraints=""):
    """
    Set the rhs of a constraint set as a percent of its current rhs.
    """

    if percent != 0 and not percent:
        print "Error: No percent specified."
        return

    try:
        percent = float(percent)
    except ValueError:
        raise ValueError("Percent must be a number. Percent: {}".format(percent))

    if not model and not constraints:
        raise ValueError("No model or constraints specified.")

    constraints = constraints_check(name, model, constraints)

    for c in constraints:
        cur_rhs = getattr(c, "rhs")
        setattr(c, "rhs", percent*cur_rhs)


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

        
def get_constraint_index_value(constraint, index):
    """
    Return the value of the given index
    for a given constraint.

    Constraint names are assumed to be given
    as A(a,c,d, ....,f)
    """

    value = constraint.constrName.split(",")[index].strip()
    if CON_BRACKET_R in value:
        value = value[:-1]
    elif CON_BRACKET_L in value:
        value = value.split(CON_BRACKET_L)[1]
        
    # Not expecting many constraint index values to
    # to be floats
    if value.isdigit:
        try: 
            value = int(value)
        except ValueError:
            pass

    return value


def get_constraints_by_index(index, model="", name="", constraints=""):
    """
    Return a dictionary of constraints with keys
    of the specified index and values a list of
    constraints having that index.
    """

    if not index:
        raise IndexError("No index given")

    if not model and not constraints:
        raise ValueError("No model or constraints given")
    
    if not (name and model) and not constraints:
        raise ValueError("No constraints specified")

    constraints = constraints_check(name, model, constraints)

    con_dict = {}

    for c in constraints:

        value = get_constraint_index_value(c, index)
        if value not in con_dict:
            con_dict[value] = [c]
        else:
            con_dict[value].append(c)

    return con_dict


def filter_constraints_by_index_value(constraints, index_values, exclude=False):
    """
    Return a filtered list of constraints.
    index_values dictionary provides index numbers as keys
    and a list of index values as values.
    If exlude is False then return constraints that match the filters.
    If exclude is True than return constraints that do not match the filters.
    """

    if not constraints:
        raise ValueError("Variables not given")
        
    if not index_values:
        raise ValueError("Dictionary of index_values not given")

    new_cons = []
    for index, value in index_values.iteritems():
        for c in constraints:
            name = get_constraint_index_value(c, index)
            if value == name:
                new_cons.append(c)

    if not exclude:
        return new_cons
    else:
        # May want to add sorting by varName here
        return [v for v in (set(constraints)-set(new_cons))]
        
        
def get_constraints_by_index_values(model, name, index_values, exclude=False):
    """
    Return a list of constraints filtered by index values.
    
    If exlude is False then return constraints that match the filters.
    If exclude is True than return constraints that do not match the filters.
    """
    
    constraints = get_constraints(model, name)
    
    filtered_constraints = filter_constraints_by_index_value(
        constraints, index_values, exclude)
    
    return filtered_constraints


def get_grb_sense_from_string(sense):
    """
    Return the GRB constraint sense object
    corresponding to the supplied string.
    
    Convention follows the Gurobi docs:
    https://www.gurobi.com/documentation/6.5/refman/sense.html#attr:Sense
    """

    if sense == "<":
        return gp.GRB.LESS_EQUAL
    elif sense == ">":
        return gp.GRB.GREATER_EQUAL
    elif sense == "=":
        return gp.GRB.EQUAL
    else:
        raise ValueError("Constraint sense is not '<', '>', '='")


def add_constraint_constant(model, variables, constant, sense="<", 
                                      con_name=""):
    """
    Add constraint to model that says the sum of 
    variables must be =, <, or , > a constant.
    """
    
    if not variables:
        raise ValueError("variables list not provided")
    
    linexp = get_linexp_from_variables(variables)

    sense = get_grb_sense_from_string(sense)

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
    a constraint set name in the given model.
    """

    constraints = get_constraints(model, name)

    if not constraints:
        return False

    return True


def add_constraint_variables(model, variables1, variables2, 
                                 sense="=", con_name=""):
    """
    Add constraint to model that says the sum of
    variables1 must be =, < , > the sum of variables2.
    """

    if not variables1 or not variables2:
        ValueError("Variables list not provided")

    linexp1 = get_linexp_from_variables(variables1)
    linexp2 = get_linexp_from_variables(variables2)

    sense = get_grb_sense_from_string(sense)

    if not con_name:
        model.addConstr(linexp1, sense, linexp2)
    else:
        model.addConstr(linexp1, sense, linexp2, con_name)

        
def graph_by_index(model, variables, index, title="", y_axis="", x_axis=""):
    """
    Display a graph of the variable against the specified index
    using matplotlib. 

    Matplotlib must already be installed to use this.
    See: http://matplotlib.org/faq/installing_faq.html
    """
    try:
        import matplotlib.pyplot as plot
    except ImportError:
        raise ImportError("{0}\n{1}".format(
        "Module Matplotlib not found.",
        "Please download and install Matplotlib to use this function.")
        
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
    
 
def graph_by_two_indices(model, variables, index1, index2, title="",
                                 y_axis="", x_axis=""):
    """
    Display a graph of the variable summed over index2
    given by index1.
    
    Matplotlib must already be installed to use this.
    See: http://matplotlib.org/faq/installing_faq.html
    """
    try:
        import matplotlib.pyplot as plot
    except ImportError:
        raise ImportError("{0}\n{1}".format(
        "Module Matplotlib not found.",
        "Please download and install Matplotlib to use this function.")
    
    fig = plot.figure()
    ax = fig.add_subplot(111)
    
    # We need to do this in reverse order to prepare it for graphing
    variables_sum = sum_variables_by_two_indices(index2, index1, 
                                       variables=variables)

    keys, values = zip(*variables_sum.items())
    
    colours = ["b", "g", "r", "c", "y", "m", "k", "w"]


    y = range(len(values[0]))
    print y
    
    if title:
        ax.set_title(title)
    if y_axis:
        ax.set_ylabel(y_axis)
    if x_axis:
        ax.set_xlabel(x_axis)
    bars = []
    
    prev_bars = [0 for bar in y]
    colour_count = 0
    for key, value in variables_sum.iteritems():
        cur_bars = [k[1] for k in sorted(value.items(), key=lambda x: x[0])]
        bars.append(ax.bar(y, cur_bars, bottom=prev_bars, 
                                color=colours[colour_count]))
        prev_bars = cur_bars
        colour_count += 1
        if colour_count == len(colours) - 1:
            colour_count = 0
    ax.legend(keys)

    plot.show()
                         

def print_variables_to_csv(file_name, model="", name="", variables=""):
    """
    Print the specified variables to a csv file
    given by the file_name parameter.

    If no variables specified than all model
    variables written.
    """

    if ".csv" not in file_name:
        raise ValueError("Non csv file specified")

    with open(file_name, "wb+") as write_file:
        writer = csv.writer(write_file)

        headers = ["Variable name", "Value"]
        writer.writerow(headers)

        variables = variables_check(model, name, variables) 
        
        # This will put quotes around strings, because the variable
        # names have commas in them.
        writer.writerows([ [v.varName, v.X] for v in variables])


def print_variables_to_csv_by_index(file_name, index, 
                                    model="", name="", variables=""):
    """
    Print the sums of variables by the specified index
    to a csv file.

    Default behaviour of the function is to overwrite
    the given file_name.
    """

    if ".csv" not in file_name:
        raise ValueError("Non csv file specified")

    with open(file_name, "wb+") as write_file:
        writer = csv.writer(write_file)

        headers = ["Index", "Value"]
        writer.writerow(headers)

        variables_dict = sum_variables_by_index(index, model=model,
                                            name=name, variables=variables)

        if not variables_dict:
            raise ValueError("No variables found")

        writer.writerows([ [key, value] 
                        for key, value in sorted(variables_dict.items())])


def print_variables_to_json_by_index(file_name, index, model="",
                                    name="", variables="", index_alias=""):
    """
    Print the specified variables to a json file given by file_name
    organized by the specified index.

    Formatted for reading into nvD3 applications.

    Default behaviour is to overwrite file if one exists in
    file_name's location.
    """

    if ".json" not in file_name:
        raise ValueError("Non json file specified")
        
    index_name = index
    if index_alias:
        index_name = index_alias

    var_dict = sum_variables_by_index(index, model=model, 
                                      name=name, variables=variables)

    data = {index_name: [{ index_name: var_dict }] }

    json.dump(data, open(file_name, "wb"))

