# =====================================
# Identity vs Equality
# =====================================

list1 = [1, 2, 3]
list2 = [1, 2, 3]

print(list1 == list2) # True (The numbers inside are the same)
print(list1 is list2) # False (They are two completely separate lists in memory)

# =====================================
# Integer Caching 
# =====================================

a = 100
b = 100
print(a is b) # True (100 is inside the cache range)

x = 257
y = 257
print(x is y) # False (257 is outside the cache range, new memory created)

# =====================================
# String Interning
# =====================================

s1 = "hello_world"
s2 = "hello_world"
print(s1 is s2) # True (Python interns this string)

s3 = "hello world!"
s4 = "hello world!"
print(s3 is s4) # False (Contains space and punctuation, so new memory is created)

""" sys.intern() is a method that allows you to manually intern strings in Python. Interning means storing only one copy of each distinct string value, which must be immutable. This can save memory and speed up dictionary lookups."""

import sys

# Without intern: Python creates two separate memory objects
a = "New York, NY"
b = "New York, NY"
print(a is b) # False (in a dynamic/REPL environment)

# With intern: Python forces them to share the exact same memory address
c = sys.intern("New York, NY")
d = sys.intern("New York, NY")
print(c is d) # True