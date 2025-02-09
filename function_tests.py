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

def display_memory(memory:dict[str, int]):

    # Header
    print("-" * 49)
    print("Memory address   Values")

    for address, value in memory.items():

        if type(value) is str:
            print(f"{address:#010x}\t {value}")

        else:
            print(f"{address:#010x}\t {value:#010x}")
    
    print()

memory = memory_text_allocation()
memory = memory_data_allocation(memory)
display_memory(memory)
