"""
PYTHON CORE FOUNDATIONS — COMPLETE CODE PLAYGROUND
===================================================

This single file contains runnable examples for the concepts covered in:

1. Python Execution Pipeline
2. Parser / AST
3. Compiler / Bytecode
4. Python Runtime / Interpreter
5. GIL
6. CPU-bound vs I/O-bound work
7. Threads
8. Async / await
9. Variables and object references
10. Mutable vs immutable objects
11. == vs is
12. Mutable default argument trap
13. Correct default argument pattern
14. Big-O examples
15. List / Tuple / Set / Dictionary
16. Hashing and dictionary/set lookup
17. Backend-style request simulation
18. Interview demonstrations

Run:

    python python_core_foundations_playground.py

Each section is independent, so you can comment out sections
while practicing.
"""

import ast
import dis
import hashlib
import threading
import asyncio
import time
from collections import Counter


# ============================================================
# 0. HELPER
# ============================================================

def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# 1. PYTHON EXECUTION PIPELINE
# ============================================================

section("1. PYTHON EXECUTION PIPELINE")

"""
Concept:

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
   Python Runtime
        ↓
     OS / CPU

Python itself is a language.

CPython is one implementation of that language.

The following examples allow us to inspect two important
intermediate stages: AST and bytecode.
"""

source_code = """
x = 10
y = 20
result = x + y
print(result)
"""

print("Python source:")
print(source_code)


# ============================================================
# 2. AST — ABSTRACT SYNTAX TREE
# ============================================================

section("2. AST — ABSTRACT SYNTAX TREE")

"""
AST represents the structure of Python code.

Example:

    x = 10 + 20

Conceptually:

    Assignment
    ├── Target → x
    └── Value
        └── Addition
            ├── 10
            └── 20
"""

code = "x = 10 + 20"

tree = ast.parse(code)

print("AST:")
print(ast.dump(tree, indent=2))


# ============================================================
# 3. BYTECODE
# ============================================================

section("3. BYTECODE")

"""
Python source is compiled into bytecode in CPython.

Bytecode is NOT CPU machine code.

We can inspect bytecode using the dis module.
"""

def add(a, b):
    return a + b


print("Function:")
print(add)

print("\nDisassembled bytecode:")
dis.dis(add)

print("""
Mental model:

    Python source
         ↓
       AST
         ↓
      Bytecode
         ↓
    CPython runtime
         ↓
        CPU
""")


# ============================================================
# 4. FUNCTIONS ARE OBJECTS
# ============================================================

section("4. FUNCTIONS ARE OBJECTS")

"""
A function definition creates a function object when the
def statement executes.

We can inspect the function's type and attributes.
"""

def greet(name):
    return f"Hello, {name}"


print("Function type:", type(greet))
print("Function name:", greet.__name__)
print("Function result:", greet("Raj"))

"""
This helps explain why Python treats functions as objects.

Functions can be:

- assigned to variables
- passed as arguments
- returned from other functions
- stored in collections
"""


another_name = greet

print("Same function object:", another_name is greet)
print("Calling through another name:", another_name("Python"))


# ============================================================
# 5. VARIABLES ARE REFERENCES TO OBJECTS
# ============================================================

section("5. VARIABLES ARE REFERENCES TO OBJECTS")

"""
Think:

    variable name
          ↓
        object

Example:

    x = 10
"""

x = 10

print("x:", x)
print("type(x):", type(x))
print("id(x):", id(x))

"""
The exact memory address returned by id() is implementation
dependent. The important concept is object identity.
"""

numbers = [1, 2, 3]

a = numbers
b = numbers

print("\nnumbers:", numbers)
print("a:", a)
print("b:", b)

print("a is numbers:", a is numbers)
print("b is numbers:", b is numbers)
print("a is b:", a is b)


# ============================================================
# 6. MUTABLE OBJECTS
# ============================================================

section("6. MUTABLE OBJECTS")

"""
Mutable means:

    The object can be changed after creation.

Common mutable objects:

    list
    dict
    set
"""

items = [1, 2, 3]

print("Before:", items)

items.append(4)

print("After append:", items)

"""
The list itself was modified.

Now demonstrate shared references.
"""

first = [10, 20]
second = first

second.append(30)

print("first:", first)
print("second:", second)

print("Same object:", first is second)


# ============================================================
# 7. IMMUTABLE OBJECTS
# ============================================================

section("7. IMMUTABLE OBJECTS")

"""
Immutable means:

    The object cannot be changed after creation.

Common immutable objects:

    int
    float
    bool
    str
    tuple
    frozenset
"""

x = 10

old_id = id(x)

x = x + 5

new_id = id(x)

print("New value:", x)
print("Old id:", old_id)
print("New id:", new_id)
print("Identity changed:", old_id != new_id)

"""
Important:

    x = x + 5

does not modify integer 10.

Instead, x becomes associated with an integer object
representing 15.
"""


# ============================================================
# 8. == VS is
# ============================================================

section("8. == VS is")

"""
==

    Compares values.

is

    Checks whether two names refer to the same object.
"""

list_a = [1, 2, 3]
list_b = [1, 2, 3]

print("list_a == list_b:", list_a == list_b)
print("list_a is list_b:", list_a is list_b)

list_c = list_a

print("list_a == list_c:", list_a == list_c)
print("list_a is list_c:", list_a is list_c)


# ============================================================
# 9. MUTABLE DEFAULT ARGUMENT TRAP
# ============================================================

section("9. MUTABLE DEFAULT ARGUMENT TRAP")

"""
WRONG:

    def add_item(item, items=[]):

The default list is created when the function definition
executes, not each time the function is called.
"""

def bad_add_item(item, items=[]):
    items.append(item)
    return items


print("First call:", bad_add_item("A"))
print("Second call:", bad_add_item("B"))
print("Third call:", bad_add_item("C"))

print("""
Notice:

    First call  → ['A']
    Second call → ['A', 'B']
    Third call  → ['A', 'B', 'C']

The same default list is reused.
""")


# ============================================================
# 10. CORRECT DEFAULT ARGUMENT
# ============================================================

section("10. CORRECT DEFAULT ARGUMENT")

"""
Correct pattern:

    def function(value=None):
        if value is None:
            value = []
"""

def good_add_item(item, items=None):
    if items is None:
        items = []

    items.append(item)

    return items


print("First call:", good_add_item("A"))
print("Second call:", good_add_item("B"))
print("Third call:", good_add_item("C"))

"""
Each call creates a new list when no list is supplied.
"""


# ============================================================
# 11. DEFAULT ARGUMENTS ARE STORED ON THE FUNCTION
# ============================================================

section("11. FUNCTION DEFAULTS")

def example(value=[]):
    return value


print("Function defaults:", example.__defaults__)
print("Default object:", example.__defaults__[0])
print("Default object id:", id(example.__defaults__[0]))

"""
The __defaults__ attribute lets us see positional default
values stored by the function object.

This is useful for understanding why mutable defaults persist.
"""


# ============================================================
# 12. LIST
# ============================================================

section("12. LIST")

"""
List:

    - ordered
    - mutable
    - duplicates allowed
    - index-based access
"""

users = ["Raj", "Aman", "Rohit", "Raj"]

print("List:", users)
print("First item:", users[0])
print("Last item:", users[-1])

users.append("Neha")

print("After append:", users)

print("Search result:", "Aman" in users)

"""
Typical complexity:

    Index access → O(1)
    Search       → O(n)
    Append       → amortized O(1)
"""


# ============================================================
# 13. TUPLE
# ============================================================

section("13. TUPLE")

"""
Tuple:

    - ordered
    - immutable
    - duplicates allowed
"""

point = (10, 20)

print("Tuple:", point)
print("X:", point[0])
print("Y:", point[1])

try:
    point[0] = 100
except TypeError as error:
    print("Cannot modify tuple:", error)


# ============================================================
# 14. SET
# ============================================================

section("14. SET")

"""
Set:

    - unique values
    - mutable
    - hashing-based membership
"""

skills = {"Python", "SQL", "Git", "Python"}

print("Set:", skills)

print("Has Python:", "Python" in skills)
print("Has Java:", "Java" in skills)

skills.add("FastAPI")

print("After adding FastAPI:", skills)

"""
Average membership lookup:

    O(1)
"""


# ============================================================
# 15. DICTIONARY
# ============================================================

section("15. DICTIONARY")

"""
Dictionary stores key-value pairs.

Example:

    key → value
"""

user = {
    "id": 101,
    "name": "Raj",
    "role": "Backend Developer"
}

print("User:", user)

print("Name:", user["name"])
print("Role:", user["role"])

user["experience"] = "Learning"

print("Updated user:", user)

print("Average key lookup:", "O(1)")


# ============================================================
# 16. HASHING CONCEPT
# ============================================================

section("16. HASHING")

"""
Dictionaries and sets use hashing.

Conceptually:

    key
     ↓
    hash
     ↓
 storage location
     ↓
   value
"""

key = "raj"

print("Key:", key)
print("Python hash:", hash(key))

"""
The exact hash value can change between Python processes
because Python intentionally randomizes hashing for some types.

Do not memorize the actual number.

Understand:

    key → hash → lookup
"""


# ============================================================
# 17. DICTIONARY LOOKUP VS LIST SEARCH
# ============================================================

section("17. LIST SEARCH VS DICTIONARY LOOKUP")

users_list = [
    "Raj",
    "Aman",
    "Rohit",
    "Neha",
    "Priya",
]

users_dict = {
    "Raj": 101,
    "Aman": 102,
    "Rohit": 103,
    "Neha": 104,
    "Priya": 105,
}

name = "Priya"

print("List search:", name in users_list)
print("Dictionary lookup:", users_dict.get(name))

"""
Conceptually:

List:

    ["Raj", "Aman", "Rohit", "Neha", "Priya"]
       ↓
    may scan elements
       ↓
    O(n)

Dictionary:

    "Priya"
       ↓
    hash
       ↓
    lookup
       ↓
    O(1) average
"""


# ============================================================
# 18. BIG-O — O(1)
# ============================================================

section("18. BIG-O — O(1)")

def get_first_item(items):
    return items[0]


numbers = [10, 20, 30, 40, 50]

print("First item:", get_first_item(numbers))

"""
Indexed list access is generally O(1).

Whether the list contains:

    5 items
    5,000 items
    5,000,000 items

the indexed lookup does not require scanning from the
beginning of the list.
"""


# ============================================================
# 19. BIG-O — O(n)
# ============================================================

section("19. BIG-O — O(n)")

def find_number(numbers, target):
    for number in numbers:
        if number == target:
            return True

    return False


numbers = [1, 2, 3, 4, 5]

print("Found:", find_number(numbers, 5))

"""
Worst-case:

    The algorithm may inspect every element.

Therefore:

    O(n)
"""


# ============================================================
# 20. BIG-O — O(n²)
# ============================================================

section("20. BIG-O — O(n²)")

def print_all_pairs(items):
    for first in items:
        for second in items:
            print(first, second)


small_list = [1, 2, 3]

print_all_pairs(small_list)

"""
For n items:

    outer loop → n
    inner loop → n

Total:

    n × n = n²

Therefore:

    O(n²)
"""


# ============================================================
# 21. BIG-O — O(log n) EXAMPLE
# ============================================================

section("21. BIG-O — O(log n)")

def binary_search(numbers, target):
    left = 0
    right = len(numbers) - 1

    while left <= right:
        middle = (left + right) // 2

        if numbers[middle] == target:
            return middle

        if numbers[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


sorted_numbers = [1, 3, 5, 7, 9, 11, 13, 15]

index = binary_search(sorted_numbers, 11)

print("Found at index:", index)

"""
Binary search repeatedly cuts the search space roughly in half.

Therefore:

    O(log n)

Important requirement:

    The data must be sorted.
"""


# ============================================================
# 22. COUNTER — ANOTHER PRACTICAL DATA STRUCTURE
# ============================================================

section("22. COUNTER")

"""
Counter is useful for frequency counting.
"""

words = ["python", "api", "python", "git", "api", "python"]

frequency = Counter(words)

print("Frequency:", frequency)
print("Python count:", frequency["python"])

"""
This is a practical example of choosing the right data
structure instead of manually counting everything.
"""


# ============================================================
# 23. THREADS — BASIC DEMONSTRATION
# ============================================================

section("23. THREADS")

"""
A thread is an execution path inside a process.

Example:

    Process
    ├── Thread 1
    ├── Thread 2
    └── Thread 3

Traditional GIL-enabled CPython does not allow multiple
threads in the same interpreter to execute Python bytecode
simultaneously.

However, threads can still be useful for I/O-bound work.
"""

def thread_work(name):
    for i in range(3):
        print(f"{name}: step {i}")


thread1 = threading.Thread(
    target=thread_work,
    args=("Thread-A",)
)

thread2 = threading.Thread(
    target=thread_work,
    args=("Thread-B",)
)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("Both threads finished.")


# ============================================================
# 24. CPU-BOUND WORK
# ============================================================

section("24. CPU-BOUND WORK")

"""
CPU-bound work spends most of its time doing calculations.

Example:
"""

def cpu_work(limit):
    total = 0

    for i in range(limit):
        total += i * i

    return total


start = time.perf_counter()

result = cpu_work(1_000_000)

elapsed = time.perf_counter() - start

print("Result:", result)
print("Time:", elapsed, "seconds")

"""
This is CPU-heavy pure Python work.

With traditional GIL-enabled CPython, using multiple Python
threads does not normally provide true parallel execution
of this bytecode across CPU cores.
"""


# ============================================================
# 25. I/O-BOUND WORK — THREADING EXAMPLE
# ============================================================

section("25. I/O-BOUND WORK — THREADING")

"""
Simulate I/O using sleep.

sleep() represents waiting.

In a real backend, this waiting might be:

    database
    HTTP API
    file
    network
"""

def fake_io(name):
    print(name, "started")

    time.sleep(2)

    print(name, "finished")


start = time.perf_counter()

t1 = threading.Thread(target=fake_io, args=("Request A",))
t2 = threading.Thread(target=fake_io, args=("Request B",))

t1.start()
t2.start()

t1.join()
t2.join()

elapsed = time.perf_counter() - start

print("Total time:", elapsed, "seconds")

"""
Conceptually, instead of:

    Request A → wait 2 sec → Request B → wait 2 sec

threads can overlap waiting:

    Request A → wait
    Request B → wait
              ↓
          both finish

This is why threads can be useful for I/O-bound work.
"""


# ============================================================
# 26. ASYNC / AWAIT
# ============================================================

section("26. ASYNC / AWAIT")

"""
Async programming is another way to handle I/O efficiently.

Important:

    GIL != async

async/await is about cooperative task scheduling and
handling operations that spend time waiting.
"""

async def async_io(name):
    print(name, "started")

    await asyncio.sleep(2)

    print(name, "finished")


async def run_async_example():
    await asyncio.gather(
        async_io("Async Request A"),
        async_io("Async Request B"),
    )


start = time.perf_counter()

asyncio.run(run_async_example())

elapsed = time.perf_counter() - start

print("Total async time:", elapsed, "seconds")

"""
The two coroutines can overlap their waiting period.

Mental model:

    Task A
       ↓
    await I/O
       ↓
    event loop works on Task B
       ↓
    Task B awaits
       ↓
    event loop resumes A when ready
"""


# ============================================================
# 27. FASTAPI-STYLE ASYNC MENTAL MODEL
# ============================================================

section("27. FASTAPI-STYLE ASYNC MENTAL MODEL")

"""
This is a simplified simulation of what an async backend
handler can conceptually look like.

Actual FastAPI behavior involves ASGI servers and an event loop.
"""

async def fake_database_query():
    print("Database query started")

    await asyncio.sleep(1)

    print("Database query completed")

    return {
        "id": 101,
        "name": "Raj"
    }


async def get_user():
    user = await fake_database_query()

    return user


user_result = asyncio.run(get_user())

print("API result:", user_result)

"""
Conceptual flow:

    HTTP request
          ↓
    FastAPI route
          ↓
    await database
          ↓
    waiting
          ↓
    event loop can run other tasks
          ↓
    database result
          ↓
    response
"""


# ============================================================
# 28. ASYNC DOES NOT MEAN CPU PARALLELISM
# ============================================================

section("28. ASYNC DOES NOT MEAN CPU PARALLELISM")

"""
This distinction is very important.

Async is excellent when tasks frequently WAIT.

Example:

    Database
    HTTP request
    Network
    File I/O

Async does not magically make a CPU-heavy Python loop
run on multiple CPU cores.
"""

async def cpu_heavy_task():
    total = 0

    for i in range(1_000_000):
        total += i * i

    return total


result = asyncio.run(cpu_heavy_task())

print("CPU result:", result)

print("""
Remember:

    async → concurrency for suitable waiting operations

    multiprocessing / suitable parallel execution
           → CPU parallelism
""")


# ============================================================
# 29. OBJECT IDENTITY DEMONSTRATION
# ============================================================

section("29. OBJECT IDENTITY")

first_list = [1, 2, 3]
second_list = first_list

print("first_list id:", id(first_list))
print("second_list id:", id(second_list))
print("Same object:", first_list is second_list)

second_list.append(4)

print("first_list:", first_list)
print("second_list:", second_list)


# ============================================================
# 30. SHALLOW COPY VS REFERENCE
# ============================================================

section("30. REFERENCE VS COPY")

original = [1, 2, 3]

reference = original
copy_list = original.copy()

reference.append(4)
copy_list.append(5)

print("Original:", original)
print("Reference:", reference)
print("Copy:", copy_list)

print("original is reference:", original is reference)
print("original is copy_list:", original is copy_list)

"""
Result conceptually:

    original  ─────┐
                   ▼
              [1,2,3,4]
                   ▲
    reference ────┘

    copy_list ───► [1,2,3,5]
"""


# ============================================================
# 31. NESTED MUTABLE OBJECT
# ============================================================

section("31. NESTED MUTABLE OBJECT")

user = {
    "name": "Raj",
    "skills": ["Python", "SQL"]
}

same_user = user

same_user["skills"].append("FastAPI")

print("user:", user)
print("same_user:", same_user)

"""
Because both variables refer to the same dictionary,
changing its nested list is visible through both references.
"""


# ============================================================
# 32. TUPLE CAN CONTAIN MUTABLE OBJECTS
# ============================================================

section("32. TUPLE WITH MUTABLE OBJECT")

"""
Important interview detail:

A tuple is immutable, but it can contain a mutable object.

"""

data = ([1, 2], "Python")

print("Before:", data)

data[0].append(3)

print("After:", data)

"""
The tuple's references cannot be replaced:

    data[0] = another_list

would fail.

But the list object referenced by data[0] can itself be
modified because the list is mutable.
"""


# ============================================================
# 33. FUNCTION PASSING — OBJECT REFERENCES
# ============================================================

section("33. FUNCTION ARGUMENTS")

def add_value(items):
    items.append(100)


numbers = [1, 2, 3]

print("Before function:", numbers)

add_value(numbers)

print("After function:", numbers)

"""
The function receives a reference to the same list object.

Therefore, mutating the list is visible outside the function.
"""


# ============================================================
# 34. REASSIGNMENT INSIDE FUNCTION
# ============================================================

section("34. REASSIGNMENT VS MUTATION")

def reassign_list(items):
    items = ["new", "list"]


def mutate_list(items):
    items.append("new")


numbers1 = [1, 2, 3]
numbers2 = [1, 2, 3]

reassign_list(numbers1)
mutate_list(numbers2)

print("After reassignment:", numbers1)
print("After mutation:", numbers2)

"""
Reassignment:

    items = [...]

changes what the local name points to.

Mutation:

    items.append(...)

changes the existing object.
"""


# ============================================================
# 35. HASHING WITH IMMUTABLE KEYS
# ============================================================

section("35. HASHABLE OBJECTS")

"""
Dictionary keys need to be hashable.

Strings, integers, and tuples containing hashable values
are common dictionary keys.
"""

data = {
    "name": "Raj",
    101: "User ID",
    (10, 20): "Point"
}

print(data)

"""
A list cannot be used as a dictionary key because a list
is mutable and therefore unhashable.
"""

try:
    invalid = {
        [1, 2]: "value"
    }
except TypeError as error:
    print("List cannot be a dictionary key:", error)


# ============================================================
# 36. COMPARING ALGORITHM GROWTH
# ============================================================

section("36. ALGORITHM GROWTH")

def constant_operation(items):
    return items[0]


def linear_operation(items):
    total = 0

    for item in items:
        total += item

    return total


def quadratic_operation(items):
    count = 0

    for first in items:
        for second in items:
            count += first + second

    return count


sample = list(range(100))

print("O(1):", constant_operation(sample))
print("O(n):", linear_operation(sample))
print("O(n²):", quadratic_operation(sample))

print("""
Growth:

    O(1)
      ↓
    O(log n)
      ↓
    O(n)
      ↓
    O(n log n)
      ↓
    O(n²)
      ↓
    O(2ⁿ)

The larger the input becomes, the more important
algorithmic complexity becomes.
""")


# ============================================================
# 37. BACKEND REQUEST SIMULATION
# ============================================================

section("37. BACKEND REQUEST SIMULATION")

"""
Simulate a simple backend route.

Real flow:

    Client
       ↓
    HTTP request
       ↓
    FastAPI
       ↓
    Python function
       ↓
    Database
       ↓
    Response

Here we simulate the Python/database portion.
"""

users_db = {
    1: {
        "id": 1,
        "name": "Raj",
        "role": "developer"
    },
    2: {
        "id": 2,
        "name": "Aman",
        "role": "designer"
    }
}


def get_user_from_database(user_id):
    return users_db.get(user_id)


def api_get_user(user_id):
    user = get_user_from_database(user_id)

    if user is None:
        return {
            "success": False,
            "message": "User not found"
        }

    return {
        "success": True,
        "data": user
    }


print("API response:")
print(api_get_user(1))

print("\nMissing user response:")
print(api_get_user(99))


# ============================================================
# 38. BACKEND DATA STRUCTURE CHOICE
# ============================================================

section("38. BACKEND DATA STRUCTURE CHOICE")

"""
Imagine we receive users from a database.
"""

users = [
    {"id": 1, "name": "Raj"},
    {"id": 2, "name": "Aman"},
    {"id": 3, "name": "Rohit"},
]

"""
If we repeatedly search by ID using the list:

    for user in users:
        if user["id"] == user_id:
            ...

that is O(n).

We can build a dictionary indexed by ID.
"""

users_by_id = {
    user["id"]: user
    for user in users
}

print("Users by ID:", users_by_id)

print("User 2:", users_by_id.get(2))

"""
Now average lookup by ID is O(1).

This is a practical example of why data structure
choice matters in backend development.
"""


# ============================================================
# 39. SIMPLE API CACHE MENTAL MODEL
# ============================================================

section("39. SIMPLE CACHE MENTAL MODEL")

cache = {}

def expensive_operation(user_id):
    print("Doing expensive work...")

    time.sleep(0.5)

    return {
        "user_id": user_id,
        "result": "computed"
    }


def get_cached_result(user_id):
    if user_id in cache:
        print("Cache hit")
        return cache[user_id]

    print("Cache miss")

    result = expensive_operation(user_id)

    cache[user_id] = result

    return result


print("First request:")
print(get_cached_result(1))

print("\nSecond request:")
print(get_cached_result(1))

"""
Mental model:

    Request
       ↓
    Cache lookup
       │
       ├── Hit → return cached value
       │
       └── Miss
             ↓
       expensive operation
             ↓
          save result
             ↓
          return result
"""


# ============================================================
# 40. REFERENCE COUNTING — CONCEPTUAL DEMONSTRATION
# ============================================================

section("40. REFERENCE COUNTING")

"""
CPython uses reference counting as an important memory
management mechanism.

The sys module can expose the reference count for an object,
but the exact observed count may include temporary/internal
references, so do not treat the number as a simple exact
"number of variables" value.
"""

import sys

object_value = []

print("Reference count:", sys.getrefcount(object_value))

another_reference = object_value

print("After another reference:", sys.getrefcount(object_value))

del another_reference

print("After deleting reference:", sys.getrefcount(object_value))


# ============================================================
# 41. GARBAGE COLLECTION
# ============================================================

section("41. GARBAGE COLLECTION")

"""
Python also has a garbage collector that helps deal with
reference cycles.

Example of a reference cycle:

    object A → object B
       ↑         │
       └─────────┘

The objects can refer to each other even when no outside
reference exists.

The garbage collector can detect and clean up certain
cyclic garbage.
"""

import gc

print("Garbage collector enabled:", gc.isenabled())

collected = gc.collect()

print("Objects collected during manual collection:", collected)


# ============================================================
# 42. INTERVIEW DEMO — ALL CORE CONCEPTS
# ============================================================

section("42. INTERVIEW DEMO")

print("""
If an interviewer asks:

"What happens when you run Python code?"

Answer:

    Python source code is parsed and represented as an AST.
    CPython compiles it into bytecode.
    The Python runtime executes that bytecode.
    The runtime ultimately relies on the operating system
    and CPU to perform the actual machine-level work.

If asked:

"What is a variable in Python?"

Answer:

    A variable is a name bound to an object.

If asked:

"What is mutable?"

Answer:

    A mutable object can be changed after creation.

If asked:

"What is the GIL?"

Answer:

    Traditional CPython uses a Global Interpreter Lock that
    allows only one thread at a time to execute Python bytecode
    within a single interpreter. This limits CPU-bound parallel
    execution using threads, while I/O concurrency is still
    possible.

If asked:

"Why use async?"

Answer:

    Async allows tasks that are waiting for I/O to give control
    back to the event loop so other tasks can make progress.

If asked:

"Why is dictionary lookup O(1)?"

Answer:

    Python dictionaries use hashing to map keys to storage
    locations, giving average constant-time lookup.

If asked:

"Why is def func(data=[]) dangerous?"

Answer:

    The default list is created when the function definition
    executes and can be reused across calls, causing shared
    mutable state.
""")


# ============================================================
# 43. FINAL MENTAL MODEL
# ============================================================

section("43. FINAL MENTAL MODEL")

print(r"""
                         PYTHON APPLICATION
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Source Code   │
                         │      .py        │
                         └────────┬────────┘
                                  │
                                  ▼
                             ┌─────────┐
                             │ Parser  │
                             └────┬────┘
                                  │
                                  ▼
                             ┌─────────┐
                             │   AST   │
                             └────┬────┘
                                  │
                                  ▼
                           ┌────────────┐
                           │  Compiler  │
                           └─────┬──────┘
                                 │
                                 ▼
                           ┌───────────┐
                           │ Bytecode  │
                           └─────┬─────┘
                                 │
                                 ▼
                     ┌─────────────────────┐
                     │   CPython Runtime   │
                     │    / Interpreter    │
                     └──────────┬──────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
            CPU-bound                      I/O-bound
                 │                             │
                 ▼                             ▼
             CPU work                     Waiting
                 │                             │
                 │                    ┌────────┴────────┐
                 │                    │                 │
                 │                    ▼                 ▼
                 │                 Database          API
                 │
                 ▼
              Result
                 │
                 └──────────────┬──────────────────────┘
                                │
                                ▼
                           HTTP Response
                                │
                                ▼
                              Client
""")


# ============================================================
# 44. QUICK REVISION
# ============================================================

section("44. QUICK REVISION")

revision = {
    "Execution": "Source → Parser → AST → Compiler → Bytecode → Runtime",
    "Variable": "Name/reference bound to an object",
    "Mutable": "Object can be changed after creation",
    "Immutable": "Object cannot be changed after creation",
    "==": "Value equality",
    "is": "Object identity",
    "GIL": "Traditional CPython lock around Python bytecode execution",
    "CPU-bound": "Mostly computation",
    "I/O-bound": "Mostly waiting for external resources",
    "async": "Efficient concurrency for suitable waiting operations",
    "List": "Ordered mutable sequence",
    "Tuple": "Ordered immutable sequence",
    "Set": "Unique hash-based collection",
    "Dictionary": "Key-value hash-based mapping",
    "O(1)": "Constant growth",
    "O(n)": "Linear growth",
    "O(log n)": "Logarithmic growth",
    "O(n²)": "Quadratic growth",
}

for concept, meaning in revision.items():
    print(f"{concept:15} → {meaning}")


# ============================================================
# END
# ============================================================

section("END OF PYTHON CORE FOUNDATIONS PLAYGROUND")

print("""
Recommended practice:

1. Run the entire file once.
2. Read one section at a time.
3. Change the values.
4. Predict the output before running.
5. Run it and compare.
6. Use print(), id(), type(), ast.dump(), and dis.dis()
   to inspect what Python is doing.
7. Then rebuild each example from memory.

Do not just memorize the output.

The goal is to understand the mental model behind the output.
""")
