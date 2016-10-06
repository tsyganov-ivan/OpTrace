from OpTrace.hook import OpTraceHook
hook = OpTraceHook(['tests.test_code'])
hook.setup_hook()

import tests.test_code as t
assert t.some_method(1, 1, 1) is True

hook.teardown_hook()
hook.report()
