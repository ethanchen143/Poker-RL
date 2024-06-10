#set up cpy
#python3 setup.py build_ext --inplace
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("hand_rank_monte_carlo.pyx", compiler_directives={'language_level': "3"}),
)