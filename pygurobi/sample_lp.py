from itertools import product
import math
import random

import gurobipy as gp


class Stand(object):
    """
    Represents a forest stand, that is, a contiguous 
    region where all land belonging sharves similar
    forest land use characteristics.
    """


    def __init__(self, id, initial_age, species, region):
        self.id = id
        self.initial_age = initial_age
        self.species = species
        self.region = region

    def __repr__(self):
        return "Stand(id={0}, age={1}, species={2}, region={3})".format(
            self.id, self.initial_age, self.species, self.region)


def schedule_test(v, k):
    """
    Test if a schedule is elgible as given by v and k.

    Find the first 1 in a schedule. Then check if the next 1 is
    at least k spaces away.

    Then make sure there's only zeroes after the last 1.
    """

    first = ""
    found_first = False
    second = ""
    found_second = False
    in_elg = False

    for a,i in enumerate(v):
        if not found_first and i == 1:
            first = a
            found_first = True

        if found_first and not found_second and i == 1 and a > first+k:
            second = a
            found_second = True
        elif found_first and not found_second and i == 1 and a > first:
            #print "exit 1:"
            #print found_first, ", ", i, ", ", first
            in_elg = True

        if found_first and found_second and i == 1 and a > second:
            #print "exit 2:"
            #print found_first, ", ", i, ", ", first, ", ", second
            in_elg = True

    return in_elg


def schedule_generator(k, n):
    """
    Generate every possible harvest schedule of length
    n with harvests at least k periods apart.
    """

    iterator = product(range(2), repeat=n)
    n -= 1
    index = 0
    vectors = []

    iterator = list(iterator)

    for i in iterator:
        in_elg = schedule_test(i, k)
        if not in_elg:
            vectors.append(i)

    return vectors


def logistic_func(x, k):
    """
    Return the value of the logistic function for
    variable x and steepness parameter k.
    
    Function multiplied by an adjuster to make it 
    better mimic a forest stand's volume grown over time.

    Logistic function has parameters L = 150 and x0 = 0.
    """
    
    f = (150 / (1 + math.exp(-k * (x - 0))))*(x/80.0)
    
    if f > 150:
        f = 150

    return f


def assign_schedules(stands, schedules, m):
    """
    Assign schedules to stands based on a minimum
    harvest age of 40.
    """
    x = {}

    for i in stands:
        added = False
        initial_age = stands[i].initial_age
        for a,j in enumerate(schedules):
            if initial_age >= 40:
                #x[i,a] = "x[{0},{1}]".format(i,a)
                x[i,a] = m.addVar(lb=0, name="x[{0},{1}]".format(i,a))
                added = True
            else:
                diff = int((40 - initial_age) / 10)
                in_elg = False
                
                for d in range(diff):

                    if d < 9 and j[d] == 1:
                        in_elg = True

                if not in_elg:
                    #x[i,a] = "x[{0},{1}]".format(i,a)
                    x[i,a] = m.addVar(lb=0, name="x[{0},{1}]".format(i,a))
                    added = True
        if not added:
            print "Not added: ", i
    m.update()
    return x


def add_gub_constraints(m, x_vars):
    """
    Add assignment problem (GUB) constraints
    for assigning schedules to stands.
    """

    gub = {}
    print len(x_vars)
    for x_var, x in x_vars.iteritems():
        # separate the stand number from the schedule and varaible name
        stand = x.varName.split(",")[0][2:]
        if stand in gub:
            gub[stand] += x
        else:
            gub[stand] = gp.LinExpr(x)
    print len(gub)

    for g in gub:
        # All stands have an area of 1
        m.addConstr(gub[g] == 1, "gub({})".format(g))
    
    m.update()


def get_age_schedule_table(schedules):
    """
    Generate a table of initial ages, schedule number,
    period number, and current age.
    """
    
    age_schedules = {}
    for i in range(0, 200, 10):
        age_schedules[i] = {}
        for a, schedule in enumerate(schedules):
            age = i
            sched_table = {}
            for b,s in enumerate(schedule):
                sched_table[b] = age
                if s == 1:
                    age = 0
                else:
                    age += 10
            
            age_schedules[i][a] = sched_table

    return age_schedules


def add_harvest_vars(m, x_vars, schedules, age_schedules, stands, yields):
    """
    Add variables that track the volume of timber harvested
    of each species, in each region, and each period.
    """

    harv_vars = {}
    for k in range(10):
        for r in ["south", "north"]:
            for y in ["sw", "hw"]:
                harv_vars[y, r, k] = m.addVar(lb=0, 
                    name="harv[{0},{1},{2}]".format(y, r, k))
    m.update()
    
    harv_x_vars = {}
    for k in range(10):
        harv_x_vars[k] = {"sw": {
                              "south": gp.LinExpr(),
                              "north": gp.LinExpr()},
                         "hw": {
                             "south": gp.LinExpr(),
                             "north": gp.LinExpr()}
        }
        for x in x_vars.values():
            stand_id = int(x.varName.split(",")[0][2:])
            schedule = int(x.VarName.split(",")[1][:-1])
            stand = stands[stand_id]
            initial_age = stand.initial_age

            harvest = schedules[schedule][k]

            if harvest:
                
                harv_x_vars[k]["sw"][stand.region] += \
                    yields["sw"][age_schedules[initial_age][schedule][k]]*x
                harv_x_vars[k]["hw"][stand.region] += \
                    yields["hw"][age_schedules[initial_age][schedule][k]]*x

    for period in harv_x_vars:
        for s in harv_x_vars[period]:
            for region in harv_x_vars[period][s]:
                # Constraint to define the tracking ahrvest variable
                m.addConstr(
                    harv_vars[s, region,period] == 
                    harv_x_vars[period][s][region], 
                    "harv({0},{1},{2})".format(s, region, period))
    m.update()

    return harv_vars


def add_age_constraints(m, x_vars, age_schedules, stands):
    """
    Add variables that track the area of the forest that's
    over 60 years of age in each region and period. Then
    add constraints saying that in each region,
    after period 5 at least 20% of the forest in each
    region should be older than 60 years.
    """

    areas = {"south": len([s for s in stands.values() 
                           if s.region == "south"]),
             "north": len([s for s in stands.values() 
                           if s.region == "north"])}

    age_vars = {}
    for k in range(5,10):
        for r in ["south", "north"]:
            age_vars[r, k] = m.addVar(lb=0, 
                                      name="age[{0},{1}]".format(r, k))
    m.update()

    age_x_vars = {}
    for k in range(5, 10):
        age_x_vars[k] = {"south": gp.LinExpr(),
                    "north": gp.LinExpr()}
        for x in x_vars.values():
            stand_id = int(x.varName.split(",")[0][2:])
            schedule = int(x.VarName.split(",")[1][:-1])
            stand = stands[stand_id]

            age = age_schedules[stand.initial_age][schedule][k]
            if age >= 60:
                age_x_vars[k][stand.region] += x

    for period in age_x_vars:
        for region in age_x_vars[period]:
            # Constraint to define the tracking variable
            m.addConstr(
                age_vars[region,period] == age_x_vars[period][region],
                "age({0},{1})".format(region, period))
            
            # Constrain the tracking variable
            m.addConstr(age_vars[region, period] >= 0.2*areas[region],
                        "env({0},{1})".format(region, period))


def create_stands(n):
    """
    Create n Stand objects.

    Stands have a maximium age of 90, 
    have a proportion of softwood to hardwood,
    and belong to either the north or south region.
    """
    stand_ids = range(n)
    
    # Age in 10 year periods
    stand_ages = dict([(s, int(round(random.gauss(40, 40))/10)*10) for s in stand_ids])

    # Percent softwood of stand
    stand_species = dict([(s, random.random()) for s in stand_ids])

    # Region a stand belongs to
    stand_region = dict([(s, random.choice(["south", "north"])) for s
                          in stand_ids])

    stands = {}

    for s in stand_ids:
        if stand_ages[s] >= 90:
            stand_ages[s] = 90
        if stand_ages[s] < 0:
            stand_ages[s] = 0
        stands[s] = Stand(stand_ids[s], stand_ages[s],
                          stand_species[s], stand_region[s])

    return stands


def create_sample_lp():
    """
    Using gurobi create a sample LP.
    """

    # Forest of 100 stands each assumed to be 1 ha in area
    stands = create_stands(100)

    # Minimum harvest age is 40 years, 10 year planning horizon
    schedules = schedule_generator(4, 10)

    # Track the age of each stand under each schedule
    age_schedules = get_age_schedule_table(schedules)

    # Yields depend only on age 
    yields = {"sw": 
              dict([(r, logistic_func(r, 0.05125)) 
                    for r in range(0, 200, 10)]),
              "hw":
              dict([(r, logistic_func(r, 0.025)) 
                    for r in range(0, 200, 10)])}
                        


    m = gp.Model("Forest LP")
    #m = ""
    
    # Create assignment problem (GUB) variables and constraints
    x_vars = assign_schedules(stands, schedules, m)
    gub = add_gub_constraints(m, x_vars)

    # Add age  constraints that say at least 20% of forest 60 years
    # or older in each region after period 5
    add_age_constraints(m, x_vars, age_schedules, stands)

    # Create variables to track the volume of each species
    # harvested in each region and each period
    harvest_vars = add_harvest_vars(m, x_vars, schedules, age_schedules, stands, yields)
    
    # Set the objective function to maximize harvest volume
    for h in harvest_vars.values():
        h.obj = 1.0
    m.update()

    return m

