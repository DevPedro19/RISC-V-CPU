# RISC-V-CPU
Basic implementation of a single cycle RISC-V CPU in Python

# How it started
After the end of the first year's first semester at FEUP, studying Computer Science (L.EIC - Licenciatura em Engenharia Informática e Computação), me and other two friends decided to code a simple implementation of a single-cycle CPU, that supports some of the instructions of the RISC-V ISA (Instruction Set Architecture), since it was, for us, the most interesting topic of one of our courses, FSC (Fundamentos de Sistemas Computacionais).

# How does it actually work
In the repository there is a file called riscv_code.txt: that's where you, the user, writes some code with the supported instructions, that we will explicit later. Then, the code will be assembled ... explain what the assembler does... . After that, the file cpu.py will read from machine_code.txt the instructions in binary, load them to the memory, and executed following a single-cycle cpu architecture. This file will print the values of the register file and the memory, before and after the execution.

# How to use it
**1-** Clone the repository
```
git clone https://github.com/DevPedro19/RISC-V-CPU.git
```

