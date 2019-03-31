# Assembler Commands List

* Definition of variables

    All variables should be defined in `.var` section

    Usage:
    ```
    [VARIABLE_NAME] [VALUE]
    ```
     This command defines 4-bytes variable with the name `VARIABLE_NAME` equals to `VALUE`. The `VALUE` should be binary number


* **mov** command

    Usage:
    ```
    mov [VARIABLE_DEST_NAME][VARIABLE_SRC_NAME]
    ```
    This command assigns the value, stored in the variable with `VARIABLE_SRC_NAME` to the variable with `VARIABLE_DEST_NAME` name

* **exec** 

    Usage:
    ```
    exec [FUNCTION_NAME] 
        .input [INPUT_VAR_1 INPUT_VAR_2 ...] 
        .output [OUTPUT_VAR_1 OUTPUT_VAR_2 ...]
    ```

    This command ivokes the procedure which has name `PROCEDURE_NAME`
    After execution the procedure returns the control back

* **execif** 

    Usage:
    ```
    execif [VARIABLE_NAME] [FUNCTION_NAME] 
        .input [INPUT_VAR_1 INPUT_VAR_2 ...] 
        .output [OUTPUT_VAR_1 OUTPUT_VAR_2 ...]
    ```

    This command invokes the procedure if the variable with `VARIABLE_NAME` name is not equal to zero

* **term** 

    Usage:
    ```
    term
    ```

    This command stops the execution of the program

* **ret** 

    Usage:
    ```
    @my_func
        ...
        ret
    ```

    This command returns the cotrol to the place, where the procedure has been invoked

* **retif**

    Usage:
    ```
    @my_func
        ...
        retif [VARIABLE_NAME]
        ...
        ret
    ```

    This command returns the control if the variable, which has `VARIABLE_NAME` name, equal to zero

* **add** 

    Usage:
    ```
    add [VARIABLE_CHANGE][VARIABLE_TO_ADD]
    ```

    This command add the value, stored in `VARIABLE_TO_ADD` to the variable with name `VARIABLE_CHANGE`

* **sub** 

    Usage:
    ```
    sub [VARIABLE_CHANGE][VARIABLE_TO_SUB]
    ```

    This command subtract the value, stored in `VARIABLE_TO_SUB` from the variable with name `VARIABLE_CHANGE`

* **in** 

    Usage:

    ```
    in [VARIABLE_NAME]
    ```

    Using this command, the input mechanism is invoked, and user can type the value from the keyboard (using binary, decimal or hex format, which defined using the final symbol `b`, `d`, `h`), and this value will be stored in the variable with name `VARIABLE_NAME`

* **out**

    Usage:
    ```
    out [VARIABLE_NAME]
    ```

    Using this command, the value, stored in the variable with the name `VARIABLE_NAME`, can be sended to output stream

# Assembler program rules

The assembler supports the following sintaxis:
Each program consists of special sections with code, each of them starts with
the following:
```
@[SECTION_NAME]
```
Each section consists of subsections, each of them starts with the following:
```
    .[SUBSECTION_NAME]
```

The program should contain `@main` code section

## `@main` code section

This section contains following subsections:

* **.var** subsection

This subsection defines variables, used in the section

* **.code** subsection

This subsection defines code, performed in the section
Note, that this code is launched on the Virtual Machine

## Other code sections

Such code sections can be considered as functions
This section contains following subsections:

* **.input** subsection

This subsections defines variables, provided by called code

* **.output** subsection

This subsection defines the variables storing the result of the function and accessed from called code 

* **.var** subsection

Local variables of the subsection

* **.code** subsection

Code of the subsection to perform


## Example

This is the simple program, written using assembler.
This function computes the n-th number of fibbonachi

```
@main

    .var
        input 0b
        output 0b

    .code
        in input
        fibbonachi input output
        out output
        term

@fibbonachi
    
    .input
        n
    
    .output
        fib_n
    
    .var
        fib_n_minus_one 0b
        fib_n_minus_two 0b
        one 1b
        zero 0b

    .code
        mov fib_n zero
        retif n 
        sub n one
        mov fib_n one
        retif n 
        exec fibbonachi n fib_n_minus_one
        sub n one
        exec fibbonachi n fib_n_minus_two
        mov fib_n zero
        add fib_n fib_n_minus_one
        add fib_n fib_n_minus_two
        ret
```
    
    