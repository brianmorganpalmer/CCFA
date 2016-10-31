#!/usr/bin/env python
from functools import partial

from anadama.cli import main as anadama_main

from . import commands

main = partial(anadama_main, cmds=commands.all)

if __name__ == '__main__':
    main()
