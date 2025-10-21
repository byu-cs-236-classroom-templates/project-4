# Datalog Rule Interpreter

Project 4 is to write an interpreter that uses relational database operations to evaluate the rules in a Datalog Program. At the end of this project, you will have a fully functional Datalog interpreter. Here is a diagram illustrating the project.

<img src="figs/Project 4 Diagram.png" alt="Interpreting Queries" width="915" />

Here is an example input to the interpreter.

```
Schemes:
  snap(S,N,A,P)
  csg(C,S,G)
  cn(C,N)
  ncg(N,C,G)

Facts:
  snap('12345','C. Brown','12 Apple St.','555-1234').
  snap('22222','P. Patty','56 Grape Blvd','555-9999').
  snap('33333','Snoopy','12 Apple St.','555-1234').
  csg('CS101','12345','A').
  csg('CS101','22222','B').
  csg('CS101','33333','C').
  csg('EE200','12345','B+').
  csg('EE200','22222','B').

Rules:
  cn(c,n) :- snap(S,n,A,P),csg(c,S,G).
  ncg(n,c,g) :- snap(S,n,A,P),csg(c,S,g).

Queries:
  cn('CS101',Name)?
  ncg('Snoopy',Course,Grade)?
```

Your code must interpret the full program, including the rules using relational algebra, to update the relations with new facts and then answer each of the queries resulting in the following output.

```
Rule Evaluation
cn(c,n) :- snap(S,n,A,P),csg(c,S,G).
  C='CS101', N='C. Brown'
  C='CS101', N='P. Patty'
  C='CS101', N='Snoopy'
  C='EE200', N='C. Brown'
  C='EE200', N='P. Patty'
ncg(n,c,g) :- snap(S,n,A,P),csg(c,S,g).
  N='C. Brown', C='CS101', G='A'
  N='C. Brown', C='EE200', G='B+'
  N='P. Patty', C='CS101', G='B'
  N='P. Patty', C='EE200', G='B'
  N='Snoopy', C='CS101', G='C'
cn(c,n) :- snap(S,n,A,P),csg(c,S,G).
ncg(n,c,g) :- snap(S,n,A,P),csg(c,S,g).

Schemes populated after 2 passes through the Rules.

Query Evaluation
cn('CS101',Name)? Yes(3)
  Name='C. Brown'
  Name='P. Patty'
  Name='Snoopy'
ncg('Snoopy',Course,Grade)? Yes(1)
  Course='CS101', Grade='C'
```

## New Database Operation

Implement `join` in the `Relation`.

The following pseudo-code describes one way to compute the join of relations $r1$ and $r2$.

```
make the header h for the result relation
    (combine r1's header with r2's header)

make a new empty relation r using header h

for each tuple t1 in r1
    for each tuple t2 in r2

    if t1 and t2 can join
        join t1 and t2 to make tuple t
        add tuple t to relation r
    end if

    end for
end for
```

Note that the following operations used in the join should be decomposed into separate routines.

* combining r1's header with r2's header
* testing t1 and t2 to see if they can join
* joining t1 and t2

These need information about which columns between the two relations should overlap; this information should be calculated once per join operation.

Join must be able to join two relations regardless if they have common attribute names or not.

The `Relation.reorder` operation will be important to interpreting rules the rules may reorder columns in the in the final relation. Test the new operations before using them to evaluate rules as described in the next section.

## Evaluating Rules

Add rule evaluation to the query interpreter from the last project. The major steps of the interpreter are:

1. Process the schemes (same as the last project)
1. Process the facts (same as the last project)
1. **Evaluate the rules** (**new code**)
1. Evaluate the queries (same as the last project)

[Evaluating Rules - Project4.pdf](./Evaluating%20Rules%20-%20Project%204.pdf) is a comprehensive guide to what you need to implement this project. It covers the same steps as in this guide only in greater detail and with examples. **You are encouraged to review it carefully before attempting the project.**

Evaluate each rule using relational algebra operations as follows:

1. **Evaluate the predicates on the right-hand side of the rule:**

    For each predicate on the right-hand side of a rule, evaluate the predicate in the same way you evaluated the queries in the last project (using select, project, and rename operations). Each predicate should produce a single relation as an intermediate result. If there are $n$ predicates on the right-hand side of a rule, there should be $n$ intermediate results. If you are careful, you can use the `eval_queries` function you wrote in Project 3 to perform this task.

2. **Join the relations that result:**

    If there are two or more predicates on the right-hand side of a rule, join the intermediate results to form the single result for Step 2. Thus, if $p1$, $p2$, and $p3$ are the intermediate results from Step 1, join them $(p1\ \ \mathtt{|\times|}\ \ p2\ \ \mathtt{|\times|}\ \ p3)$ into a single relation.

    If there is a single predicate on the right hand side of the rule, use the single intermediate result from Step 1 as the result for Step 2.

3. **Project the columns that appear in the head predicate:**

    The predicates in the body of a rule may have variables that are not used in the head of the rule.  Use a project operation on the result from Step 2 to remove the columns that don't appear in the head of the rule and to reorder the columns to match the order in the head. 

4. **Reorder the columns of the relation to produce the order in the head prediate:**
    The variables in the head predicate may appear in a different order than the columns of the relation produced in the previous step

5. **Rename the relation to make it union-compatible:**

    Rename the relation that results from Step 3 to make it union compatible with the relation that matches the head of the rule. Rename each attribute in the result from Step 3 to the attribute name found in the corresponding position in the relation that matches the head of the rule.

6. **Union with the relation in the database:**

    Union the result from Step 4 with the relation in the database whose name matches the name of the head of the rule.

Evaluate the rules in the order they are given in the input file.

---

## The Fixed-point Algorithm

Use a fixed-point algorithm to repeatedly evaluate the rules. If an iteration over the rules changes the database by adding at least one new tuple to at least one relation in the database, the algorithm evaluates the rules again. If an iteration over the rules does not add a new tuple to any relation in the database, then the fixed-point algorithm terminates.

An easy way to tell if any tuples were added to the database is to count the number of tuples in the database both before and after evaluating the rules. If the two counts are different, something changed, and the rules need to be evaluated again. However, this is computationally inefficient. A more efficient way is to use the return value of `set.insert`, which includes a boolean that is true if the inserted element was new to the set.

## Assumptions

You may assume the following about the Datalog input:

1. The Datalog program is semantically correct and satisfies all def-use requirements.
1. The head of every rule will only contain variable names. No strings will be given in the head of any rule.
1. No two variable names in a rule head are the same. Each variable in a rule head is unique in that rule head.
1. Every variable name in the head of a rule will appear in at least one predicate in the body (right-hand side) of the rule.

## FAQ

1. **When should a rule update the associated relation?**

    When a rule is evaluated, any tuples generated by the rule should be added to the associated relation immediately.

    For example, suppose there are two rules, $R1$ and $R2$, associated with relation $A$. Suppose $R1$ is evaluated first then followed by $R2$. When $R1$ is evaluated, any new tuples it generates are added to $A$. Then $R2$ is evaluated using the updated relation $A$ that contains new tuples from $R1$, and any new tuples $R2$ generates are added to $A$.

2. **When should the algorithm that repeatedly evaluates rules terminate?**

    The algorithm should evaluate the rules, repeatedly, until the number of tuples in all the relations in the database does not change. At this point, the rules do not generate any new tuples.

3. **What order should be followed in evaluating rules?**

    Evaluate the rules in the order they are given in the input file.

4. **Why is the code taking a long time to run?**

    Are you running your code in Visual Studio? Visual Studio usually runs code in 'debug' mode. Debug mode may slow down the code significantly. Try running the code outside of Visual Studio (from the command line), or configure Visual Studio to run in [release mode](https://docs.microsoft.com/en-us/visualstudio/debugger/how-to-set-debug-and-release-configurations).

    Other things that may impact running time include:

    1. The computer on which the code is running. (Run the code on the lab computers for the best approximation of how it will run on the TA computers.)
    1. Using a list to store the tuples in a relation instead of a set. (Sorting lists and searching lists for duplicates are relatively slow operations).
