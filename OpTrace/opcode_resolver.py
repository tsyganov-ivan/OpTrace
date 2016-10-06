import re
from collections import namedtuple

# issues:
# LOAD_CLOSURE - неправильно получаем строку.
# MAKE_CLOSURE - неправильно получаем строку.
# LOAD_CLASSDEREF(i)
# Much like LOAD_DEREF but first checks the locals dictionary before consulting the cell. This is used for loading free variables in class bodies.
#
# STORE_DEREF(i)
# Stores TOS into the cell contained in slot i of the cell and free variable storage.
#
# DELETE_DEREF(i)
# Empties the cell contained in slot i of the cell and free variable storage. Used by the del statement.
#
# EXTENDED_ARG(ext)¶
# Prefixes any opcode which has an argument too big to fit into the default two bytes. ext holds two additional bytes which, taken together with the subsequent opcode’s argument, comprise a four-byte argument, ext being the two most-significant bytes.

MissingOpcode = namedtuple(
    'MissingOpcode', ['line', 'start', 'stop', 'comment'])

class OpcodeResolver:
    skip_opnames = [
        'NOP', 'POP_TOP', 'ROT_TWO', 'ROT_THREE', 'DUP_TOP', 'DUP_TOP_TWO',
        'CALL_FUNCTION', 'POP_TOP', 'PRINT_EXPR', 'POP_BLOCK', 'POP_EXCEPT',
        'LOAD_BUILD_CLASS', 'MAKE_FUNCTION', 'CALL_FUNCTION_VAR', 'CALL_FUNCTION_KW',
        'CALL_FUNCTION_VAR_KW', 'HAVE_ARGUMENT'

        # Async opcodes
        'GET_AWAITABLE', 'GET_AITER', 'GET_ANEXT', 'BEFORE_ASYNC_WITH',
        'SETUP_ASYNC_WITH',
        # Exceptions
        'END_FINALLY', 'SETUP_EXCEPT', 'SETUP_FINALLY'

        # Maybe resolve?
        'SETUP_WITH', 'WITH_CLEANUP_START', 'WITH_CLEANUP_FINISH',
        'SETUP_LOOP', ''
        'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP', 'JUMP_ABSOLUTE'
    ]

    def resolve(self, opcode, line, source, prev_position):
        resolver = getattr(self, '_{}'.format(opcode.opname), None)
        if resolver is None:
            return

        data = resolver(opcode, line, source, prev_position)
        if not data:
            return

        return MissingOpcode(data.line, data.start, data.stop, opcode.opname)

    def find_index(self, source, substr, start):
        try:
            return source.index(substr, start)
        except ValueError:
            if start>0:
                return self.find_index(source, substr, 0)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(source)
            print(substr)

    def missing_by_regexp(self, line, source, regexp):
        found = re.search(regexp, source)
        if not found:
            return
        return MissingOpcode(line, found.start(1), found.end(1), '')

    def missing_symbol(self, line, source, prev_position, symbol):
        last_line, position = prev_position
        index = self.find_index(source, symbol, position)
        if not index:
            return
        return MissingOpcode(line, index, index + len(symbol), '')

    def vars_and_const(self, opcode, line, source, prev_position):
        regexp = r'(?:\W|\s)(dumper)(?:\W|\s)'.format(re.escape(opcode.argrepr))
        return self.missing_by_regexp(line, source, regexp)
        # return self.missing_symbol(line, source, prev_position, opcode.argrepr)

    def missing_line(self, line, source, comment):
        line_len = len(source)
        line_stripped = len(source.lstrip())
        return MissingOpcode(line, line_len-line_stripped, line_len, comment)

    def _BREAK_LOOP(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, 'break')

    def _CONTINUE_LOOP(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, 'continue')

    def _UNARY_NOT(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, 'not')

    def _UNARY_INVERT(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '~')

    def _STORE_NAME(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _DELETE_NAME(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, 'del '+opcode.argrepr)

    def _LOAD_GLOBAL(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _STORE_GLOBAL(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _LOAD_FAST(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _LOAD_CONST(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _LOAD_NAME(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _LOAD_DEREF(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _COMPARE_OP(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _STORE_FAST(self, opcode, line, source, prev_position):
        return self.vars_and_const(opcode, line, source, prev_position)

    def _POP_JUMP_IF_TRUE(self, opcode, line, source, prev_position):
        line, position = prev_position
        return MissingOpcode(line, position+1, position+2, 'Never True')

    def _POP_JUMP_IF_FALSE(self, opcode, line, source, prev_position):
        return self.missing_line(line, source, 'Never False')

    def _RETURN_VALUE(self, opcode, line, source, prev_position):
        return self.missing_line(line, source, 'Never returned')

    def _YIELD_VALUE(self, opcode, line, source, prev_position):
        return self.missing_line(line, source, 'Never yielded')

    def _YIELD_FROM(self, opcode, line, source, prev_position):
        return self.missing_line(line, source, 'Never yielded from')

    def _BINARY_POWER(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '**')

    def _BINARY_MULTIPLY(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '*')

    def _BINARY_MATRIX_MULTIPLY(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '@')

    def _BINARY_FLOOR_DIVIDE(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '//')

    def _BINARY_TRUE_DIVIDE(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '/')

    def _BINARY_MODULO(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '%')

    def _BINARY_ADD(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '+')

    def _BINARY_SUBTRACT(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '-')

    def _BINARY_SUBSCR(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\[.+?\])')

    def _BINARY_LSHIFT(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source,prev_position, '<<')

    def _BINARY_RSHIFT(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source,prev_position, '>>')

    def _BINARY_AND(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source,prev_position, '&')

    def _BINARY_XOR(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source,prev_position, '^')

    def _BINARY_OR(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source,prev_position, '|')

    def _INPLACE_POWER(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '**')

    def _INPLACE_MULTIPLY(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '*')

    def _INPLACE_MATRIX_MULTIPLY(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '@')

    def _INPLACE_FLOOR_DIVIDE(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '//')

    def _INPLACE_TRUE_DIVIDE(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '/')

    def _INPLACE_MODULO(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '%')

    def _INPLACE_ADD(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '+')

    def _INPLACE_SUBTRACT(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '-')

    def _INPLACE_LSHIFT(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '<<')

    def _INPLACE_RSHIFT(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '>>')

    def _INPLACE_AND(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '&')

    def _INPLACE_XOR(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '^')

    def _INPLACE_OR(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, '|')

    def _STORE_SUBSCR(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\S+\[.+?\])')

    def _DELETE_SUBSCR(self, opcode, line, source, prev_position):
        return self.missing_line(line, source, '')

    def _SET_ADD(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'\{(\S+)')

    def _LIST_APPEND(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'\[(\S+)')

    def _MAP_ADD(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'\{(\w+\s*:\s*\S+)')

    def _IMPORT_STAR(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, r'import *')

    def _SETUP_WITH(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, r'with ')

    def _UNPACK_SEQUENCE(self, opcode, line, source, prev_position):
        return self.missing_line(line, source, '')

    def _UNPACK_EX(self, opcode, line, source, prev_position):
        return self.missing_line(line, source, '')

    def _RAISE_VARARGS(self, opcode, line, source, prev_position):
        return self.missing_line(line, source, '')

    def _STORE_ATTR(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\w+\.\w+\s*=)')

    def _DELETE_ATTR(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(del\s*\w+\.\w+)')

    def _DELETE_GLOBAL(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(del\s*\w+)')

    def _DELETE_FAST(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(del\s*\w+)')

    def _BUILD_TUPLE(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\((\w*,?\s*)*\))')

    def _BUILD_LIST(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\[(\w*,?\s*)*\])')

    def _BUILD_SET(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\{(\w*,?\s*)*\})')

    def _BUILD_MAP(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\{(\w*\s*:\s*\w*,?\s*)*\})')

    def _LOAD_ATTR(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\w+\.\w+)')

    def _IMPORT_NAME(self, opcode, line, source, prev_position):
        return self.missing_symbol(line, source, prev_position, opcode.argrepr)

    def _IMPORT_FROM(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(from\s*\S+\s*import\s*\S+)')

    def _FOR_ITER(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(for\s*.+?\s*in\s*.+?)')

    def _GET_ITER(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(for\s*.+?\s*in\s*.+?)')

    def _BUILD_SLICE(self, opcode, line, source, prev_position):
        return self.missing_by_regexp(line, source, r'(\S+\[\w*:\w*:?\w*\])')
