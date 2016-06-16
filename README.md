# PyGurobi
### Rapid interactive Gurobi model modification and analysis

 * Quickly visualize the results of modelling
 * Powerful variable and constraint querying
 * Create linear expressions and new constraints on the fly



PyGurobi extends the Gurobi Python API.  It's a library of helper functions that comes out of almost 5 years experience with the Gurobi Python API. These functions accelerate modelling with Gurobi because they allow you to perform deeper analysis interactively while writing less interpreter code.


An example will illustrate its usage.

I'll demonstrate with a simplified forest management LP. Find it in the root directory as forest.lp. 

forest.lp is a harvest scheduling model where we want to find the optimal assignment of harvest schedules to cut-blocks. Our forest management model will run for 10 periods where each period represents 10 years. 

The objective is to **maximize the total volume of timber harvested**.

The variables are: 

* **x[i,j]** - the number of hectares of cut-block, i, to be managed under schedule j, where j is a schedule of harvests. Each cut-block, i, belongs to a region, r, has both hardwood and softwood timber, and an initial age.

* **harv[r,s,t]** - the volume of timber harvested from cut-blocks in region, r, of species s (softwood or hardwood), in period t. 

* **age[r,t]** - the area of the forest that is at least 60 years old in region, r, and period, t.

The constraints are:

* **gub(i)** - assignment problem GUB constraints that say no more than the area of each cut-block can be assigned to harvest schdules.
* **age(r, t)** - at least 20% of the forest in each region has to be age 60 or greater after period 5.

Code to generate this model can be found in LINK.

We'll talk about the index of a variable often in the following demonstration. 

To demonstrate how to use PyGurobi, we're going to optimize the model. View some data about it, then modify a constraint, and finally add a new constraint. Some familiarity with the Gurobi Python API is assumed.

```python
>>> import gurobipy as gp # Gurobi Python API
>>> import pygurobi as pg # PyGurobi
>>> m = gp.read("forest.lp")
>>> m.optimize()
```
We find that we have an optimal objective of ...

Now, let's review what the model contains
```python
>>> pg.list_variables(m)
Variable set, Number of variables
x, 1963
harv, 40
age, 20

# Now constraints
>>> pg.list_constraints(m)
Constraint set, Number of constraints
gub, 100
age, 20
```
What are the actual periodic harvest levels?

```python
# "X" is the Gurobi variable attribute that tells use
>>> pg.print_variables_attr("X", model=m, name="harv")
...
```
Well, that's too messy. Let's try a different way. Recall that for the **harv[r,s,t]** variables, index 0 is r, region, index 1 is s, species, and index 2 (or -1, a.k.a. last index) is t, period.

```python
# The first argument references the index we want to sum variables by. 
# In this case this is the periods index which for the harvest variables is
# the last index. In python -1 can be used to access the last index.
>>> periodic_harvest = pg.sum_variables_by_index(-1, model=m, name="harv")
>>> pg.print_dict(periodic_harvest)
...
```

That's much nicer. Notice how I passed `pg.sum_variables_by_index` a model object and the name of a set of variables. This syntax allows me to access variables without managing them in the interpreter. There are however use cases where it's preferable to pass a list of variables to be summed. PyGurobi offers syntax for this as well.


```python
# Print periodic softwood harvest volume.

# We pass the following function a dictionary that has index numbers as keys,
# and index values to filter by as values. Here {0: "sw"} says only return variables
# that have value "sw" (softwood) in index 0.
>>> softwood_harvest = pg.get_variables_by_index_values(m, "harv", {0: "sw"})
>>> periodic_softwood_harvest = pg.sum_varaibles_by_index(-1, variables=softwood_harvest)
>>> pg.print_dict(periodic_softwood_harvest)
...
```

We can also pop up a simple graph using Matplotlib (installed separately).

```python
# Display a graph of periodic harvest levels.
>>> harvest = pg.get_variables(m, "harv")
>>> pg.graph_by_index(m, harvest, -1, title="Periodic Volume", y_axis="Cubic Meters", x_axis="Period")
...
```
And this pops up:

IMAGE OF GRAPH

We can also play with constraints. For instance, if we want to change the right hand side of the age constraints so that we have at least 20 ha of forest over 60 years old in each region.

```python
>>> pg.set_constraint_attr("rhs", 20, model=m, name="age")
>>> m.update() # Updates aren't done in PyGurobi functions - just like the Python Gurobi API
>>> m.reset()
>>> m.optimize()
...
```

Not surprisingly, we see the objective value decrease because the model has to cut less wood to satisfy the new age constraint.

Look at those harvest volumes though, they're all over the place. In some periods cutting X and in others cutting 0. We'd like to smooth out those harvests so that in each period we're cutting the same amount of volume.

```python
>>> # We're going to add this constraint period by period, saying the harvest volume in 
>>> # period n has to equal the harvest volume in period n +1
>>> for n in range(9):
>>>     # Get harvest variables from period n
>>>     variables1 = pg.get_variables_by_index_values(m, "harv", {-1: str(n)})
>>>     # Get harvest variables from period n+1
>>>     variables2 = pg.get_variables_by_index_values(m, "harv", {-1: str(n+1)})
>>>     pg.add_sum_constraint_variables(m, variables1, variables2, sense="=", con_name="even")
```

So now we've added a set of constraints that say in each period, the volume harvested must equal the volume harvested in the next period. 

The results say...
```python
>>> harvest = pg.get_variables(m, "harv")
>>> pg.graph_by_index(m, harvest, -1, title="Periodic Volume", y_axis="Cubic Meters", x_axis="Period")
...
```

And before wrapping up, we can look at the results by region, and by species
```python
>>> # By region
>>> pg.graph_by_two_indices(m, harvest, -1, 1, title="Periodic Volume by Region", y_axis="Cubic Meters", x_axis="Period")
...
>>>  # By species
>>>  pg.graph_by_two_indices(m, harvest, -1, 0, title="Periodic Volume by Region", y_axis="Cubic Meters", x_axis="Period")
...
```
This is [on GitHub](https://github.com/jbt/markdown-editor) so let me know if I've b0rked it somewhere.


