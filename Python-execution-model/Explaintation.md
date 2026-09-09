Yes — you want the **actual `.md` format**, so you can directly copy it into a Markdown file such as `python-core-foundations.md`.

````md
# Python Core Foundations: Backend Developer Cheat Sheet

## 1. The Python Execution Pipeline

Python does not take your `.py` source code and directly execute it as CPU machine instructions. In **CPython**, your code goes through several stages.

### The Execution Flow

```text
                    Python Source Code
                         (.py)
                           │
                           ▼
                    ┌─────────────┐
                    │    Parser   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     AST     │
                    │ Abstract    │
                    │ Syntax Tree │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Compiler  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Bytecode  │
                    │   (.pyc)*   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     PVM     │
                    │ Python VM / │
                    │ Interpreter │
                    └──────┬──────┘
                           │
                           ▼
                    Operating System
                           │
                           ▼
                          CPU
````

> **Note:** Bytecode may be cached in `.pyc` files, usually inside `__pycache__`. Python does not simply read a `.pyc` file every time the program runs.

### Stage 1 — Source Code

You write normal Python:

```python
x = 10
y = 20
print(x + y)
```

This is **human-readable source code**.

The CPU cannot directly understand Python syntax. Python therefore has to process the source code before it can execute it.

---

### Stage 2 — Parser

The parser reads the Python source code and checks whether it follows Python's grammar.

For example:

```python
x = 10
```

is valid Python syntax.

But:

```python
x =
```

is invalid syntax.

The parser detects syntax errors before normal execution can continue.

---

### Stage 3 — AST

The source code is converted into an **Abstract Syntax Tree (AST)**.

The AST represents the **structure and relationships** of the program.

For example:

```python
x = 10 + 20
```

can be conceptually represented as:

```text
        Assignment
        /         \
       x        Addition
                /      \
              10       20
```

You can inspect Python's AST:

```python
import ast

code = "x = 10 + 20"

tree = ast.parse(code)

print(ast.dump(tree, indent=2))
```

> **Core idea:** The AST answers:
> **"What is the structure and meaning of this Python code?"**

---

### Stage 4 — Compilation to Bytecode

Python's compiler converts the AST into **bytecode**.

Bytecode is an intermediate instruction format understood by the Python interpreter.

It is **not CPU machine code**.

You can inspect bytecode using the `dis` module:

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

You may see instructions conceptually similar to:

```text
LOAD_FAST
LOAD_FAST
BINARY_OP
RETURN_VALUE
```

The exact bytecode instructions can change between Python versions.

---

### Stage 5 — Python Virtual Machine

The **Python Virtual Machine (PVM)** is the conceptual/runtime layer that executes Python bytecode in CPython.

It is not a separate physical CPU.

A useful mental model is:

```text
.py source
   ↓
Parser
   ↓
AST
   ↓
Compiler
   ↓
Bytecode
   ↓
Python Interpreter / Evaluation Loop
   ↓
CPython Runtime
   ↓
Operating System
   ↓
CPU
```

> **Core idea:** Python introduces an abstraction layer between your source code and the physical CPU.

---

## 🌳 Python Execution Model

### Tree 1 — How Python Code Is Transformed

```text
Python Program
│
├── Source Code (.py)
│
├── Parser
│   └── validates Python grammar
│
├── AST
│   └── represents program structure
│
├── Compiler
│   └── generates bytecode
│
├── Bytecode
│   └── intermediate instructions
│
└── Python Interpreter
    └── executes bytecode
```

### Tree 2 — What Exists During Execution

```text
Python Process
│
├── Interpreter
│
├── Memory
│   ├── Objects
│   ├── References / Names
│   ├── Call Stack
│   └── Heap
│
├── Threads
│   └── execute Python code
│
├── I/O
│   ├── Database
│   ├── Network
│   ├── Files
│   └── APIs
│
└── Operating System
    └── CPU / Hardware
```

This second model becomes important when learning:

* Memory management
* GIL
* Threads
* Async programming
* Event loops
* FastAPI
* Concurrency

---

# 2. The GIL — Global Interpreter Lock

The **GIL (Global Interpreter Lock)** is a lock in traditional CPython execution that restricts multiple threads from executing Python bytecode simultaneously within the same interpreter.

A simplified mental model:

```text
          CPython Interpreter
                  │
             ┌────▼────┐
             │   GIL   │
             └────┬────┘
                  │
          Only one thread
       executes Python bytecode
          at a time in the
       traditional GIL-enabled
              build
```

### Why Does CPython Have a GIL?

One major reason is that CPython's memory-management system historically relies heavily on **reference counting**.

Conceptually, objects keep track of how many references point to them.

```text
Object
  ↑
  │
Reference Count
```

If multiple threads modify reference counts simultaneously, synchronization is required to prevent race conditions and corruption.

The GIL greatly simplifies parts of CPython's runtime and memory-management implementation.

> **Important:** The GIL is not simply "Python's memory protection system." It is an interpreter-level lock that also simplifies many internal CPython operations.

---

## GIL and CPU-Bound Work

Consider a CPU-heavy calculation:

```python
import threading

def calculate():
    total = 0

    for i in range(10_000_000):
        total += i

    return total

t1 = threading.Thread(target=calculate)
t2 = threading.Thread(target=calculate)

t1.start()
t2.start()

t1.join()
t2.join()
```

In a traditional GIL-enabled CPython build, the threads cannot execute Python bytecode simultaneously on different CPU cores.

Conceptually:

```text
CPU Core 1 ── Thread 1 ──┐
                         │
                       GIL
                         │
CPU Core 2 ── Thread 2 ──┘

       Only one thread
       executes Python
       bytecode at a time
```

Therefore, Python threads are generally **not the solution for speeding up CPU-bound pure-Python calculations**.

For CPU-heavy workloads, possible approaches include:

```text
CPU-bound
│
├── Multiprocessing
├── Multiple worker processes
├── Native libraries that release the GIL
└── Free-threaded CPython where appropriate
```

> **Important:** Modern CPython also supports free-threaded builds, so "Python always has a GIL" is not an absolute rule.

---

## GIL and I/O-Bound Work

Consider a database operation:

```python
result = database.query(...)
```

The application may spend significant time waiting for the database:

```text
Application
    │
    ▼
Database
    │
    │ waiting...
    ▼
Response
```

During many blocking I/O operations, CPython can release the GIL, allowing another thread to execute Python code.

However:

> **The GIL and asynchronous programming are not the same thing.**

FastAPI commonly uses asynchronous I/O:

```python
@app.get("/users")
async def get_users():
    users = await database.fetch_all()
    return users
```

Here, `await` allows the event loop to work on other tasks while the current operation is waiting for I/O.

Conceptually:

```text
Request A
   │
   ├── Query database
   │
   └── WAIT ───────────────┐
                           │
Request B                  │
   │                       │
   ├── Execute Python      │
   │                       │
   └── Response             │
                           │
Request A <────────────────┘
```

### Backend Mental Model

```text
CPU-bound
    ↓
CPU is the bottleneck

I/O-bound
    ↓
Waiting for external resources is often the bottleneck
```

---

# 3. Variables, Memory & Mutability

One of the most important Python concepts is:

> **A Python variable is a name/reference associated with an object.**

It is better to imagine a variable as a **name tag** rather than a physical box containing the value.

For example:

```python
age = 21
```

Conceptually:

```text
age
 │
 ▼
┌─────────┐
│   21    │
│ integer │
└─────────┘
```

The name `age` refers to an integer object.

---

## Immutable Objects

Common immutable objects include:

```text
int
float
str
tuple
bool
frozenset
```

Consider:

```python
age = 21
age = 22
```

Python does not modify the integer object `21`.

Conceptually:

```text
Before:

age ───────► 21


After:

age ───────► 22
```

The name `age` is now associated with another integer object.

> **Core idea:** An immutable object cannot be changed after it has been created.

---

## Mutable Objects

Common mutable objects include:

```text
list
dict
set
bytearray
```

Example:

```python
users = ["Raj", "Amit"]

users.append("John")
```

The list itself is modified:

```text
users
  │
  ▼
┌─────────────────────┐
│ Raj │ Amit │ John   │
└─────────────────────┘
```

---

## Mutable Object Example

Consider:

```python
a = [1, 2, 3]
b = a

b.append(4)

print(a)
print(b)
```

Output:

```text
[1, 2, 3, 4]
[1, 2, 3, 4]
```

Why?

```text
       ┌───────────────┐
a ─────►               │
       │ [1, 2, 3, 4]  │
b ─────►               │
       └───────────────┘
```

Both `a` and `b` refer to the **same list object**.

You can verify this:

```python
print(a is b)
```

Output:

```text
True
```

---

# 4. The Mutable Default Argument Trap

This is particularly important for backend developers.

Consider:

```python
def add_user(name, users=[]):
    users.append(name)
    return users
```

You might expect:

```python
add_user("Raj")
# ["Raj"]

add_user("Amit")
# ["Amit"]
```

But the actual behavior is:

```python
add_user("Raj")
# ["Raj"]

add_user("Amit")
# ["Raj", "Amit"]
```

### Why Does This Happen?

Default arguments are evaluated when the function is **defined**, not every time the function is called.

Conceptually:

```text
Function created
      │
      ▼
Default list created
      │
      ▼
Same list reused
      │
 ┌────┴────┐
 ▼         ▼
Call 1    Call 2
 │         │
 └────┬────┘
      ▼
Same list
```

This can become dangerous in server applications if mutable state is unintentionally shared between requests.

### Correct Approach

Use `None`:

```python
def add_user(name, users=None):
    if users is None:
        users = []

    users.append(name)
    return users
```

Now each call creates a fresh list:

```text
Request 1 → New list
Request 2 → New list
Request 3 → New list
```

> **Backend mental model:** A Python function definition is created once, so a mutable default object can persist across function calls.

---

# 5. Big-O Notation & Data Structures

**Big-O notation** describes how an algorithm's resource usage grows as the input size grows.

It is not simply:

> "How many seconds will this code take?"

Instead, it focuses on the **growth rate** of the work as input size increases.

---

# O(n) — Linear Time

Consider:

```python
users = ["Raj", "Amit", "John", "Sam"]

for user in users:
    if user == "Sam":
        print("Found")
```

If there are:

```text
10 users        → up to 10 checks
1,000 users     → up to 1,000 checks
100,000 users   → up to 100,000 checks
```

The amount of work grows approximately with `n`.

Therefore:

```text
O(n)
```

---

# O(1) — Constant Time

A Python dictionary uses hashing to provide **average-case constant-time lookup**.

Example:

```python
users = {
    101: "Raj",
    102: "Amit",
    103: "John"
}

print(users[102])
```

Conceptually:

```text
key
 │
 ▼
Hashing
 │
 ▼
Bucket / table location
 │
 ▼
Value
```

The dictionary normally does not scan every key one by one.

Therefore:

```text
Dictionary lookup → Average O(1)
```

The same general idea applies to sets:

```python
blocked_ips = {
    "192.168.1.10",
    "192.168.1.20"
}

if "192.168.1.20" in blocked_ips:
    print("Blocked")
```

Average-case:

```text
Set membership → O(1)
```

---

## Important O(1) Clarification

Do not memorize:

> "O(1) means it always takes exactly the same amount of time."

That's not strictly correct.

`O(1)` means the operation's complexity is **constant with respect to the input size**.

Also, Python dictionary and set operations are generally **average-case O(1)**, not guaranteed O(1) in every possible situation.

---

# 🌳 Data Structure Mental Model

```text
Data Structures
│
├── List
│   ├── Ordered
│   ├── Mutable
│   └── Search → O(n)
│
├── Tuple
│   ├── Ordered
│   ├── Immutable
│   └── Index access → O(1)
│
├── Dictionary
│   ├── Key → Value
│   ├── Mutable
│   └── Average lookup → O(1)
│
└── Set
    ├── Unique values
    ├── Mutable
    └── Average membership → O(1)
```

---

# 🌳 Complete Python Backend Mental Model

```text
                    PYTHON APPLICATION
                           │
                           ▼
                 ┌──────────────────┐
                 │   Source Code    │
                 │      .py         │
                 └────────┬─────────┘
                          │
                          ▼
                       Parser
                          │
                          ▼
                         AST
                          │
                          ▼
                      Compiler
                          │
                          ▼
                      Bytecode
                          │
                          ▼
                Python Interpreter
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
          Objects                    Threads
             │                         │
      ┌──────┴──────┐                  │
      │             │                  ▼
  Immutable      Mutable              GIL*
      │             │                  │
      │             │           one thread executes
      │             │           Python bytecode at
      │             │           a time in traditional
      │             │           GIL-enabled CPython
      │             │
      └──────┬──────┘
             │
             ▼
        Memory / Heap
             │
             ▼
      Data Structures
       │    │    │
       ▼    ▼    ▼
     List Dict Set
       │    │    │
      O(n) O(1) O(1)
       │    │    │
       └────┴────┘
             │
             ▼
        Backend Logic
             │
       ┌─────┴─────┐
       ▼           ▼
      CPU          I/O
   computation   Database
                 Network
                 Files
                    │
                    ▼
                Operating
                  System
                    │
                    ▼
                   CPU
```

> *Traditional GIL-enabled CPython. Modern Python also supports free-threaded builds.*

---

# 🔑 What I Should Remember

## 1. Execution

```text
Source Code
     ↓
Parser
     ↓
AST
     ↓
Compiler
     ↓
Bytecode
     ↓
Python Interpreter
     ↓
Operating System / CPU
```

Python source code is **not directly executed by the CPU**.

---

## 2. GIL

```text
Traditional CPython
        ↓
       GIL
        ↓
One thread executes Python bytecode
at a time within the interpreter
```

Remember:

```text
CPU-bound → threads don't generally provide
            parallel execution of pure Python
            bytecode in traditional CPython

I/O-bound → waiting can be overlapped using
            threads or asynchronous I/O
```

---

## 3. Variables and Objects

```text
Variable
   ↓
Name / Reference
   ↓
Object
```

```text
Immutable → object cannot be changed
Mutable   → object can be changed in place
```

---

## 4. Mutable Default Arguments

```python
def func(data=[]):
```

can reuse the **same list across calls**.

Prefer:

```python
def func(data=None):
    if data is None:
        data = []
```

---

## 5. Big-O

```text
List search
    ↓
O(n)

Dictionary lookup
    ↓
Average O(1)

Set membership
    ↓
Average O(1)
```

---

# 🧠 Final Mental Model

> **Python source code is transformed into bytecode, and the Python interpreter executes that bytecode. Python variables are names that refer to objects in memory. Objects can be mutable or immutable. The GIL affects how traditional CPython threads execute Python bytecode, while I/O-bound applications can use concurrency to avoid wasting time waiting. Finally, choosing the right data structure affects the algorithm's performance as the amount of data grows.**

```
```
