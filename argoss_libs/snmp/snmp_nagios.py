import importlib
sys = importlib.import_module('sys')
traceback = importlib.import_module('traceback')
nagios = importlib.import_module('nagiosplugin')
#import nagiosplugin as nagios
import functools
from nagiosplugin.runtime import Runtime


def guarded(original_function=None, verbose=None):
    """Runs a function nagiosplugin's Runtime environment.

    `guarded` makes the decorated function behave correctly with respect
    to the Nagios plugin API if it aborts with an uncaught exception or
    a timeout. It exits with an *unknown* exit code and prints a
    traceback in a format acceptable by Nagios.

    This function should be used as a decorator for the script's `main`
    function.

    :param verbose: Optional keyword parameter to control verbosity
        level during early execution (before
        :meth:`~nagiosplugin.Check.main` has been called). For example,
        use `@guarded(verbose=0)` to turn tracebacks in that phase off.
    """
    def _decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            runtime = SnmpRuntime()
            if verbose is not None:
                runtime.verbose = verbose
            try:
                return func(*args, **kwds)
            except nagios.Timeout as exc:
                runtime._handle_exception(
                    'Timeout: check execution aborted after {0}'.format(
                        exc))
            except Exception:
                runtime._handle_exception()
        return wrapper
    if original_function is not None:
        assert callable(original_function), (
            'Function {!r} not callable. Forgot to add "verbose=" keyword?'.
            format(original_function))
        return _decorate(original_function)
    return _decorate


class SnmpRuntime(Runtime):

    def _handle_exception(self, statusline=None):
        exc_type, value = sys.exc_info()[0:2]
        name = self.check.name.upper() + ' ' if self.check else ''
        self.output.status = '{0}UNKNOWN: {1}'.format(
            name, statusline or traceback.format_exception_only(
                exc_type, value)[0].strip())
        if self.verbose > 0:
            self.output.add_longoutput(traceback.format_exc())
        print('{0}'.format(self.output), end='', file=self.stdout)
        self.exitcode = 3
        return self.exitcode, '{0}'.format(self.output)

    def execute(self, check, verbose=None, timeout=None):
        self.check = check
        if verbose is not None:
            self.verbose = verbose
        if timeout is not None:
            self.timeout = int(timeout)
        if self.timeout:
            with_timeout(self.timeout, self.run, check)
        else:
            self.run(check)
        return self.exitcode, '{0}'.format(self.output)

    def sysexit(self):
        print('Exit code')
        return self.exitcode


class SnmpCheck(nagios.Check):

    def main(self, verbose=None, timeout=None):
        """All-in-one control delegation to the runtime environment.

        Get a :class:`~nagiosplugin.runtime.Runtime` instance and
        perform all phases: run the check (via :meth:`__call__`), print
        results and exit the program with an appropriate status code.

        :param verbose: output verbosity level between 0 and 3
        :param timeout: abort check execution with a :exc:`Timeout`
            exception after so many seconds (use 0 for no timeout)
        """
        runtime = SnmpRuntime()
        return runtime.execute(self, verbose, timeout)


class InterfaceStatusContext(nagios.ScalarContext):

    def __init__(self, name, warning=None, critical=None, fmt_metric=None, result_cls=nagios.Result):
        super(InterfaceStatusContext, self).__init__(name=name, warning=warning, critical=critical,
                                                     fmt_metric=fmt_metric, result_cls=result_cls)

    def evaluate(self, metric, resource):
        if int(metric.value) == 1:
            return self.result_cls(nagios.state.Ok, metric=metric)
        else:
            hint = ('There is a problem with your interface status')
            return self.result_cls(nagios.state.Critical, hint=hint, metric=metric)
