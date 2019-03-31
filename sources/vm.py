import argparse

stack_size = 1024 # bytes

def get_command_index(code_list):
    command_index = 0
    command_index = command_index.from_bytes(code_list[0], byteorder='big')
    assert command_index % 4 == 0
    return command_index//4

def get_command(code_list):
    return code_list[get_command_index(code_list)]

def get_index_from_bin(bin):
    index = 0
    index = index.from_bytes(bin, byteorder='big')
    assert index % 4 == 0
    return index//4

def move_IP(code_list, offset):
    '''
    offset is number of elements of code_list to move IP
    '''
    curr_index = get_command_index(code_list)
    curr_index += offset
    code_list[0] = (curr_index*4).to_bytes(4, byteorder='big')

def get_value_index(code_list, var_index):
    operand = code_list[var_index]
    return get_index_from_bin(operand)

def get_ptr_value_index(code_list, var_index):
    return get_value_index(
        code_list, 
        get_value_index(code_list, var_index))


def mov_handler(code_list):
    cmd_index = get_command_index(code_list)
    first_index = get_value_index(code_list, cmd_index + 1)
    second_index = get_value_index(code_list, cmd_index + 2)
    code_list[first_index] = code_list[second_index]
    # move IP
    move_IP(code_list, 3)
    return True

def send_handler(code_list):
    cmd_index = get_command_index(code_list)
    first_index = get_ptr_value_index(code_list, cmd_index + 1)
    second_index = get_value_index(code_list, cmd_index + 2)
    code_list[first_index] = code_list[second_index]
    # move IP
    move_IP(code_list, 3)
    return True

def change_command(code_list, sign=1):
    cmd_index = get_command_index(code_list)
    first_index = get_value_index(code_list, cmd_index + 1)
    second_index = get_value_index(code_list, cmd_index + 2)
    first_val = 0
    first_val = first_val.from_bytes(code_list[first_index], byteorder='big')
    second_val = 0
    second_val = second_val.from_bytes(code_list[second_index], byteorder='big')
    first_val += second_val*sign
    result = first_val.to_bytes(4, byteorder='big')
    code_list[first_index] = result
    # move IP
    move_IP(code_list, 3)  
    return True  

def add_handler(code_list):
    return change_command(code_list, 1)

def sub_handler(code_list):
    return change_command(code_list, -1)

def in_handler(code_list):
    cmd_index = get_command_index(code_list)
    index = get_value_index(code_list, cmd_index + 1)
    input_val = int(input())
    result = input_val.to_bytes(4, byteorder='big')
    code_list[index] = result
    # move IP
    move_IP(code_list, 2)  
    return True  

def out_handler(code_list):
    cmd_index = get_command_index(code_list)
    index = get_value_index(code_list, cmd_index + 1)
    val = 0
    val = val.from_bytes(code_list[index], byteorder='big')
    print(val)
    # move IP
    move_IP(code_list, 2)  
    return True  

def jmp_handler(code_list):
    cmd_index = get_command_index(code_list)
    index = get_ptr_value_index(code_list, cmd_index + 1)
    code_list[0] = (index*4).to_bytes(4, byteorder='big')
    return True

def rec_handler(code_list):
    cmd_index = get_command_index(code_list)
    first_index = get_value_index(code_list, cmd_index + 1)
    second_index = get_ptr_value_index(code_list, cmd_index + 2)
    code_list[first_index] = code_list[second_index]
    # move IP
    move_IP(code_list, 3)
    return True

def jmpif_handler(code_list):
    cmd_index = get_command_index(code_list)
    cond_index = get_value_index(code_list, cmd_index + 1)
    jmp_index = get_ptr_value_index(code_list, cmd_index + 2)
    cond_val = 0
    cond_val = cond_val.from_bytes(code_list[cond_index], byteorder='big')
    if not cond_val:
        code_list[0] = (jmp_index*4).to_bytes(4, byteorder='big')
    else:
        move_IP(code_list, 3)
    return True

def term_handler(code_list):
    return False


handlers = {
    b'\x00\x00\x00\x00' : mov_handler,
    b'\x00\x00\x00\x10' : send_handler,
    b'\x00\x00\x00\x01': add_handler,
    b'\x00\x00\x00\x02': sub_handler,
    b'\x00\x00\x00\x03' : in_handler,
    b'\x00\x00\x00\x04': out_handler,
    b'\x00\x00\x00\x05' : jmp_handler,
    b'\x00\x00\x00\x50' : rec_handler,
    b'\x00\x00\x00\x06' : jmpif_handler,
    b'\xFF\xFF\xFF\xFF' : term_handler
}

def execute_command(code_list):
    command = get_command(code_list)
    assert command in handlers.keys()
    return handlers[command](code_list)

def add_stack(binary_code):
    stack = b'\x00'*stack_size
    binary_code += stack
    return binary_code

def make_code_list(binary_code):
    code_list = [binary_code[4*i:4*(i+1)] for i in range(len(binary_code) // 4)]
    return code_list



parser = argparse.ArgumentParser(
    description=
    'This script emulates Von Neuman virtual machine')

parser.add_argument(
    'source_name',
    help="source file to execute on VM")

args = parser.parse_args()
source_name = args.source_name

with open(source_name, 'rb') as sf:
    binary_code = sf.read()

binary_code = add_stack(binary_code)
code_list = make_code_list(binary_code)

while execute_command(code_list):
    pass
