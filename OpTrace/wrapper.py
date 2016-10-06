import opcode
import dis

from types import CodeType
from functools import partial

class Wrapper:
    AGR_OP_LEN = 3

    def __init__(self, trace_func, mark_func):
        self.visit = trace_func
        self.mark = mark_func
        self.current_code_object_id = 0

    def print_codeobj_attr(self, obj):
        print('---------------> ', obj)
        for key in dir(obj):
            if key.startswith('__'):
                continue
            try:
                print('{}: {}'.format(key, object.__getattribute__(obj, key)))
            except:
                print('{} : ???'.format(key))
        print('-' * 20)

    def print_codeobj(self, codeobj):
        dis.dis(codeobj)
        self.print_codeobj_attr(codeobj)
        print('!'*80)
        for st in dis.get_instructions(codeobj):
            print(st.offset, st, sep=' -> ')
        print('!' * 80)
        for code in codeobj.co_code:
            print(opcode.opname[code])

    @property
    def TRACE_CODE_LEN(self):
        return len(list(self.make_trace(0)))

    def make_args(self, value):
        yield from reversed(divmod(value, 256))

    def make_trace(self, constant_index):
        yield opcode.opmap['LOAD_CONST']
        yield from self.make_args(constant_index)
        yield opcode.opmap['CALL_FUNCTION']
        yield from [0, 0] # trace_func parameters set by closure in lambda
        yield opcode.opmap['POP_TOP']

    def calculate_offset(self, old_offset, code):
        new_position = self.TRACE_CODE_LEN-1
        skip_args_counter = 0
        for op in code[:old_offset + 1]:
            if skip_args_counter:
                skip_args_counter -= 1
                new_position += 1
                continue

            if op >= opcode.HAVE_ARGUMENT:
                skip_args_counter = 2

            new_position += self.TRACE_CODE_LEN + 1

        return new_position

    def get_codeobj_id(self):
        self.current_code_object_id += 1
        return self.current_code_object_id

    def wrap_code(self, codeobj, codeobj_id=0):
        codes = []
        constants = [
            self.wrap_code(item, self.get_codeobj_id())
            if isinstance(item, CodeType) else item
            for item in codeobj.co_consts
        ]

        update_offset = partial(self.calculate_offset, code=codeobj.co_code)
        for st in dis.get_instructions(codeobj):
            self.mark(codeobj_id, st.offset, st)
            constants.append(
                lambda co_id=codeobj_id, opcode=st: self.visit(co_id, opcode)
            )
            codes.extend(self.make_trace(len(constants) - 1))
            codes.append(st.opcode)

            if st.opcode in opcode.hasjrel:
                current_position = update_offset(st.offset)
                taget_position = update_offset(st.argval) - self.TRACE_CODE_LEN
                new_delta = taget_position - current_position
                codes.extend(self.make_args(new_delta - self.AGR_OP_LEN))
            elif st.opcode in opcode.hasjabs:
                codes.extend(self.make_args(
                    update_offset(st.arg) - self.TRACE_CODE_LEN
                ))
            elif st.opcode >= opcode.HAVE_ARGUMENT:
                codes.extend(self.make_args(st.arg))

        new_code = CodeType(
            codeobj.co_argcount,
            codeobj.co_kwonlyargcount,
            codeobj.co_nlocals,
            codeobj.co_stacksize + self.AGR_OP_LEN,
            codeobj.co_flags,
            bytes(codes),  # codestring
            tuple(constants),  # constants
            codeobj.co_names,
            codeobj.co_varnames,
            codeobj.co_filename,
            codeobj.co_name,
            codeobj.co_firstlineno,
            codeobj.co_lnotab,
            codeobj.co_freevars,
            codeobj.co_cellvars,
        )
        return new_code
