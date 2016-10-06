# OpTrace

Library created to check Python code-coverage on opcode level.
Checked only on Python 3.5.1

##### This is proof of concept! Be careful!

## Example

```python
from OpTrace.hook import OpTraceHook
hook = OpTraceHook(['tests.test_code'])
hook.setup_hook()

# your test code starts here

import tests.test_code as t
assert t.some_method(1, 1, 1) is True

# your test code ends here

hook.teardown_hook()
hook.report()
```

Target code from exampe:
```python
def some_method(a, b, c):
    if a or b or c:
        return True
    return False
```

After call `hook.report()` you will see simple and terrible report.
Those opcodes never executed.

```

----------- Report tests.test_code --------------
   1:     if a or b or c:
          ^^^^^^^^^^^^^^^ POP_JUMP_IF_FALSE
   1:     if a or b or c:
                  ^ POP_JUMP_IF_TRUE
   3:     return False
          ^^^^^^^^^^^^ RETURN_VALUE
--- cannot represent ---
Last known source line:
    if a or b or c:
Opcodes:
 -    Instruction(opname='LOAD_FAST', opcode=124, arg=1, argval='b', argrepr='b', offset=6, starts_line=None, is_jump_target=False)
 -    Instruction(opname='LOAD_FAST', opcode=124, arg=2, argval='c', argrepr='c', offset=12, starts_line=None, is_jump_target=False)
------------------------
Last known source line:
        return True
Opcodes:
 -    Instruction(opname='LOAD_CONST', opcode=100, arg=1, argval=True, argrepr='True', offset=18, starts_line=3, is_jump_target=True)
------------------------
Last known source line:
    return False
Opcodes:
 -    Instruction(opname='LOAD_CONST', opcode=100, arg=2, argval=False, argrepr='False', offset=22, starts_line=4, is_jump_target=True)
------------------------

```