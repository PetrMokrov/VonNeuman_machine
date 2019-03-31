# Von Neuman Virtual Machine

## About 

This project includes realisation of a Virtual Machine, based on Von Neuman architecture concept.
The VM is implemented on python.

## Usage

*For correct working of all components of the project, execute all scripts from `.` directory*

To perform a programm using the VM, it should be written in the special assembler.
Full command list, supported by the assembler is available in `AssemblerCommandList.md` file

The programm should be compiled before launching the VM
To compile the program, use `.\sources\compiler.py` script:

Supported command line arguments for `.\sources\comiler.py` are following:
* **--source** **-s** \[PATH_TO_PROGRAM_FILE\] specifies the file with the program to compile
* **--name** **-n** \[DESIRED_BIN_FILE_NAME\] specifies the name of binary file with the compiled program. All binary files are stored in `.\bin\` directory

The example of using the script:
```
> python .\sources\comiler.py -s path\to\my\program\file -n my_compiled_file
```

A binary file can be executed on VM by launching `.\sources\vm.py` script:
To execute the binary file, just pass the path to binary file as the command line argument as following:
```
> python .\sources\vm.py path\to\binary\program\file
```

Be careful with the depth of recursion. Size of stack is bounded by 1024 bytes.