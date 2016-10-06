class FileOpcode:
    def __init__(self, module, source):
        self.module = module
        self.source = source
        self.opcodes = {}

    def add(self, codeobj_id, offset, instruction):
        self.opcodes[codeobj_id, offset] = WrappedOpcode(instruction)

    def visit(self, codeobj_id, offset, instruction):
        key = codeobj_id, offset
        if key not in self.opcodes:
            return

        if self.opcodes[key].instruction == instruction:
            self.opcodes[key].visit()
            return

        print(self.opcodes[key].instruction)
        print(instruction)
        raise Exception(
            'Unexpected instruction {} {} {}'.format(
                codeobj_id, offset, str(instruction))
        )


class WrappedOpcode:
    def __init__(self, instruction):
        self.instruction = instruction
        self.visited = False

    def __getattr__(self, item):
        return getattr(self.instruction, item)

    def visit(self):
        self.visited = True

    def __str__(self):
        return '{} {}'.format(
            '[visited]' if self.visited else '[missing]', self.instruction
        )
