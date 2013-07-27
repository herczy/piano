piano
=====

Python static typing with annotations

Usage
=====

Piano can be enabled the following way:

    import piano
    piano.install()
    
All modules loaded after this will have type checking automatically enabled.

Piano requires for checks that you define your functions with annotations. The annotation should be a type or check function:

    def my_function(arg0 : int, arg1 : str) -> str:
        ...

When module containing such functions is loaded, all functions and class members will be checked.

''WARNING'': piano is slow. The recommended usage is to only use piano for tests.
