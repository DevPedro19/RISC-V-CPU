import assembler

def register_file_generator() -> dict[str, int]:
    return {
        "00000": 0x00000000,
        "00001": 0x00000000,
        "00010": 0x7fffeffc,
        "00011": 0x10008000,
        "00100": 0x00000000,
        "00101": 0x10010000,
        "00110": 0x00000004,
        "00111": 0x00000000,
        "01000": 0x00000006,
        "01001": 0x00000001,
        "01010": 0x00000000,
        "01011": 0x00000000,
        "01100": 0x00000000,
        "01101": 0x00000000,
        "01110": 0x00000000,
        "01111": 0x00000000,
        "10000": 0x00000000,
        "10001": 0x00000000,
        "10010": 0x00000000,
        "10011": 0x00000000,
        "10100": 0x00000000,
        "10101": 0x00000000,
        "10110": 0x00000000,
        "10111": 0x00000000,
        "11000": 0x00000000,
        "11001": 0x00000000,
        "11010": 0x00000000,
        "11011": 0x00000000,
        "11100": 0x00000000,
        "11101": 0x00000000,
        "11110": 0x00000000,
        "11111": 0x00000000
    }


def memory_text_allocation() -> dict[int, str]:
    """
    Populates the text memory, respresented as a dict, with the address and the instruction
    """
    ret_memory = {}
    with open("machine_code.txt", "r") as machine_code:
        current_address = 0x00400000
        for instruction in machine_code:
            ret_memory[current_address] = instruction.strip("\n")
            current_address += 4
    return ret_memory


def memory_data_allocation(memory:dict[int, str]) -> dict:
    """
    Populates the data memory, respresented as a dict, with the address and the value
    """
    ret_memory = memory
    current_address = 0x10010000
    for _ in range(256): # 1024byte / 1Mb memory
        ret_memory[current_address] = 0x00000000
        current_address += 4
    return ret_memory


def control_unit(opcode:str) -> tuple[str, ...]:
    """
    Creates the control signs for a given operation
    """
    if opcode == "0000011": # I-type, lw
        Branch = "0"
        MemRead = "1"
        MemtoReg = "1"
        ALUOp = "00"
        MemWrite = "0"
        ALUSrc = "1"
        RegWrite = "1"

    elif opcode == "0100011":  # S-type, sw
        Branch = "0"
        MemRead = "0"
        MemtoReg = "0"
        ALUOp = "00"
        MemWrite = "1"
        ALUSrc = "1"
        RegWrite = "0"
        
    elif opcode == "1100011": # B-type
        Branch = "1"
        MemRead = "0"
        MemtoReg = "0"
        ALUOp = "01"
        MemWrite = "0"
        ALUSrc = "0"
        RegWrite = "0"
        
    else: # R-Type
        Branch = "0"
        MemRead = "0"
        MemtoReg = "0"
        ALUOp = "10"
        MemWrite = "0"
        ALUSrc = "0"
        RegWrite = "1"

    return Branch, MemRead, MemtoReg, ALUOp, MemWrite, ALUSrc, RegWrite


def pc_adder(pc:int) -> int:
    """
    Adds 4 to de PC (program counter)
    """
    return pc + 4


def instruction_memory(pc:int, memory:dict) -> str:
    """
    Gets the instruction which corresponds to the current PC address
    """
    return memory[pc]


def imm_gen(instruction:str, opcode:str) -> str:
    """
    Generates the immediate based on the instruction    
    """
    if opcode == "0000011": # I-type
        imm = instruction[:12]
        if imm[0] == "1":  #negative
            imm = "1" * (32-len(imm)) + imm
        else: #positive
            imm = "0" * (32-len(imm)) + imm
            
    elif opcode == "0100011": # S-type
        imm = instruction[:7] + instruction[20:25]
        if imm[0] == "1":  #negative
            imm = "1" * (32-len(imm)) + imm
        else: #positive
            imm = "0" * (32-len(imm)) + imm
            
    elif opcode == "1100011":
        # B-type
        imm = instruction[0] + instruction[24] + instruction[1:7] + instruction[20:24] + "0"
        if imm[0] == "1":  #negative
            imm = "1" * (32-len(imm)) + imm
        else: #positive
            imm = "0" * (32-len(imm)) + imm
    else:
        return "0"
    
    return imm


def twos_complement_reader(num:str) -> int:
    first_bit = int(num[0])
    exp = len(num)-1
    res = -2 ** exp * first_bit
    for bit in num[1:]:
        exp -= 1
        res += 2**exp * int(bit)
    return res    


def branch_adder(pc:int, imm:int) -> int:
    """
    Adds the immediate in the branch instruction and adds it do PC
    """
    return pc + imm + 4


def ALU_control(funct7:str, funct3:str, ALUOp:str) -> str:
    if ALUOp == "00":
        return "add"
    
    elif ALUOp == "01":
        return "subtract"
    
    elif ALUOp == "10":
        if funct7 == "0000000":
            if funct3 == "000":
                return "add"
            elif funct3 == "111":
                return "and"
            elif funct3 == "110":
                return "or"
        else:
                return "subtract"
        

def registers(rs1:str, rs2:str, rd:str, write_data:None, RegWrite:str, register_file:dict[str, int]):
    read_data_1 = register_file[rs1]
    read_data_2 = register_file[rs2]
    if RegWrite == "1" and write_data != None:
        register_file[rd] = write_data
        return register_file
    return read_data_1, read_data_2


def ALUSrc_MUX(ALUSrc:str, read_data_2:int, imm:int) -> int:
    if ALUSrc == "1":
        return imm
    return read_data_2


def ALU(op:str, read_data_1:int, second_op:int) -> tuple[int, str]:

    if op == "add":
        res = read_data_1 + second_op
        ALU_result = res
    
    elif op == "subtract":
        res = read_data_1 - second_op
        ALU_result = res

    else:
        res = ""
        read_data_1_bin = assembler.binary_converter(read_data_1, 32)
        read_data_2_bin = assembler.binary_converter(second_op, 32)
        if op == "and":
            for index, bit in enumerate(read_data_1_bin):
                res += AND(bit, read_data_2_bin[index])
        else:
            for index, bit in enumerate(read_data_1_bin):
                res += OR(bit, read_data_2_bin[index])
        ALU_result = twos_complement_reader(res)
    
    Zero = "0"
    if read_data_1 == second_op:
        Zero = "1"
        
    return ALU_result, Zero


def AND(x:str, y:str) -> str:
    if x == "1" and y == "1":
        return "1"
    return "0"


def OR(x:str, y:str) -> str:
    if x == "1" or y == "1":
        return "1"
    return "0"


def data_memory(address:int, write_data:int, MemWrite:str, MemRead:str, memory: dict) -> None | int:
    if MemRead == "1":
        read_data = memory[address]
    else:
        read_data = None

    if MemWrite == "1":
        memory[address] = write_data
        
    return read_data


def MemtoReg_MUX(read_data: None | int, ALU_result:int, MemtoReg:str) -> None | int:
    if MemtoReg == "0":
        return ALU_result
    elif read_data != None:
        return read_data
    return None


def PCSrc_MUX(res_pc_adder:int, res_branch_adder:int, Branch:str, Zero:str) -> int:
    
    if AND(Branch, Zero) == "1":
        PCScr = "1"
    else:
        PCScr = "0"

    if PCScr == "0":
        return res_pc_adder
    else:
        return res_branch_adder


def display_register_file_pre(register_file:dict[str, int]):
    """
    Displays register file before execution
    """
    # Header
    print("-" * 26)
    print("Register Name   Values")

    for register_bin, value in register_file.items():
        # Converts the binary string into a decimal string, ex "01000" -> 8
        register_decimal = str(int(register_bin, 2))

        # Creates the name of the register, ex: x8
        register_name = "x" + register_decimal

        # Format string -> align the register name to the left and display registers as hexadecimal 

        print(f"{register_name:<4}\t\t{value:#010x}")
    
    print()


def display_memory_pre(memory:dict):
    """
    Displays memory before execution
    """

    # Header
    print("-" * 49)
    print("Memory address   Values")

    for address, value in memory.items():

        if type(value) is str:
            print(f"{address:#010x}\t {value}")

        else:
            print(f"{address:#010x}\t {value:#010x}")
    
    print()


def display_register_file_post(start_register_file:dict[str, int], register_file:dict[str, int]):
    """
    Displays register after before execution
    """
    # Header
    print("-" * 26)
    print("Register Name   Values")

    for register_bin, value in register_file.items():
        # Converts the binary string into a decimal string, ex "01000" -> 8
        register_decimal = str(int(register_bin, 2))

        # Creates the name of the register, ex: x8
        register_name = "x" + register_decimal

        # Format string -> align the register name to the left and display registers as hexadecimal 

        if value == start_register_file[register_bin]:
            print(f"{register_name:<4}\t\t{value:#010x}")
        else:
            print(f"{'\033[33m'}{register_name:<4}{'\033[0m'}\t\t{'\033[33m'}{value:#010x}{'\033[0m'}")  

    
    print()


def display_memory_post(start_memory:dict, memory:dict):
    """
    Displays memory after execution
    """

    # Header
    print("-" * 49)
    print("Memory address   Values")

    for address, value in memory.items():

        if type(value) is str:
            if value == start_memory[address]:
                print(f"{address:#010x}\t {value}")
            else:
                print(f"{'\033[33m'}{address:#010x}{'\033[0m'}\t {'\033[33m'}{value}{'\033[0m'}")

        else:
            if value == start_memory[address]:
                print(f"{address:#010x}\t {value}")
            else:
                print(f"{'\033[33m'}{address:#010x}{'\033[0m'}\t {'\033[33m'}{value:#010x}{'\033[0m'}")
    
    print()


def main():
    pc = assembler.main()
    # Instruction memory
    memory = memory_text_allocation()
    memory = memory_data_allocation(memory)


    register_file = register_file_generator()

    start_register_file = register_file.copy()

    start_memory = memory.copy()

    print("Initial Register File")
    display_register_file_pre(register_file)

    print("Initial Memory")
    display_memory_pre(memory)

    #display_memory

    while pc in memory.keys():
        #pc adder
        res_pc_adder = pc_adder(pc)

        # Gets the instruction
        instruction = instruction_memory(pc, memory)

        #Slices the instruction
        opcode = instruction[25:]
        funct7 = instruction[:7]
        funct3 = instruction[17:20]
        rs1 = instruction[12:17]
        rs2 = instruction[7:12]
        rd = instruction[20:25]

        # Signals from the control unit
        Branch, MemRead, MemtoReg, ALUOp, MemWrite, ALUSrc, RegWrite = control_unit(opcode)

        # ImmGen unit
        imm = imm_gen(instruction, opcode)

        # Branch_adder
        imm = twos_complement_reader(imm)
        res_branch_adder = branch_adder(pc, imm)

        # ALU_Control
        ALU_operation = ALU_control(funct7, funct3, ALUOp)

        # Registers
        read_data_1, read_data_2 = registers(rs1, rs2, rd, None, RegWrite, register_file)

        #ALUScr_MUX
        second_op = ALUSrc_MUX(ALUSrc, read_data_2, imm)

        #ALU
        ALU_result, Zero = ALU(ALU_operation, read_data_1, second_op)

        #Data_Memory
        read_data = data_memory(ALU_result, read_data_2, MemWrite, MemRead, memory)

        #MemToReg_MUX
        write_data = MemtoReg_MUX(read_data, ALU_result, MemtoReg)

        #registers
        if RegWrite == "1":
            register_file = registers(rs1, rs2, rd, write_data, RegWrite, register_file)

        # PCSrc_MUX
        pc = PCSrc_MUX(res_pc_adder, res_branch_adder, Branch, Zero)
    
    print("Final Register File")
    display_register_file_post(start_register_file, register_file)

    print("Final Memory")
    display_memory_post(start_memory, memory)
    

main()