"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[7] = 0xf4
        self.halted = False

    def stackMemory(self):
        stackSpace = len(self.ram)
        self.ram += [0] * stackSpace
        return self.ram

    def ram_read(self, address):
        """accept the address to read and return the value stored there"""
        return self.ram[address]

    def ram_write(self, address, value):
        """accept a value to write, and the address to write it to"""
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print('You must have two arguments')
            sys.exit(1)
        try:
            with open(sys.argv[1], 'r') as file:
                # print('in load')
                for line in file:
                    # print(line) 
                    array_split = line.split('#')
                    nums = array_split[0]
                    try:
                        num = int(nums, 2)
                        self.ram[address] = num
                        # print(self.ram[address])
                        address += 1 
                    except:
                        continue
        except:
            print("File not found")
            sys.exit(1)


    def alu(self, op, reg_a, reg_b):
        """ALU operations.""" 

        if op == "ADD": # 160
            # print(self.reg[reg_a])
            self.reg[reg_a] += self.reg[reg_b]
            return self.reg[reg_a]
        elif op == 162:
            self.reg[reg_a] *= self.reg[reg_b]
            

        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # Instruction Register, contains a copy of the currently executing instruction
        # if at 160

        LDI = 130
        HLT = 1
        PRN = 71
        MULT = 162
        PUSH = 69
        POP = 70
        CALL = 80
        RET = 17
        ADD = 160
        CMP = 167
        JEQ = 85
        JNE = 86
        JMP = 84

        equalFlag = 0
        lessFlag = 0
        greatFlag = 0

        memory = self.stackMemory() # create memory for a stack
        SP = 7
        self.reg[SP] = len(memory) - 1

        while not self.halted:

            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR == LDI:
                self.reg[operand_a] = operand_b
                # print(f'seting self.reg[{operand_a}] to {operand_b}')
                # print('the register values are, ', self.reg)
                self.pc += 3
            elif IR == HLT:
                self.halted = True
                sys.exit(1)
            elif IR == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif IR == PUSH:
                self.reg[SP] -= 1
                registerValue = self.ram[self.pc + 1]
                valueInRegister = self.reg[registerValue]
                self.ram[self.reg[SP]] = valueInRegister
                self.pc += 2
            elif IR == POP:
                topValueInStack = self.ram[self.reg[SP]]
                registerToStoreItIn = self.ram[self.pc + 1] 
                self.reg[registerToStoreItIn] = topValueInStack
                self.reg[SP] += 1
                self.pc += 2
            elif IR == MULT:
                self.alu(IR,operand_a,operand_b)
                self.pc += 3
            elif IR == CALL:
                ret_addr = self.pc + 2
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = ret_addr

                addrToGet = self.ram[self.pc + 1]
                # print(f'Calling reg[{addrToGet}]')
                self.pc = self.reg[addrToGet]
                # print(f'PC is at ', self.pc)

            elif IR == RET:
                # print('In Ret')
                ret_addr = self.ram[self.reg[SP]]
                self.reg[SP] += 1

                self.pc = ret_addr

            elif IR == ADD:
                # op = 'ADD'
                self.alu(op, 0, 0)
                self.pc += 3

            elif IR == CMP:
                # print('In CMP')
                registerA = self.reg[operand_a]
                registerB = self.reg[operand_b]
                if registerA == registerB:
                    # set the Equal E flag to 1, otherwise set it to 0.
                    equalFlag = 1
                    self.pc += 3
                elif registerA < registerB:
                    # set the Less-than L flag to 1, otherwise set it to 0.
                    lessFlag = 1
                    self.pc += 3
                elif registerA > registerB:
                    # set the Greater-than G flag to 1, otherwise set it to 0.
                    greatFlag = 1
                    self.pc += 3
            elif IR == JEQ:
                # If equal flag is set (true)
                # print('JEQ')
                # print(f'registerA {registerA} == registerB {registerB}')
                if equalFlag:
                    # jump to the address stored in the given register.
                    self.jumpToRegister()
                else:
                    # if not go to the next instruction
                    self.pc += 2
            elif IR == JNE:
                # If E flag is clear (false, 0)
                # print('JNE')
                # print(f'registerA {registerA} !== registerB {registerB}')
                if equalFlag == 0:
                    # jump to the address stored in the given register.
                    self.jumpToRegister()
                else:
                    self.pc += 2
            elif IR == JMP:
                self.jumpToRegister()

    def jumpToRegister(self):
        registerToJumpTo = self.pc + 1
        regIndex = self.ram[registerToJumpTo]
        # print('Jumping to register, ', regIndex)
        self.pc = self.reg[regIndex]
        # print('self.pc = ', self.pc)