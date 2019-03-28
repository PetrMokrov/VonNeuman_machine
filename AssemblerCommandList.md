# Assembler Commands List

* **def**
    
    Usage:
    ```
    [VARIABLE_NAME] def [VALUE]
    ```
    This command defines 4-bytes variable with the name `VARIABLE_NAME` equals to `VALUE`. The `VALUE` can have the following appearance:
    
    * `1001010b` . The final symbol `b` means that the preceding number should be interpreted as the bynary number

    * `1234566d` . The final symbol `d` means that the preceding number should be interpreted as the decimal number

    * `AB12EFh` . The final symbol `h` means that the preceding number should be interpreted as the hex number

    All `def` commands should be located in `@data` section

* **mov** 

    Usage:
    ```
    mov [VARIABLE_DEST_NAME][VARIABLE_SRC_NAME]
    ```
    This command assigns the value, stored in the variable with `VARIABLE_SRC_NAME` to the variable with `VARIABLE_DEST_NAME` name

* **exec** 

    Usage:
    ```
    exec [PROCEDURE_NAME]
    ```

    This command ivokes the procedure which has name `PROCEDURE_NAME`
    After execution the procedure returns the control back

* **execif** 

    Usage:
    ```
    execif [VARIABLE_NAME] [PROCEDURE_NAME]
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
    @procedure proc
        # code here
        ret
    ```

    This command returns the cotrol to the place, where the procedure has been invoked

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

There are three different section of program, written on assembler:

* **@data** section

    This is the first section in the program code

    In this section all variables, used in the program are defined, using `def` command:

    Usage:
    
    ```
    @data

    var_1 def 1b
    var_2 def 101b
    
    ```

* **@program** section

    This is the second section in the program code.
    This section includes the main program, which is launched in the VM.
    The program should be finished with `term` command
    
    Usage:

    ```
    @program
    add var_1 var_2
    ...
    term
    ```

* **@procedure** section

    This function defines the procedure, which can be invoked from the main program or from the other procedures. The procedure should be finished with `ret` command

    Usage:

    ```
    @procedure [PROCEDURE_NAME]

    sub var_1 var_2
    ...
    ret
    ```

## Example

This is the simple program, written using assembler

```
@data

    a def 0b
    one def 1b
    add_one_var def 0b

@program

    in a
    mov add_one_var a
    exec add_one 
    mov a add_one_var
    out a
    term

@procedure add_one

    add add_one_var one
    ret
```
    
    