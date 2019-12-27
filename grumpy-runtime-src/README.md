This is home for Grumpy runtime, which provides Python stdlib written in Go for programs produced by Grumpy. The runtime consists of two directories.

 * [`runtime/`](runtime) contains Go code
 * [`lib/`](lib) contains Python code
 
Both are used to implement Python feature on top of Go, such as slices, types, exceptions and so on. When `import` code is encountered, it first looks in these two dirs.

See [../README.md](../README.md) for details on using Grumpy.
