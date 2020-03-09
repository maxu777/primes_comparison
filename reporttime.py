# -*- coding: utf-8 -*-
# (c) https://gist.github.com/zed/4276624#file-reporttime-py

import inspect
import sys
import timeit
from functools import partial, wraps
from timeit import default_timer as timer

__version__ = "0.4.0"


def measure_func(func, args, number=1):
    """Measure how long `func(*args)` takes in seconds."""
    f = partial(func, *args)  # pylint: disable=W0142
    while True:
        start = timer()
        r = timeit.repeat(f, number=number, repeat=1)
        if timer() - start > 1:  # at least 1 second per measurement
            break
        number *= 2
    return min(r + timeit.repeat(f, number=number, repeat=2)) / number


def accept_funcs(func):
    """Add function names if necessary.

    Decorator for functions that accept either a sequence of functions
    or (name, function) pairs.
    """
    @wraps(func)
    def wrapper(funcs, *args, **kwargs):
        if hasattr(funcs[0], '__name__'):
            funcs = [(f.__name__, f) for f in funcs]
        return func(funcs, *args, **kwargs)
    return wrapper


def human_seconds(seconds, fmt="%.3g %s"):
    """Return human-readable string that represents given seconds."""
    t = 1e6 * seconds  # start with µsec
    for suff in "usec msec".split():
        if t < 1000:
            return fmt % (t, suff)
        t /= 1000
    return fmt % (t, " sec")


@accept_funcs
def measure(funcs, args, comment='', verbose=False, number=1):
    """Report how long `f(*args)` takes for each f in funcs."""
    if not comment:
        comment = repr(args)

    # measure performance
    results = []
    w = max(len(name) for name, _ in funcs)
    for name, f in funcs:
        results.append((measure_func(f, args, number=number), name))
        if verbose:
            print("{:{}s} {:>9s} {}".format(
                name, w, human_seconds(results[-1][0]), comment))

    # print sorted results
    results.sort()
    mint = results[0][0]  # minimal time
    ratios = ["%5.2f" % (t / mint,) for t, _ in results]
    maxratio_width = max(len(r) for r in ratios)
    #  header
    print("{:{}s} {:>9s} {:>{}s} {}".format(
        "name", w, "time", "ratio", maxratio_width, "comment"))
    ratios = [s.rjust(maxratio_width) for s in ratios]
    for (t, name), ratio in zip(results, ratios):
        print("{:{}s} {:>9s} {} {}".format(
            name, w, human_seconds(t), ratio, comment))
    return results


def get_functions_with_prefix(prefix, module=None):
    if module is None:  # use caller's module
        modname = inspect.currentframe().f_back.f_globals['__name__']
        module = sys.modules[modname]
    all_funcs = inspect.getmembers(module, inspect.isfunction)
    return [f for name, f in all_funcs if name.startswith(prefix)]
