import sys
import argparse
import json

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
            
            #TODO:Make checking of cmd <-> args correctness
            #TODO:Make chekcing of args <-> self.var matching

            commands_list.append([cmd, args])
        
        self.commands = commands_list
        return index
    
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
functions[0].to_json('main.json')
functions[1].to_json('fibbonachi.json')


