# Brewin++

## Variables and Typing
Static typing for all variables
- All variables must be defined before they are used (like in C++) and a type must be specified in each definition
- All languages must ensure that all variable assignments and expressions have compatible types; no implicit conversions are allowed.

Example:

```
func main void
    var int b c d     # b, c, and d are integer variables
    assign b 5
    var bool e        # e is a boolean variable
    assign e "foobar" # this would be a type error!
endfunc
```

> Note: Even though Brewin++ is an interpreted language, by adding variable definitions with types, we enable all variable's types to be determined prior to execution, so a compiler could be written if we desired, making this a statically-typed language. But technically, it's still dynamically typed for now.

## Scoping
Brewin++ now implements lexical scoping for all variables, just like you'd see in C++. Here's an example program:

```
func main void
    var int a
    assign a 5
    if > a 0
        funccall print a # prints 5
        var string a     # legal: shadows our original a variable
        assign a "foobar"
        funccall print a # prints foobar
        var bool b
    endif
    funccall print a     # prints 5
    funccall print b     # Name error: b is out of scope
endfunc
```

## Functions
Brewin++ now supports parameters for user-defined functions, and allows arguments to be passed to these functions by value or by reference. Functions also nowmust have an explicit return type. To access the return value from a function, you no longer refer to the `result` variable, but refer to `resulti` for integers, `resultb` for booleans, and `results` for strings.

Example:

```
# Equivalent to: bool absval(int val, int& change_me)
func absval val:int change_me:refint bool
    if < val 0
        assign change_me * -1 val
        return True
    else
        assign change_me val
        return False
    endif
endfunc

func main void
    var int val output
    assign val -5
    funccall absval val output
    funccall print "The absolute value is: " output
    funccall print "Did I negate the input value? " resultb
endfunc
```

# CS 131 Fall 2022: Project Starter

Hey there! This is a template repository that contains the necessary boilerplate for [CS 131](https://ucla-cs-131.github.io/fall-22/)'s quarter-long project: making an interpreter. The project specs are as follows:

1. [Project 1 Spec](https://docs.google.com/document/d/17Q4EPgHLMlMuQABhmgTpk_Ggxij0DZwvPQO2uzVVPzk/)
2. [Project 2 Spec](https://docs.google.com/document/d/14cZ7s-RPDO3FvYCDFMlS_NrGSSPUmavSX0wzsN-yHDw/edit#)
3. Project 3 - coming soon!

There are three stages to the project; students are currently at the second. Thus, this folder contains the necessary bootstrapping code:

- `intbase.py`, the base class and enum definitions for the interpreter
- a sample `readme.txt`, which should illustrate any known bugs/issues with the program (or, an "everything's good!")

As well as **canonical solutions for Project 1** (written by Carey):

- `interpreterv1.py`: a top-level entrypoint: has some utility classes, finding the main function, the interpreter loop, and handlers for each token type
- `env_v1.py`: manages the "environment" / state for a program
- `func_v1.py`: manages and caches functions (will be much more useful in Project 2!)
- `tokenize.py`: tokenization logic

You do not have to use the canonical solutions for Project 2; in particular, since you didn't write the code, it may be confusing!

Some notes on your submission (for Project 2; we'll update this for later projects):

1. You **must have a top-level, versioned `interpreterv2.py` file** that **exports the `Interpreter` class**. If not, **your code will not run on our autograder**.
2. You may also submit one or more additional `.py` modules that your interpreter uses, if you decide to break up your solution into multiple `.py` files.

You can find out more about our autograder, including how to run it, in [its accompanying repo](https://github.com/UCLA-CS-131/fall-22-autograder).

## Licensing and Attribution

This is an unlicensed repository; even though the source code is public, it is **not** governed by an open-source license.

This code was primarily written by [Carey Nachenberg](http://careynachenberg.weebly.com/), with support from his TAs for the [Fall 2022 iteration of CS 131](https://ucla-cs-131.github.io/fall-22/).
