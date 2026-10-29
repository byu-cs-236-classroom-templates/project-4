# Evaluating Expressions in Rules

Deeper learning in Project 2 added a small expression language to the
parser: a rule may end with one optional comparison, `Less(left, right)`, where
`left` and `right` are arithmetic expression trees built from `Integer`,
`Variable`, `Add`, and `Multiply` nodes. In Project 2 the tree was only parsed.
In this project you **evaluate** it.

```text
small(X) :- value(X), X * 2 + 1 < 10.
```

The comparison is a **filter**. It never binds variables and never produces new
values; it only decides which rows of the body result survive.

------------------------------------------------------------------------

## Where Expressions Fit in Rule Evaluation

The steps in [EVALUATE_RULE_ALGORITHM.md](./EVALUATE_RULE_ALGORITHM.md) gain one
new step between the joins and the projection:

1. Evaluate each body predicate (select, project, rename).
2. Join the intermediate results.
3. **If the rule has an expression, select the rows of the joined relation that satisfy it (new).**
4. Project the columns that appear in the head.
5. Transpose the columns to match the head.
6. Rename to the header of the relation to match that of the same named relation in the database.
7. Union with the database relation.

The filter **must** come after _all_ the joins and **before** the project.
Before the joins, a variable used in the expression may not yet be in the
relation. After the project, a variable used only in the expression (for
example `Y` in `answer(X) :- left(X), right(Y), X + Y < 20.`) will have been
dropped.

------------------------------------------------------------------------

## What You Need to Change

You are responsible for all code changes. The pieces are:

1. **Expression classes**: The tree node classes (`Integer`, `Variable`,
   `Add`, `Multiply`, `Less`) need a way to be evaluated. See below.
2. **`Relation`** (`relation.py`): a new select that takes an expression.
3. **`Interpreter`** (`interpreter.py`): call the new select in rule evaluation.

This document assumes the Project 2 work is done: the parser already builds
the expression tree and the `Rule` already carries it.

You must also write your own tests for the evaluator, the new select, and
rules with expressions. Tests must be **type correct**: relations only hold
`str` values (quotes included for facts), and expressions only hold `int`
literals and variable names. Do not write a test that puts an `int` in a
`RelationTuple` or a non-integer string in a column an expression uses.

------------------------------------------------------------------------

## Evaluating an Expression Tree

An arithmetic tree is evaluated recursively, mirroring how it was built. Given a
**binding** from variable names to `int` values:

| Node               | Value                                              |
|--------------------|----------------------------------------------------|
| `Integer(v)`       | `v`                                                |
| `Variable(name)`   | `bindings[name]`                                   |
| `Add(l, r)`        | `eval(l, bindings) + eval(r, bindings)`            |
| `Multiply(l, r)`   | `eval(l, bindings) * eval(r, bindings)`            |
| `Less(l, r)`       | `eval(l, bindings) < eval(r, bindings)` (a `bool`) |

Precedence and parentheses are already encoded in the tree structure, so
evaluation needs no special handling for them: the deeper nodes are evaluated
first simply because the recursion reaches them first.

For example, with `X = 2` and `Y = 4`, the tree for `X + Y * 2 < 20` evaluates as

```text
Less(Add(X, Multiply(Y, 2)), 20)
  -> Add(2, Multiply(4, 2)) < 20
  -> Add(2, 8) < 20
  -> 10 < 20
  -> True
```

Two reasonable designs are:

-   a method on each node class (e.g., `evaluate(self, bindings: dict[str, int])`), or
-   a single recursive function that uses `match` / `isinstance` to dispatch on
    the node type.

Either way the evaluator should only know about `int` and variable names. It
should not know anything about `Relation` or `RelationTuple`.

------------------------------------------------------------------------

## Moving Between `str` and `int`

This is the most error-prone part of the project, so it is worth being explicit.

### The types involved

-   `RelationTuple = tuple[str, ...]` in `relation.py`. **Every value stored in
    a relation is a `str`.** `Relation.add_tuple` enforces this and raises
    `IncompatibleOperandError` if any element is not a `str`.
-   Facts come from the parser as `STRING` parameters, and the string value
    includes its quotes (the tests use values like `"'c'"`). So a fact such as
    `value('2').` is stored as the tuple `("'2'",)`, not `("2",)`.
-   `Relation.header` is `list[str]` and holds the variable names (`"X"`, `"Y"`).
-   The expression tree holds `int` values in `Integer` nodes (the lexer `INT`
    token text converted with `int(...)`) and `str` names in `Variable` nodes.
-   Expression evaluation works on `int` only.

So there is a type boundary between the relation (`str`) and the evaluator
(`int`).

### Direction 1: `str` to `int` (relation into the evaluator)

For each tuple in the relation, build the binding the evaluator needs:

1. Pair each header name with the value at the same position in the tuple
   (`zip(self.header, row)`).
2. Convert each value that the expression uses from `str` to `int`.
3. Evaluate the `Less` node with that binding.

```text
header = ["X", "Y"]
row    = ("'2'", "'4'")          # strings, quotes included
         -> strip the quotes     -> ("2", "4")
         -> int(...)             -> {"X": 2, "Y": 4}
         -> evaluate expression  -> True / False
```

Points to watch:

-   **Strip the quotes first.** `int("'2'")` raises `ValueError`; only
    `int("2")` works. Strip the single-quote characters from both ends of the
    stored value (e.g., `value[1:-1]` when it starts and ends with `'`, or
    `value.strip("'")`). A value that has no quotes should also work, in case
    unquoted integers are ever stored.
-   **Negative numbers** are fine: `int("-10")` is `-10`.
-   **Convert only what you need.** The header may contain columns that are
    not in the expression and are not numbers (e.g., `'alice'`). Do not
    convert the whole row. Collect the variable names that occur in the
    expression (walk the tree) and convert only those columns.
-   **Convert once per row**, not once per use of a variable in the tree.
-   **A failed conversion is a bug, so crash.** If a column the expression
    uses does not hold an integer (e.g., `'abc'`), the program or its tests are
    wrong. Do not skip the row or silently continue. Catch the `ValueError`
    from `int(...)` and raise an `AssertionError` (for example
    `raise AssertionError(f"cannot convert {value!r} to int") from e`, or
    `assert` on a validity check) so the interpreter crashes and points at the
    bad value while you debug.
-   **Unbound variables.** If the expression names a variable that is not in the
    relation's header, no row can ever be evaluated. Raise
    `IncompatibleOperandError`, as the other selects do for an unknown column,
    rather than a bare `KeyError`. Check this once up front, before looping over
    rows.

### Direction 2: `int` back to `str` (out of the evaluator)

For this project, **nothing converted to `int` ever goes back into a relation.**
The comparison produces a `bool`, and the select uses it only to decide
whether to keep the **original** tuple. Arithmetic results such as `X * 2 + 1`
are intermediate values that are discarded.

That has an important consequence: when you keep a row, keep the original
`RelationTuple` of strings, quotes and all. Do not rebuild it from the `int`
values (that would drop the quotes and change e.g. `"'02'"` into `"2"`). The
new relation has the same header and holds the unchanged tuples that passed
the filter.

Only if you add your own code that stores an integer in a relation (not needed
here) would you convert it with `str(value)` and add quotes to match the
representation of the other facts, because `add_tuple` rejects `int`.

### Summary of the boundary

| Where                          | Type                       | Notes                         |
|--------------------------------|----------------------------|-------------------------------|
| Lexer `INT` token text         | `str`                      | e.g. `"-10"`                  |
| `Integer` node in the tree     | `int`                      | converted with `int(text)`    |
| `Variable` node in the tree    | `str`                      | a name matching the header    |
| Tuple element in `Relation`    | `str`                      | quoted, e.g. `"'2'"`          |
| Binding passed to the evaluator| `dict[str, int]`           | built per row                 |
| Result of `Less`               | `bool`                     | decides keep or discard       |
| Tuple kept in the result       | `str` (unchanged original) | same header as the input      |

------------------------------------------------------------------------

## The New Select on `Relation`

Add a third kind of select next to `select_eq_col` and `select_eq_lit`. For
example:

```python
def select_expr(self, expression: Less) -> "Relation":
    """The select of this relation where each tuple satisfies `expression`.

    Every variable in `expression` must be in the header. Values for those
    variables are converted from `str` to `int` to evaluate the expression.
    The new relation has the same header and only the original tuples that
    satisfy the expression.

    Raises:
        error (IncompatibleOperandError): Error if a variable in `expression`
            is not found in the header.
    """
```

Outline:

1. Collect the variable names used in `expression`; raise
   `IncompatibleOperandError` if any is not in `self.header`.
2. Look up the index of each variable in the header once.
3. Start an empty set of tuples.
4. For each tuple in `self.set_of_tuples`: build the `dict[str, int]` binding
   from only those indexes (strip quotes, `int(...)`), evaluate the expression,
   and if it is `True` add the **original** tuple to the new set.
5. Return `Relation(self.header, new_tuples)`.

Like the other operations, this must **not** modify `self`.

------------------------------------------------------------------------

## Using It in the Interpreter

In `eval_rules`, after the body predicates have been joined into one relation,
and only when `rule.expression` is not `None`, replace the joined relation by
the filtered one before projecting:

```python
joined = ...                       # result of joining all body predicates
if rule.expression is not None:
    joined = joined.select_expr(rule.expression)
# continue: project, reorder, rename, union
```

Rules without an expression behave exactly as before.

### Worked Example

```text
value(2).   value(4).   value(7).      # stored as ("'2'",), ("'4'",), ("'7'",)

small(X) :- value(X), X * 2 + 1 < 10.
```

1. `value(X)` gives the relation with header `["X"]` and tuples `("'2'",)`, `("'4'",)`, `("'7'",)`.
2. No joins (single predicate).
3. Select with the expression, binding after conversion:

    | Tuple      | Binding   | `X * 2 + 1 < 10` | Kept? |
    |------------|-----------|------------------|-------|
    | `("'2'",)` | `X = 2`   | `5 < 10` True    | yes   |
    | `("'4'",)` | `X = 4`   | `9 < 10` True    | yes   |
    | `("'7'",)` | `X = 7`   | `15 < 10` False  | no    |

4. Project to `X`, reorder, rename, and union with `small`: `small` gains
   `("'2'",)` and `("'4'",)`, still strings with their quotes.

A two-predicate example, where the expression uses a variable from each side:

```text
answer(X) :- left(X), right(Y), (X + Y) * 2 < 20.
```

The join produces header `["X", "Y"]`; the select evaluates the expression on
each joined row; the project then drops `Y`. Had the project come first, `Y`
would be gone and the expression could not be evaluated.

------------------------------------------------------------------------

## Checklist

-   [ ] A failed `int` conversion raises an `AssertionError` (no skipping, no swallowing).
-   [ ] Your own tests are type correct and cover the evaluator, the select, and rules with expressions.
-   [ ] Expression nodes can be evaluated against a `dict[str, int]`.
-   [ ] The new select converts `str` to `int` only for variables in the expression, after stripping quotes.
-   [ ] The new select returns the original `str` tuples and the same header, and does not mutate `self`.
-   [ ] An expression variable missing from the header raises `IncompatibleOperandError`.
-   [ ] The interpreter applies the select after all joins and before the project.
-   [ ] A rule with no expression is evaluated exactly as before.
-   [ ] Fixed-point iteration still stops when no new tuples are added (the filter does not change this logic).
