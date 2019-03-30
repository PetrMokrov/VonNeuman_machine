import sys
import argparse
import json
import copy
import os

all_commands_list = [
    'mov', 
    'exec', 
    'execif', 
    'term', 
    'ret', 
    'retif', 
    'add', 
    'sub', 
    'in', 
    'out']

binarised_commands_dict = {
    'mov': b'\x00\x00\x00\x00',
    'send' : b'\x00\x00\x00\x10',
    'add': b'\x00\x00\x00\x01',
    'sub': b'\x00\x00\x00\x02',
    'in': b'\x00\x00\x00\x03',
    'out': b'\x00\x00\x00\x04',
    'jmp': b'\x00\x00\x00\x05',
    'rec': b'\x00\x00\x00\x50',
    'jmpif': b'\x00\x00\x00\x06',
    'term': b'\xFF\xFF\xFF\xFF'
}

command_size = 4

registers_addresses = {
    'IP': b'\x00\x00\x00\x00',
    'SP': b'\x00\x00\x00\x04',
    'R1': b'\x00\x00\x00\x08',
    'R2': b'\x00\x00\x00\x0C',
    'R3': b'\x00\x00\x00\x10',
    'OFFSET': b'\x00\x00\x00\x14'
}

class Function:

    def __init__(self, lines):
        '''
        this function parse lines to more appropriate format
        '''
        index = 0
        raw_func_name = lines[index]
        self.name = raw_func_name.strip()[1:].strip()
        index = 1

        while True:
            new_index = self._parse_new_subsection(lines, index)
            if new_index == index:
                break
            index = new_index
    
    def to_json(self, name):
        dict_to_json = {}
        dict_to_json['name'] = self.name
        dict_to_json['var'] = self.variables
        dict_to_json['code'] = self.commands
        if not self.name == 'main':
            dict_to_json['input'] = self.input_variables
            dict_to_json['output'] = self.output_variables
        
        with open(name, "w") as f:
                json.dump(dict_to_json, f, indent=4, sort_keys=True)
        

    
    def _parse_new_subsection(self, lines, index):
        # check for end of lines
        if self._is_end_of_lines(lines, index):
            return index
        
        subsec_name = ''

        while True:
            
            if self._is_new_subsection_head(lines, index):
                subsec_name = lines[index].strip()[1:]
                index += 1
                break
            index += 1

        # different types of parsing, depends of subsection name
        if subsec_name == 'var':
            index = self._parse_var_subsection(lines, index)
        
        elif subsec_name == 'code':
            index = self._parse_code_subsection(lines, index)
        
        elif subsec_name == 'input':
            index = self._parse_input_subsection(lines, index)
        
        elif subsec_name == 'output':
            index = self._parse_output_subsection(lines, index)
        
        else:
            raise Exception("Wrong subsection name")
        
        return index
            

    def _parse_var_subsection(self, lines, index):
        var_dict = {}

        while not self._is_end_of_lines(lines, index):

            if self._is_new_subsection_head(lines, index):
                break
            
            var_line = lines[index]
            index += 1

            if self._is_empty_line(var_line):
                continue
            
            try:
                var_line = var_line.strip()
                var_name, var_ref_str = var_line.split(' ')
                var_name = var_name.strip()
                var_ref_str = var_ref_str.strip()
                var_ref = int(var_ref_str, 2)
            except Exception:
                raise Exception("Wrong variable reference")

            var_dict[var_name] = var_ref

        self.variables = var_dict
        return index
    
    def _parse_code_subsection(self, lines, index):

        commands_list = []

        while not self._is_end_of_lines(lines, index):

            if self._is_new_subsection_head(lines, index):
                break
            
            command_line = lines[index].strip()
            index += 1

            if self._is_empty_line(command_line):
                continue
            
            soup = command_line.split(' ')
            cmd = soup[0]
            args = soup[1:]
            cmd = cmd.strip()
            if not cmd in all_commands_list:
                raise Exception("Wrong command")
            
            if cmd == 'exec' or cmd == 'execif':
                index, input_vars, output_vars = self._parse_exec_command(
                    lines, index)
                args = [arg.strip() for arg in args]
                
                commands_list.append(
                    {'command': cmd, 
                    'args': args,
                     'func_args': {
                         'input': input_vars, 
                         'output': output_vars}})
                continue

            
            #TODO:Make checking of cmd <-> args correctness
            #TODO:Make chekcing of args <-> self.var matching

            commands_list.append({'command': cmd, 'args': args})
        
        self.commands = commands_list
        return index
    
    def _parse_exec_command(self, lines, index):
        input_vars = []
        output_vars = []

        parsed_lines = 0

        while not self._is_end_of_lines(lines, index):
            
            vars = lines[index].strip()
            index += 1

            if self._is_empty_line(vars):
                continue
            
            splitted_vars = vars.split(' ')
            splitted_vars = [var.strip() for var in splitted_vars]
            if splitted_vars[0] == '.input':
                input_vars = splitted_vars[1:]
                parsed_lines += 1
            elif splitted_vars[0] == '.output':
                output_vars = splitted_vars[1:]
                parsed_lines += 1
            else:
                print('splitted_vars[0]: ', splitted_vars[0])
                raise Exception("Wrong exec argument")
            
            if parsed_lines == 2:
                return index, input_vars, output_vars

        
        raise Exception("Missed exec argument")

    
    def _parse_io_subsection(self, lines, index):

        var_list = []
        while not self._is_end_of_lines(lines, index):

            if self._is_new_subsection_head(lines, index):
                break
            
            var = lines[index].strip()
            index += 1

            if self._is_empty_line(var):
                continue
            
            var_list.append(var)
        
        return index, var_list
    
    def _parse_input_subsection(self, lines, index):
        index, var_list = self._parse_io_subsection(lines, index)
        self.input_variables = var_list
        return index
    
    def _parse_output_subsection(self, lines, index):
        index, var_list = self._parse_io_subsection(lines, index)
        self.output_variables = var_list
        return index
        

        
    
    @staticmethod
    def _is_new_subsection_head(lines, index):

        # end of lines
        if not index < len(lines) :
            return False
        
        line = lines[index].strip()

        # the line is empty
        if not line :
            return False
        
        return line[0] == '.'
    
    @staticmethod
    def _is_end_of_lines(lines, index):
        if not lines:
            return True
        return index >= len(lines)
    
    @staticmethod
    def _is_empty_line(line):
        return not line.strip()


def tail_address(binary_code):
    '''
    this function returns the address of the last segment 
    in binary_code
    '''
    return ((len(binary_code) - 1)*4).to_bytes(4, byteorder='big')

def set_simple_command(binary_code, vars_addresses, command):
    command_addr = binarised_commands_dict[command['command']]
    var_names = command['args']
    binary_code.append(command_addr)
    for var in var_names:
        binary_code.append(vars_addresses[var])    

    
def set_registers(binary_code):
    '''
    This function sets registers in binary_code
    '''
    # add IP
    binary_code.append((0).to_bytes(4, byteorder='big'))

    # add SP
    binary_code.append((0).to_bytes(4, byteorder='big'))

    # add R1
    binary_code.append((0).to_bytes(4, byteorder='big'))

    # add R2
    binary_code.append((0).to_bytes(4, byteorder='big'))

    # add R3
    binary_code.append((4).to_bytes(4, byteorder='big'))

    # add offset
    binary_code.append((4).to_bytes(4, byteorder='big'))

    register_addresses = {
        'IP': (0).to_bytes(4, byteorder='big'),
        'SP': (4).to_bytes(4, byteorder='big'),
        'R1': (8).to_bytes(4, byteorder='big'),
        'R2': (12).to_bytes(4, byteorder='big'),
        'R3': (16).to_bytes(4, byteorder='big'),
        'OFFSET': (20).to_bytes(4, byteorder='big')
    }
    return register_addresses

def set_function_links(binary_code, functions):
    '''
    This function sets empty linkes to functions
    '''
    functions_indices = {}
    for func in functions:

        # do not add main function
        # if func.name == 'main':
        #     continue
        
        binary_code.append((0).to_bytes(4, byteorder='big'))
        functions_indices[func.name] = len(binary_code) - 1
    
    return functions_indices

def set_function_constants(binary_code, function):
    '''
    This function hard-codes constants, used in the function
    '''

    variable_values_addresses = {}

    for item in function.variables.items():
        binary_code.append(item[1].to_bytes(4, byteorder='big'))
        variable_values_addresses[item[0]] = tail_address(binary_code)
    
    return variable_values_addresses

def set_offsets(binary_code, function):
    variable_offsets_addresses = {}

    offset = 0
    for var in reversed(list(function.variables.keys())):
        offset += 4
        binary_code.append(offset.to_bytes(4, byteorder='big'))
        variable_offsets_addresses[var] = tail_address(binary_code)
    
    if function.name == 'main':
        # add offsets only for variables
        return variable_offsets_addresses
    
    # add offsets for input variables
    for var in reversed(function.input_variables):
        offset += 4
        binary_code.append(offset.to_bytes(4, byteorder='big'))
        variable_offsets_addresses[var] = tail_address(binary_code)
    
    # add offsets for output variables
    for var in reversed(function.output_variables):
        offset += 4
        binary_code.append(offset.to_bytes(4, byteorder='big'))
        variable_offsets_addresses[var] = tail_address(binary_code)
    
    # add special ret symbol offset:
    offset += 4
    binary_code.append(offset.to_bytes(4, byteorder='big'))
    variable_offsets_addresses['ret'] = tail_address(binary_code)
    return variable_offsets_addresses

def set_lsp(binary_code, function):
    '''
    This functions sets local stack pointer 
    (in order to not touch SP)
    '''

    binary_code.append((0).to_bytes(4, byteorder='big'))
    return tail_address(binary_code)

def move_stack_to_register(binary_code, var_name, dest, lsp_address, variable_offsets_addresses, start_offset = 'SP'):

    # copy SP to LSP:
    command_addr = binarised_commands_dict["mov"]
    binary_code.append(command_addr)
    binary_code.append(lsp_address)
    binary_code.append(registers_addresses[start_offset]) 

    # decrement var_offset from lsp
    command_addr = binarised_commands_dict["sub"]
    binary_code.append(command_addr)
    binary_code.append(lsp_address)
    binary_code.append(variable_offsets_addresses[var_name])

    # move variable to register 
    command_addr = binarised_commands_dict["rec"]
    binary_code.append(command_addr)
    binary_code.append(registers_addresses[dest])
    binary_code.append(lsp_address)

def move_register_to_stack(binary_code, var_name, source, lsp_address, variable_offsets_addresses, start_offset = 'SP'):

    # copy SP to LSP:
    command_addr = binarised_commands_dict["mov"]
    binary_code.append(command_addr)
    binary_code.append(lsp_address)
    binary_code.append(registers_addresses[start_offset]) 

    # decrement var_offset from lsp
    command_addr = binarised_commands_dict["sub"]
    binary_code.append(command_addr)
    binary_code.append(lsp_address)
    binary_code.append(variable_offsets_addresses[var_name])

    # move the resutl to the stack
    command_addr = binarised_commands_dict['send']
    binary_code.append(command_addr)
    binary_code.append(lsp_address)
    binary_code.append(registers_addresses[source])

    

def set_command(binary_code, command, lsp_address, variable_offsets_addresses):

    if len(command['args']) == 0:
        binary_code.append(binarised_commands_dict[command['command']])
        return

    if len(command['args']) == 2:
        move_stack_to_register(
            binary_code, 
            command["args"][1], 
            'R2', 
            lsp_address, 
            variable_offsets_addresses)

    move_stack_to_register(
        binary_code, 
        command["args"][0], 
        'R1', 
        lsp_address, 
        variable_offsets_addresses)

    # perform the command:
    command_addr = binarised_commands_dict[command['command']]
    binary_code.append(command_addr)
    binary_code.append(registers_addresses['R1'])
    
    if len(command['args']) == 2:
        binary_code.append(registers_addresses['R2'])

    # move the resutl to the stack
    move_register_to_stack(
        binary_code, 
        command["args"][0], 
        'R1', 
        lsp_address, 
        variable_offsets_addresses)


def set_stack_cleaner(binary_code, function, lsp_address, variable_offsets_addresses):
    cleaner_address = (len(binary_code)*4).to_bytes(4, byteorder='big')
    move_stack_to_register(
        binary_code, 
        'ret', 
        'R1', 
        lsp_address, 
        variable_offsets_addresses)
    
    for var in function.variables.keys():
        # move SP back
        command_addr = binarised_commands_dict['sub']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["SP"])
        binary_code.append(registers_addresses['OFFSET'])
    
    command_addr = binarised_commands_dict["jmp"]
    binary_code.append(command_addr)
    binary_code.append(registers_addresses['R1'])
    binary_code.append(cleaner_address)


def validate_function_link(binary_code, function, functions_indices):
    '''
    This function validates link to the function
    after that link to the function points to stack validation
    '''
    binary_code[functions_indices[function.name]] = (len(binary_code)*4).to_bytes(4, byteorder='big')


def set_stack(binary_code, function, variable_values_addresses):
    vars_addresses = variable_values_addresses.copy()
    vars_addresses.update(registers_addresses)
    inc_SP = {
        "command": "add",
        "args": [
            "SP",
            "OFFSET"
        ]
    }

    for var in function.variables.keys():
        # move stack pointer
        set_simple_command(binary_code, vars_addresses, inc_SP)
        add_value = {
            "command": "send",
            "args": [
                "SP",
                var
            ]
        }
        # copy constants to stack
        set_simple_command(binary_code, vars_addresses, add_value)


def set_exec(binary_code, command, lsp_address, variable_offsets_addresses, functions_indices):

    # move current *SP to *R3:
    command_addr = binarised_commands_dict['mov']
    binary_code.append(command_addr)
    binary_code.append(registers_addresses["R3"])
    binary_code.append(registers_addresses['SP'])

    #######################
    ### add return line ###
    #######################

    # add new empty string to stack
    command_addr = binarised_commands_dict['add']
    binary_code.append(command_addr)
    binary_code.append(registers_addresses["SP"])
    binary_code.append(registers_addresses['OFFSET'])

    # command for specifying the address to return
    command_addr = binarised_commands_dict['send']
    binary_code.append(command_addr)
    binary_code.append(registers_addresses["SP"])
    binary_code.append(registers_addresses['SP']) # this string will be changed later

    # here the returned address will be specified
    return_address_index = len(binary_code) - 1

    #############################
    ### add output variables: ###
    #############################

    output_vars = command["func_args"]["output"]
    for output_var in output_vars:

        # add new empty string to stack
        command_addr = binarised_commands_dict['add']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["SP"])
        binary_code.append(registers_addresses['OFFSET'])
    
    ############################
    ### add input variables: ###
    ############################

    input_vars = command["func_args"]["input"]
    
    for input_var in input_vars:
        
        # copy input_var from stack to R1:
        move_stack_to_register(
            binary_code, 
            input_var, 
            'R1', 
            lsp_address, 
            variable_offsets_addresses, 
            start_offset = 'R3')
        
        # add new empty string to stack
        command_addr = binarised_commands_dict['add']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["SP"])
        binary_code.append(registers_addresses['OFFSET'])

        # move value from R1 to *SP
        command_addr = binarised_commands_dict['send']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["SP"])
        binary_code.append(registers_addresses['R1'])

    
    #######################
    ### add jmp command ###
    #######################

    if command['command'] == "exec":

        command_addr = binarised_commands_dict['jmp']
        binary_code.append(command_addr)

        # insert variables, which includes the address of func
        func_name = command["args"][0]
        func_index = functions_indices[func_name]
        func_address = (func_index*4).to_bytes(4, byteorder='big')
        binary_code.append(func_address)

    elif command['command'] == "execif":
        # copy conditional var to the R1
        move_stack_to_register(
            binary_code, 
            command["args"][0], 
            'R1', 
            lsp_address, 
            variable_offsets_addresses, 
            start_offset = 'R3')
        
        command_addr = binarised_commands_dict['jmpif']
        binary_code.append(command_addr)

         # add condition
        binary_code.append(registers_addresses['R1'])

        # insert variables, which includes the address of func
        func_name = command["args"][1]
        func_index = functions_indices[func_name]
        func_address = (func_index*4).to_bytes(4, byteorder='big')
        binary_code.append(func_address)
    
    # specification The address to return 
    addr_to_return = (len(binary_code)*4).to_bytes(4, byteorder="big")
    binary_code[return_address_index] = addr_to_return

    ###################
    ### clean stack ###
    ###################

    for input_var in input_vars:
        # move SP back
        command_addr = binarised_commands_dict['sub']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["SP"])
        binary_code.append(registers_addresses['OFFSET'])
    
    ################################################
    ### Move output variables to their originals ###
    ################################################

    # move current *SP to *R3:
    command_addr = binarised_commands_dict['mov']
    binary_code.append(command_addr)
    binary_code.append(registers_addresses["R3"])
    binary_code.append(registers_addresses['SP'])

    # move R3 to the start of own stack part
    for output_var in output_vars: 
        command_addr = binarised_commands_dict['sub']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["R3"])
        binary_code.append(registers_addresses['OFFSET'])
    
    # move R3 back (return address pass)
    command_addr = binarised_commands_dict['sub']
    binary_code.append(command_addr)
    binary_code.append(registers_addresses["R3"])
    binary_code.append(registers_addresses['OFFSET'])
    
    for output_var in reversed(output_vars):

        # move original variable to register
        move_stack_to_register(
            binary_code, 
            output_var, 
            'R1', 
            lsp_address, 
            variable_offsets_addresses, 
            start_offset = 'R3')
        
        # move new variable to register
        command_addr = binarised_commands_dict['mov']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["R2"])
        binary_code.append(registers_addresses['SP'])

        # move R2 -> R1
        command_addr = binarised_commands_dict['mov']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["R1"])
        binary_code.append(registers_addresses['R2'])

        # copy R1 to variable
        move_register_to_stack(
            binary_code, 
            output_var, 
            'R1', 
            lsp_address, 
            variable_offsets_addresses, 
            start_offset='R3')

        # move SP back
        command_addr = binarised_commands_dict['sub']
        binary_code.append(command_addr)
        binary_code.append(registers_addresses["SP"])
        binary_code.append(registers_addresses['OFFSET'])
    
    # pass return value
    command_addr = binarised_commands_dict['sub']
    binary_code.append(command_addr)
    binary_code.append(registers_addresses["SP"])
    binary_code.append(registers_addresses['OFFSET'])

def set_ret(binary_code, command, lsp_address, variable_offsets_addresses, own_func_index):
    if command['command'] == 'ret':
        # just jump to stack cleaner
        command_addr = binarised_commands_dict['jmp']
        binary_code.append(command_addr)

        # add jmp_addr
        own_func_index -= 1
        jmp_addr = (own_func_index*4).to_bytes(4, byteorder='big')
        binary_code.append(jmp_addr)
    
    if command['command'] == 'retif':
        # move condition variable to R1 register:
        move_stack_to_register(
            binary_code, 
            command['args'][0],
            'R1', 
            lsp_address, 
            variable_offsets_addresses, 
            start_offset = 'SP')
        
        command_addr = binarised_commands_dict['jmpif']
        binary_code.append(command_addr)

        # add condition variable:
        binary_code.append(registers_addresses['R1'])

        # add jmp_addr
        own_func_index -= 1
        jmp_addr = (own_func_index*4).to_bytes(4, byteorder='big')
        binary_code.append(jmp_addr)
        



def set_function(binary_code, func, functions_indices):

    # set constants
    variable_values_addresses = set_function_constants(binary_code, func)

    # set offsets
    variable_offsets_addresses = set_offsets(binary_code, func)

    # set lsp
    lsp_address = set_lsp(binary_code, func)

    if not func.name == 'main':
        # set stack cleaner
        set_stack_cleaner(binary_code, func, lsp_address, variable_offsets_addresses)

    # validate function link
    validate_function_link(binary_code, func, functions_indices)

    # set stack 
    set_stack(binary_code, func, variable_values_addresses)

    for command in func.commands:
        if command['command'] in ['exec', 'execif']:
            set_exec(
                binary_code, 
                command, 
                lsp_address, 
                variable_offsets_addresses, 
                functions_indices)
        
        elif command['command'] in ['ret', 'retif']:
            set_ret(
                binary_code, 
                command,
                lsp_address, 
                variable_offsets_addresses, 
                functions_indices[func.name])
        else:
            set_command(
                binary_code, 
                command, 
                lsp_address, 
                variable_offsets_addresses)

def set_instraction_pointer(binary_code, functions_indices):
    binary_code[0] = (functions_indices['main']*4).to_bytes(4, byteorder='big')

def set_stack_pointer(binary_code):
    binary_code[1] = (len(binary_code)*4).to_bytes(4, byteorder='big')
        

def program_parser(lines):
    
    # here we determine sections with the code:
    new_functions_indices = []
    for i in range(len(lines)):
        if lines[i].strip() and lines[i].strip()[0] == '@':
            new_functions_indices.append(i)
    
    new_functions_indices.append(len(lines))

    functions = []
    for i in range(len(new_functions_indices) - 1):
        lb = new_functions_indices[i]
        rb = new_functions_indices[i + 1] - 1

        # extract lines with the current function
        func_lines = lines[lb:rb]
        functions.append(Function(func_lines))
    
    return functions



parser = argparse.ArgumentParser(
    description=
    'This script parses the program, written on the assembler to bynary code')

parser.add_argument(
    '--source', 
    '-s', 
    required=True, 
    help="source file to parse", 
    dest="source_name")

parser.add_argument(
    '--name', 
    '-n', 
    required=True, 
    help="name of binary file", 
    dest="target_name")

args = parser.parse_args()
source_name = args.source_name
target_name = args.target_name

with open(source_name, 'r') as source:
    program = source.readlines()

functions = program_parser(program)


# the obtained code will be stored here
binary_code = []

# set registers
set_registers(binary_code)

# set function indices
functions_indices = set_function_links(binary_code, functions)

try:
    main_function = list(filter(lambda x: x.name=='main', functions))[0]
except Exception:
    Exception("There is not main function in the program")

# set main function:
set_function(binary_code, main_function, functions_indices)


for func in [func for func in functions if func.name != 'main']:
    set_function(binary_code, func, functions_indices)

set_instraction_pointer(binary_code, functions_indices)
set_stack_pointer(binary_code)

if not os.path.exists('./bin'):
    os.makedirs('./bin')

target_path = './bin/{}.binary'.format(target_name)
with open(target_path, 'wb') as f:
    for item in binary_code:
        f.write(item)


#functions[0].to_json('main.json')
# functions[1].to_json('fibbonachi.json')


