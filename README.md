# Project 4

This project uses the `lexer` and `parser` functions from Project 1 and Project 2 to get an instance of a `DatalogProgram`. It also uses the `Interpreter.eval_schemes`, `Interpreter.eval_facts`, and `Interpreter.eval_queries` from Project 3. Project 4 must evaluate the rules in the Datalog program to add new facts to relations that exist in the database. This will be done by implementing the `Interpreter.eval_rule` function according to the algorithm specified in [RULE_INTERP.md](docs/RULES_INTERP.md).

Why do we use `Interpreter.eval_query` for evaluating rules? Consider this example rule: `R(X,Z) :- G(X,Y,'a'), R(Y,Z).` To evaluate this rule, we need to first compute the operands to the _join_ operation. The left operand is given by `G(X,Y,'a')` and the right operand is given by `R(Y,Z)`. Assuming that the relations are declared in the _Schemes_ section of the Datalog program as `G(A,B,C)` and `R(A,B)` respectively, then the relation for the left operand is `left = rename([X,Y], project([A,B], (select(C = 'a', G)))` and the relation for the right operand is `right = rename([Y,Z], project([A,B], R))`. These two operands are **the resulting relations when each operand is treated as a query**.

The `,` in the rule represents join. The head predicate in our rule, `R(X,Z)`, tells us how to format the final relation from the join: `project([X,Z], join(left, right))`. The tuples in this final relation are added to the relation `R` in the database. That may require a rename operation to use `Relation.union`. Rules are evaluated, in order, until no new facts are added to any of the relations in the database. The `Relation.union` relational operator must be used for Project 4. Whether you implemented union in Project 3 or will implement it in Project 4, you should include unit tests for this operation.

**Summary of Documentation**

- [README.md](README.md): describes project logistics
- [RULES_INTERP.md](docs/RULES_INTERP.md): describes how to use relational operators to interpret rules in Datalog
- [CODE.md](docs/CODE.md): describes the starter code
- [Testing Natural Join](docs/Project4_Guide.ipynb) (Jupyter Notebook)
- Lecture notes in [learningsuite.byu.edu](https://learningsuite.byu.edu) and specifically the slides in the lecture _Project 4 Discussion_.

**You are strongly encouraged to review the above documentation _before_ proceeding further**.

## Table of Contents
- [Developer Setup](#developer-setup)
- [Project Requirements](#project-requirements)
- [AI Policy for Project 3](#ai-policy-for-project-3)
- [Unit Tests](#unit-tests)
- [Integration Tests (pass-off)](#integration-tests-pass-off)
- [Code Quality](#code-quality)
- [Submission And Grading](#submission-and-grading)
- [Best Practices](#best-practices)

## Developer Setup

The Project 4 setup is the same setup as for Project 3. You must create the virtual environment and activate it, install the package in the virtual environment, install pre-commit, and then copy over files for the solutions to the prior projects.

Here are the files to copy from Project 3 into the `src/project4/` folder:

  * `datalogprogram.py`
  * `fsm.py`
  * `interpreter.py`
  * `lexer.py`
  * `parser.py`
  * `relation.py`
  * `./tests/test_relation.py`
  * `./tests/test_interpreter.py`

The `token.py` file is unchanged here and should not be copied over. Other test files from older projects can be copied as needed.


## Project Requirements

1. The project must be completed individually -- there is no group work.
1. Project pass-off is on GitHub. You will commit your final solution to the `master` branch of your local repository and then push that commit to GitHub. Multiple commits, and pushes, are allowed. A push triggers a GitHub action that is the auto-grader for pass-off. The TAs look at both the result of the auto-grader on GitHub and your code to determine your final score. Projects that use iteration instead of tail recursion will not be accepted.
1. You must pass all integration tests up to, and including, `tests/test_passoff_80.py` to move on to the next project. Bucket 80 is the minimum functionality to complete the course.
1. You must **_"do the math"_** to write positive and negative tests in `tests/test_relation.py` for `Relation.join` in `src/project3/relation.py`. AI may be used to generate the code for the testing the function once you **_"do the math"_** for the inputs and outputs and write a few examples for the AI to follow using your inputs and outputs. See [AI Policy for Project 3](#ai-policy-for-project-3) for details.
1. You must implement `Relation.join` in `src/project3/relation.py`. **AI may not be used for any part of the implementation.**
1. You must interpret the Datalog program, including the rules, with relational algebra by implementing `Interpreter.eval_rules` in `src/project3/interpreter.py`. The other functions will be implemented in later projects. See [RULES_INTERP.md](docs/RULES_INTERP.md) for details. **AI may not be used for any part of the implementation.**
1. You must use [input partitioning](#input-partitioning) to write tests for `join` and `eval_rules` using the pattern demonstrated in the Project 3 Jupyter notebook tutorial. We won't be looking for a perfect partitioning of the input when we grade your tests, but we will be looking to see if you made an effort to generate tests that had good test coverage. After you **do the math** to find inputs for each of the partitions, then you may use AI to generate the code for the actual tests. We suggest that you use a parameterized test.
1. Your code must not report any issues with the following code quality tool run in the integrated `vscode` terminal from the root of the project directory: `pre-commit run --all-files`. This tool includes _type checking_, which means that type annotations are required in your code.
1. Your code must pass each bucket in 150 seconds or less. If you have trouble meeting this requirement, see the FAQ in [RULES_INTERP](docs/RULES_INTERP.md).

Consider using a branch as you work on your submission so that you can `commit` your work from time to time. Once everything is working, and the auto-grader tests are passing, then you can `merge` your work into your master branch and push it to your GitHub repository. Ask your favorite AI for help learning how to use Git branches for feature development.

## AI Policy for Project 4

Project 4 code is very algorithmic and specific to interpreting Datalog rules. It does not include repeated code with similar structure that AI can learn, adapt, and repeat. As such, you are expected to write all the implementation code for `Relation.join` class and `Interpreter.eval_rules` class without any AI assist.

AI may be used to help generate code for tests **after you "Do the math" to figure out the input and expected output**. In this application, you figure out the computation with the math, and the AI then generates the test code for your given input and output relations.

We recommend that the test code for `eval_rules` be parameterized since the test for each input is the same while there should be least one test for each input partition.

## Unit Tests

You must write tests for `Relation.join` and `Interpreter.eval_rules`. These tests should be derived from input partitioning -- divide the input space into interesting partitions and create a test for each partition.

## Integration Tests (pass-off)

All the primary tests are in a single file: `tests/test-passoff.py`. Running individual tests is the same using either `pytest` directly or the testing pane in vscode (**recommended**). As before, the `xx` on each bucket denotes the available points for passing the tests in that bucket. The value of each test in each bucket is uniform: _points-for-bucket/number-of-tests-in-bucket_. Bucket 80 is the minimum requirement to pass the course.

## Code Quality

Pre-commit must run on all the files and report no errors.

## Submission and Grading

The minimum standard for this project is **bucket 80**. That means that if all the tests pass in all buckets up to and including bucket 80, then the next project can be started safely. You can run each bucket from the testing pane or with `pytest` on the command line. Passing everything up to and including `test_passoff_80.py` is the minimum requirement to move on to the next project.

Submit Project 2 for grading by doing the following:

  * Commit your solution on the master branch
  * Push the commit to GitHub -- that should trigger the auto-grader
  * Goto [learningsuite.byu.edu](https://learningsuite.byu.edu) at _Assignments_ &rarr; _Projects_ &rarr; _Project 2_ to submit the following:
    1. Your GitHub ID and Project 2 URL for grading.
    1. A short paragraph outlining (a) how you prompted the AI to generate any code (if you used it) and (b) how you determined the quality and correctness of that code.
    1. A screen shot showing no issues with `pre-commit run --all-files`.
  * Confirm on the GitHub Actions pane that the pass-off tests passed, or alternatively, goto the Project 1 URL, find the green checkmark or red x, and click it to confirm the auto-grader score matches the pass-off results from your system.

### Paragraph on AI

Guidelines for answering

_"A short paragraph outlining (a) how you prompted the AI to generate any code (if you used it) and (b) how you determined the quality and correctness of that code."_

These guidelines give examples from Project 1.

* Brief means no more than 500 words.
* Be specific about what code was generated. _"AI generated FSM code for the following non-terminals: `facts`, etc."_
* Be general about the final form of the prompts used to generate the code and any prompt iteration that was required. _"I gave the AI example code and asked it to create code that matched the pattern, and style, in that example code. I had to revise the prompt to specifically ask it to not generalize an FSM to detect a supplied string."_
* Be specific about how you determined the quality and correctness of generated code. _"A manual visual inspection was sufficient to determine quality and correctness because the generated code was trivial. I also ran the code quality tools on the generated code as a second level check."_
* Be specific about where else AI was leveraged. _"I used AI to breakdown and explain the pseudo-code for the `lexer` algorithm as well as the `FiniteStateMachine` class. AI also provided test inputs for my `STRING` FSM to help debug the apostrophe escape sequence."_
* Be specific about how you used AI to write tests, and how you generated the parse trees necessary for writing tests based on the math.

## Best Practices

Here is the suggested order for Project 4:

1. Figure out the input partition for `Relation.join` -- you must consider at least three unique tests: no shared attributes, attributes shared, and a mix of shared and not shared attributes:

    1. Write a positive test that may fail (should fail the first test because no code has been written and may fail other tests depending on the code written for the first test).
    1. Write code to pass the positive test.

1. Figure out the input partition for `Interpreter.eval_rules` -- as a starting point consider if number of iterations to reach a fix-point matters in testing, if the number of rules being evaluated matters, or if the composition of rules matter:

    1. Write a positive test that may fail (should fail the first test because no code has been written and may fail other tests depending on the code written for the first test).
    1. Write code to pass the positive test.

1. Run the pass-off tests -- debug as needed.
