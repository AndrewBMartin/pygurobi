# PyGurobi
### Rapid interactive Gurobi model modification and analysis

 * Quickly visualize the results of modelling
 * Powerful variable and constraint querying
 * Create linear expressions and new constraints on the fly



PyGurobi extends the already awesome [Gurobi Python API](https://www.gurobi.com/documentation/6.5/quickstart_mac/the_gurobi_python_interfac.html). It's a Python library that comes out of almost 5 years experience working with the Gurobi Python API. These functions accelerate modelling with Gurobi because they allow you to perform deeper analysis interactively while writing less interpreter code. 

I'm not associated with the Gurobi company, just a user and admirer of their product.

**Requirements**: Python 2.7+, a working [Gurobi](http://gurobi.com) license, [gurobipy](https://www.gurobi.com/documentation/6.5/quickstart_mac/the_gurobi_python_interfac.html) installed, optional (for graphing only) [Matplotlib](http://matplotlib.org/).

**Install**: `pip install pygurobi` or download this repo and run `python setup.py install`

An important note before starting, PyGurobi by default assumes that *variable names* are separated from indices by square brackets "[" and "]", and that *constraint names* are separated from indices by round brackets "(" and ")". For example, variables look like **x[i,j]** and constraints look like **env(r,t)**. If this is not your convention then you can modify PyGurobi to use your bracketing convetion by accessing the source code. You can find the location of the PyGurobi source code using the `inspect.getfile()` command:
```python
>>> import inspect
>>> import pygurobi
>>> inspect.getfile(pygurobi)
'/Users/admin/app/env/lib/python2.7/site-packages/pygurobi/__init__.pyc' 
>>> # Your path will be different but should still have "/pygurobi/__init__.py" at the end.
```
If you've installed PyGurobi, then when you issue `inspect.getfile(pygurobi)` you'll see the path to the PyGurobi folder with the same ending as the one shown above. Open this folder and then open the [pygurobi.py](https://github.com/AndrewBMartin/pygurobi/blob/master/pygurobi/pygurobi.py) file in a texteditor. Change the `CON_BRACKET_L`, `CON_BRACKET_R`, `VAR_BRACKET_L` and `VAR_BRACKET_R` global variables to the constraint and variable brackets that you use, and you'll be set to go.

#### Example Model

I'll demonstrate how to use PyGurobi with a simple forest management Linear Programming model. Find it in the root directory as [forest.lp](https://github.com/AndrewBMartin/pygurobi/blob/master/pygurobi/forest.lp). 

[forest.lp](https://github.com/AndrewBMartin/pygurobi/blob/master/pygurobi/forest.lp) is a harvest scheduling model that seeks the optimal assignment of harvest schedules to cut-blocks. Our forest management model will run for 10 periods where each period represents 10 years. 

The objective is to **maximize the total volume of timber harvested**.

The variables are: 

* **x[i,j]** - the number of hectares of cut-block, *i*, to be managed under schedule *j*, where *j* is a schedule of harvests. Each cut-block, *i*, belongs to a region, *r*, has both hardwood and softwood timber, and an initial age.

* **harv[s,r,t]** - the volume of timber harvested from cut-blocks of species *s* (softwood or hardwood), in region, *r* (north or south), , in period *t*. 

* **age[r,t]** - the area of the forest that is at least 60 years old in region, *r*, and period, *t*.

The constraints are:

* **gub(i)** - assignment problem constraints that say no more than the area of each cut-block can be assigned to harvest schedules.
* **harv(s,r,t)** - inventory constraint that says the **harv[s,r,t]** variables equal the volume harvested from cut-blocks of species, *s*, belonging to region, *r*, in period, *t*.
* **age(r,t)** - inventory constraint that says the **age[r,t]** variables equal the sum of cut-blocks that are at least age 60 in period, *t*, and belong to region, *r*.
* **env(r, t)** - environmental constraint that say at least 20% of the forest in each region, *r* has to be age 60 or greater after period 5.



Code to generate similar models can be found in the [or-models repository](https://github.com/AndrewBMartin/or-models/blob/master/sample_lp.py).

We'll talk about the *index of a variable* often in the following demonstration, i.e. the **[s,r,t]** part of **harv[s,r,t]**.

To demonstrate how to use PyGurobi, we're going to optimize the model, analyze it, and then modify model constraints. Some familiarity with the Gurobi Python API, called gurobipy, is assumed, and the gurobipy Python package must be installed to follow along with the example or use PyGurobi.

```python
>>> import pygurobi as pg 
>>> m = pg.read_model("forest.lp")
>>> m.optimize()
Optimize a model with 160 rows, 1945 columns and 10172 nonzeros
Coefficient statistics:
  Matrix range    [1e+00, 2e+02]
  Objective range [1e+00, 1e+00]
  Bounds range    [0e+00, 0e+00]
  RHS range       [1e+00, 1e+01]
Presolve removed 50 rows and 1102 columns
Presolve time: 0.06s
Presolved: 110 rows, 843 columns, 2770 nonzeros

Iteration    Objective       Primal Inf.    Dual Inf.      Time
       0    4.1153473e+04   1.100000e+01   0.000000e+00      0s
      20    4.0724706e+04   0.000000e+00   0.000000e+00      0s

Solved in 20 iterations and 0.08 seconds
Optimal objective  4.072470571e+04
```
We find that we have an optimal objective of 40,725 m<sup>3</sup> of harvest volume.

Now, let's review the model. First we'll list the variable sets and constraint sets.
```python
>>> pg.list_variables(m)
Variable set, Number of variables
x, 1963
harv, 40
age, 20

>>> pg.list_constraints(m)
Constraint set, Number of constraints
gub, 100
age, 20
```

We see that we have 3 variable sets, **x**, **harv**, and **age** with 1963, 40, and 20 variables in each, respectively. While there's 4 constraint sets, **gub**, **harv**, **age**, and **env** with 100, 40, 20 and 10 constraints, respectively.


Moving forward to model analysis, from the solution we want to know the periodic harvest volumes, so we'll print the "X" attribute, i.e. the solution value, of all the variables in the **harv** set.

```python
>>> # Print the specified attribute, in this case "X", of
>>> # the specified variable set, in this case "harv", from model, m.
>>> pg.print_variable_attr("X", model=m, name="harv")
harv[hw,north,0], 1728.47824679
harv[hw,north,1], 132.119561697
harv[hw,north,2], 660.597808483
harv[hw,north,3], 660.597808483
harv[hw,north,4], 996.054224258
harv[hw,north,5], 0.0
harv[hw,north,6], 150.0
harv[hw,north,7], 450.0
harv[hw,north,8], 750.0
harv[hw,north,9], 4460.13364558
harv[hw,south,0], 1032.1195617
...
```
This output is too messy to make much sense out of though. This is because each **harv** variable is indexed by region and species as well as period, so it's hard to see what the periodic harvest volumes are. Let's try a different way instead. Recall that for the **harv[s,r,t]** variables, index 0 is s, species, index 1 is r, region, and index 2 (or -1, a.k.a. last index) is t, period.


```python
>>> # In the following function first argument references the index we want to sum variables by. 
>>> # In this case this is the periods index which for the harvest variables is
>>> # the last index. This can be represented as 2 or, as I use, -1 (using Python indexing notation).
>>> periodic_harvest = pg.sum_variables_by_index(-1, model=m, name="harv")
>>> pg.print_dict(periodic_harvest)
0, 5598.37093395
1, 2517.06768112
2, 2517.06768112
3, 1957.71930754
4, 2915.86019735
5, 0.0
6, 900.0
7, 900.0
8, 3000.0
9, 20418.6199105
```
That's much easier to read. We can clearly see how much volume is harvested in each of the 10 periods. 

Notice how we passed `pg.sum_variables_by_index` a model object, m, and the name of a set of variables, "harv". This syntax allows me to access variables without managing them in the interpreter. There are however use cases where it's preferable to manage variables in the interpreter, for instance to pass a list of variables to be summed. PyGurobi offers syntax for this as well.

As an example, consider the case where we want to see the volume of softwood, sw, harvested in each period.


```python
# Print periodic softwood harvest volume.

>>> # Pass the following function a dictionary with index numbers as keys
>>> # and index values to filter by as values. In this example, {0: "sw"} says only return variables
>>> # that have value "sw" (softwood) in index 0.
>>> softwood_harvest = pg.get_variables_by_index_values(m, "harv", {0: "sw"})
>>> periodic_softwood_harvest = pg.sum_variables_by_index(-1, variables=softwood_harvest)
>>> pg.print_dict(periodic_softwood_harvest)
0, 2837.77312547
1, 1327.99162585
2, 1327.99162585
3, 1032.88237566
4, 1543.74804444
5, 0.0
6, 450.0
7, 450.0
8, 1500.0
9, 10610.9584725
```

To demonstrate how much code PyGurobi can save you from writing, consider printing this same data using only the Gurobi Python API. 
```python
>>> # Print periodic softwood volume
>>> 
>>> # Possible to do this step with a list comprehension in fewer lines, 
>>> # but that would be less clear.
>>> # Get softwood harvest variables
>>> softwood_variables = []
>>> for v in m.getVars():
...    split_name = v.varName.split("[")
...    if "harv" == split_name[0]:
...        indices = split_name[1].split(",")
...        if "sw" == indices[0]:
...            softwood_variables.append(v)
...
>>> # Create dictionary of softwood variables by period
>>> var_dict = {}
>>> for v in softwood_variables:
...     period = v.varName.split(",")[-1][:-1]
...     if period not in var_dict:
...         var_dict[period] = [v]
...     else:
...         var_dict[period].append(v)
...
>>> # Sum the softwood harvest volume by period
>>> summed_vars = {index_name: sum([v.X for v in index_vars])
...                       for index_name, index_vars in 
...                       sorted(var_dict.items())}
...                       
>>> print "\n".join(["{0}, {1}".format(index_name, index_value)                 
...                     for index_name, index_value in.                            
...                     sorted(summed_vars.items())])
0, 2837.77312547
1, 1327.99162585
2, 1327.99162585
3, 1032.88237566
4, 1543.74804444
5, 0.0
6, 450.0
7, 450.0
8, 1500.0
9, 10610.9584725
```

That's a lot more code than the PyGurobi version (20 lines versus 3 lines). We see that it takes less time to perform the analysis with PyGurobi than the Gurobi Python API, which also means there's less likelihood of making mistakes.

PyGurobi we can also display graphs using [Matplotlib](http://matplotlib.org/) (install separately).

```python
>>> # Display a graph of periodic harvest levels.
>>> 
>>> # Get the variables to graph
>>> harvest = pg.get_variables(m, "harv")
>>> 
>>> # Graph the variables
>>> pg.graph_by_index(m, harvest, -1, title="Periodic Volume", y_axis="Cubic Meters", x_axis="Period")
```
![alt text](https://github.com/AndrewBMartin/pygurobi/blob/master/harvest_volume.png?raw=true "Harvest Volume")

This allows us to easily visualize relationships in our data. In this case, drawing our attention to the fact that almost no timber is harvested in periods 5, 6 and 7.

In addition to model analysis, PyGurobi allows can enables us to modify constraints. For instance, if we want to change the right hand side of the age constraints so that we have at least 40% of forest over 60 years old in each region instead of 20%.

```python
>>> # Multiply the right hand side of all "env" constraints by 2
>>> # to change the constraint from 20% to 40%.
>>> pg.set_constraint_rhs_as_percent(2, model=m, name="env")
>>> 
>>> # Update, reset, and optimize the model
>>> pg.reoptimize(m)
Optimize a model with 160 rows, 1945 columns and 10172 nonzeros
Coefficient statistics:
  Matrix range    [1e+00, 2e+02]
  Objective range [1e+00, 1e+00]
  Bounds range    [0e+00, 0e+00]
  RHS range       [1e+00, 2e+01]
Presolve removed 50 rows and 1102 columns
Presolve time: 0.02s
Presolved: 110 rows, 843 columns, 2770 nonzeros

Iteration    Objective       Primal Inf.    Dual Inf.      Time
       0    4.1153473e+04   3.800000e+01   0.000000e+00      0s
      65    3.8280531e+04   0.000000e+00   0.000000e+00      0s

Solved in 65 iterations and 0.02 seconds
Optimal objective  3.828053089e+04
```

Not surprisingly, we see the objective value decrease - by about 5% - because the model must cut less wood to satisfy the new more difficult age constraint.

Let's graph the result the same way as before.

```python
>>> harvest = pg.get_variables(m, "harv")
>>> pg.graph_by_index(m, harvest, -1, title="Periodic Volume", y_axis="Cubic Meters", x_axis="Period")
```

![alt text](https://github.com/AndrewBMartin/pygurobi/blob/master/harvest_volume_age_con.png?raw=true "Harvest Volume")

Looking at harvest volumes, we see that they're all over the place. In the last period the model cuts almost 20,000 m<sup>3</sup> and in period 4 it cuts nothing. For more predictable timber flow, we'd like to smooth out harvests so that in each period we're cutting the same amount of volume. To achieve this we'll add a constraint saying that in each period, harvest volume has to be the same as it is in the subsequent period.

```python
>>> # Add this constraint period by period: harvest volume in 
>>> # period n has to equal the harvest volume in period n + 1
>>> for n in range(9):
>>> 
>>>     # Get harvest variables from period n
>>>     variables1 = pg.get_variables_by_index_values(m, "harv", {-1: n})
>>>     
>>>     # Get harvest variables from period n+1
>>>     variables2 = pg.get_variables_by_index_values(m, "harv", {-1: n+1})
>>>     
>>>     # Create  constraint in the form Σ(variables1) = Σ(variables2)
>>>     pg.add_constraint_variables(m, variables1, variables2, sense="=", con_name="even")
```

So now we've added a set of constraints, called **even**, that say in each period the volume harvested must equal the volume harvested in the next period. 

```python
>>> pg.reoptimize(m)
Optimize a model with 169 rows, 1945 columns and 10244 nonzeros
Coefficient statistics:
  Matrix range    [1e+00, 2e+02]
  Objective range [1e+00, 1e+00]
  Bounds range    [0e+00, 0e+00]
  RHS range       [1e+00, 2e+01]
Presolve removed 46 rows and 46 columns
Presolve time: 0.05s
Presolved: 123 rows, 1899 columns, 7639 nonzeros

Iteration    Objective       Primal Inf.    Dual Inf.      Time
       0    5.5798741e+05   4.323514e+03   0.000000e+00      0s
     424    2.5034308e+04   0.000000e+00   0.000000e+00      0s

Solved in 424 iterations and 0.06 seconds
Optimal objective  2.503430827e+04
```

We'll graph periodic harvest volumes to visualize the results.
```python
>>> harvest = pg.get_variables(m, "harv")
>>> pg.graph_by_index(m, harvest, -1, title="Periodic Volume", y_axis="Cubic Meters", x_axis="Period")
```
![alt text](https://github.com/AndrewBMartin/pygurobi/blob/master/harvest_volume_even.png?raw=true "Harvest Volume - Even")

We see that total harvest has gone down by about 35%, but every period harvests the same volume.


Now before wrapping up, we'll look at the harvest volumes by region, showing how much volume comes from the north and the south, respectively.
```python
>>> # By region
>>> pg.graph_by_two_indices(m, harvest, -1, 1, title="Periodic Volume by Region", y_axis="Cubic Meters", x_axis="Period")
```
![alt text](https://github.com/AndrewBMartin/pygurobi/blob/master/harvest_volume_by_region.png?raw=true "Harvest Volume by Region")

And, by species, showing the proportion of harvest volume that comes from softwood and hardwood.
```python
>>>  # By species
>>>  pg.graph_by_two_indices(m, harvest, -1, 0, title="Periodic Volume by Species", y_axis="Cubic Meters", x_axis="Period")
```
![alt text](https://github.com/AndrewBMartin/pygurobi/blob/master/harvest_volume_by_species.png?raw=true "Harvest Volume by Species")




And, that wraps up our introduction to PyGurobi. With this forest management model example, We've shown some of the key features of PyGurobi. We analyzed model variables in just a few lines of code, we added a non-trivial constraint with a simple for-loop, and we visualized the results of our modelling using 1 and 2 index graphs.

There's more to discover once you get started using PyGurobi, but I hope this tutorial has given you a taste of how to use it to make modelling in Gurobi faster and easier.