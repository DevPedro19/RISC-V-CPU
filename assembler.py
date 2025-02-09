# Ideas

#Sign-extend : binary_number = sign_extend * (bits - len(binary_number)) + binary_number

def binary_converter(num: int, bits: int) -> str:
    # It's a feature not a bug (positivo - unsigned, negativo - signed) - fantástico wtf
    """
    Converts decimal number into a binary number with n bits
    """
    # Verifies if the representation of the number is valid
    assert -2**bits <= num <= 2**bits - 1

    if num == -2**bits:
        return "1" + "0" * (bits - 1)
    
    # If the number is negative
    complement = False
    if num < 0:
        complement = True
        num = -num
    
    # Division algorithm to get the bits
    binary_number = ""
    if num != 0:
        while num != 1:
            binary_number = str(num % 2) + binary_number
            num = num // 2
    binary_number = str(num % 2) + binary_number
    binary_number = "0" * (bits - len(binary_number)) + binary_number

    # Converts the number in a list, so we can obtain the complement
    binary_number = list(binary_number)

    # If the number is negative we have to find the complement
    if complement:
        switch = False
        for index in range(len(binary_number) - 1, -1, -1):
            bit = binary_number[index]
            if switch:
                binary_number[index] = "1" if bit == "0" else "0"
            elif bit == "1":
                switch = True
          
    return "".join(binary_number)

def x_remover(field:str) -> str:
    """
    Removes the string x in the register string of the instruction
    """
    register = ""
    is_register = False
    for letter in field:
        if is_register:
            if letter == ")":
                return register
            register += letter
        elif letter == "x":
            is_register = True
    raise ValueError("Invalid field")

def offset_finder(field:str) -> str:
    """
    Removes the string value of the offset in the instruction
    """
    offset = ""
    for letter in field:
        if letter == "(":
            return offset
        offset += letter
    raise ValueError("Invalid field")


def offset_generator(label:str, labels:dict[str, int], line_index:int) -> int:
    """
    Generates the offset for branch jumps to existing labels
    """
    target_index = labels[label]
    offset = target_index - line_index
    return offset

def label_finder() -> dict[str, int]:
    """
    Analyzes the file with the code and puts every label in a dict containing the name and the line
    """
    ret_labels = {}
    line_index = 0
    with open("riscv_code.txt","r") as riscv_code:
        for line in riscv_code.readlines():
            if ":" in line:
                current_label = line.split()[0][:-1]
                ret_labels[current_label] = line_index
            line_index += 4
    return ret_labels

def decoder(instruction:str, labels:dict[str, int], line_index:int) -> str: 
    """
    Transforms instruction in binary code
    """
    fields = [inst.strip(",") for inst in instruction.split()] # gets fields for each instruction
    # This dictionary holds the respective values of funct3 and funct7 of a certain instruction
    inst_op_funct = {
        "add": ("0110011","000", "0000000"),
        "sub": ("0110011", "000", "0100000"),
        "and": ("0110011", "111", "0000000"),
        "or": ("0110011", "110", "0000000"),
        "lw": ("0000011", "010"),
        "sw": ("0100011", "010"),
        "beq": ("1100011", "000")
    }
    
    # Checks if the first field is a label
    if fields[0][-1] == ":":
        # Adds one to the index if first field is a label
        inc = 1
    else:
        # If not keeps the indexes unchanged
        inc = 0
    
    operation = fields[0 + inc]

    assert operation in inst_op_funct.keys()
    
    opcode, funct3 = (inst_op_funct[operation][0], inst_op_funct[operation][1])
    
    #identify the instruction's type
    if opcode == "0110011": #R-Type add t0, t1, t2
        funct7 = inst_op_funct[operation][2]
        rd = binary_converter(int(fields[1+inc][1:]), 5)
        rs1 = binary_converter(int(fields[2+inc][1:]), 5)
        rs2 = binary_converter(int(fields[3+inc][1:]), 5)
        binary_code = funct7 + rs2 + rs1 + funct3 + rd + opcode

    elif opcode == "0000011": # lw x1, 4(x5)
        rd = binary_converter(int(fields[1+inc][1:]), 5)
        rs1 = binary_converter(int(x_remover(fields[2+inc])), 5)
        imm = binary_converter(int(offset_finder(fields[2+inc])), 12)
        binary_code = imm + rs1 + funct3 + rd + opcode
        
    elif opcode == "0100011": # sw x1, 8(x6)
        rs1 = binary_converter(int(x_remover(fields[2+inc])), 5)
        rs2 = binary_converter(int(fields[1+inc][1:]), 5)
        imm = binary_converter(int(offset_finder(fields[2+inc])), 12)
        binary_code = imm[:7] + rs2 + rs1 + funct3 + imm[7:] + opcode

    else: # beq x11, x0, 25
        rs1 = binary_converter(int(fields[1+inc][1:]), 5)
        rs2 = binary_converter(int(fields[2+inc][1:]), 5)
        try:
            int(fields[3+inc])
        except ValueError:
            label = fields[3+inc]
            imm = offset_generator(label, labels, line_index)
            imm = binary_converter(imm, 13)
        else:
            imm = binary_converter(int(fields[3+inc]), 13)
        binary_code = imm[0] + imm[2:8] + rs2 + rs1 + funct3 + imm[8:12] + imm[1] + opcode

    return binary_code


def main() -> int:
    # Searches the lables in the file
    labels = label_finder()
    # Creates a file called machine code that has the binary code of each instruction 32 bits
    with open("riscv_code.txt", "r") as riscv_code, open("machine_code.txt", "a") as machine_code:
        machine_code.truncate(0) # truncate the file until it has 0 bytes
        line_index = 0
        for line in riscv_code:
            line_index += 4
            machine_code.write(decoder(line.strip("\n"), labels, line_index) + "\n")
    # The assembler specifies the intial value of the memory area
    pc = 0x00400000
    return pc
main()
