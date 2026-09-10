# How Python Actually Runs Your Code — A Complete, Interview-Ready Explanation

## The Short Answer (say this first in an interview)

Python is often called an "interpreted language," but that's only half the story. When you run a Python script, your code doesn't get executed directly as text. Instead, it goes through a **hybrid process**: your source code is first **compiled into bytecode**, and then that bytecode is **interpreted** by something called the Python Virtual Machine (PVM). So Python is best described as **compiled-then-interpreted**, not purely interpreted.

---

## The Full Pipeline, Step by Step

When you run `python script.py`, four things happen in order:

```
Your source code (.py)
        ↓
Parsed into an Abstract Syntax Tree (AST)
        ↓
Compiled into Bytecode
        ↓
Executed by the Python Virtual Machine (PVM)
```

Let's break down each step in plain language.

### Step 1: Parsing → Abstract Syntax Tree (AST)
Python reads your raw source text and figures out its grammatical structure — this is an assignment, this is a function definition, this is a loop, this is an if-statement. The result is a tree-like structure called an **AST**, which represents your code's structure rather than its raw text.

### Step 2: Compiling → Bytecode
The AST is then compiled into **bytecode** — a set of simple, low-level instructions (things like `LOAD_FAST`, `BINARY_OP`, `STORE_FAST`, `CALL`). Bytecode is not something a CPU understands directly; it's a Python-specific instruction format designed to be executed efficiently by Python's own virtual machine.

### Step 3: Execution → Python Virtual Machine (PVM)
The **PVM** — which is part of **CPython**, the standard Python implementation almost everyone uses — reads through these bytecode instructions and executes them one at a time. This is where your program actually runs.

**Important clarification:** bytecode is *not* the same as machine code. The PVM doesn't hand bytecode off to the CPU to "finally understand" — the PVM itself interprets each bytecode instruction, step by step. There's no separate step after this where "the computer understands it." The PVM is the thing doing the work, all the way through.

---

## Why Compile to Bytecode at All? (The Key Insight)

This is the question that trips people up, so let's be very precise about it.

You might think: "Why not just have Python read and execute the raw text line-by-line every time, like a very simple interpreter?" Here's the problem with that approach — and it has nothing to do with restarting your program later. It's about what happens **within a single run**, especially with loops and function calls.

### The core idea
**Parsing (text → AST) and compiling (AST → bytecode) happen once per piece of code — no matter how many times that code actually runs.**

This applies to:
- **Loops** — a loop body might run thousands of times, but it's parsed and compiled only once.
- **Function calls** — if you call the same function 500 times, its body was compiled once; each call just re-executes the same prepared bytecode.

If Python were a pure text interpreter with no bytecode step, it would have to re-parse and re-analyze the same lines of source text over and over on every single loop iteration or function call — repeating expensive work for no reason. Compiling once and reusing the result is what makes repeated execution fast.

### Seeing it for real

Here's actual proof, using Python's built-in `dis` module, which shows you the real bytecode behind a function:

```python
import dis

def loop_example():
    total = 0
    for i in range(3):
        total = total + i
    return total

dis.dis(loop_example)
```

Output:
```
  3           0 RESUME                   0

  4           2 LOAD_CONST               1 (0)
              4 STORE_FAST               0 (total)

  5           6 LOAD_GLOBAL              1 (NULL + range)
             16 LOAD_CONST               2 (3)
             18 CALL                     1
             26 GET_ITER
        >>   28 FOR_ITER                 7 (to 46)
             32 STORE_FAST               1 (i)

  6          34 LOAD_FAST                0 (total)
             36 LOAD_FAST                1 (i)
             38 BINARY_OP                0 (+)
             42 STORE_FAST               0 (total)
             44 JUMP_BACKWARD            9 (to 28)

  5     >>   46 END_FOR

  7          48 LOAD_FAST                0 (total)
             50 RETURN_VALUE
```

### Reading this output like an engineer

Two things to notice:

**1. `JUMP_BACKWARD` is the loop, not re-parsing.**
Instruction `44 JUMP_BACKWARD 9 (to 28)` literally tells the PVM: "go back to instruction 28 and run this block again." It does not say "go re-read the source text." The instructions between 28 and 44 (`LOAD_FAST`, `BINARY_OP`, `STORE_FAST`) were generated **once**, and the loop is just the PVM jumping back and forth between them, reusing the exact same instructions with new data (`i`) each time.

**2. `range(3)` only appears once — because it's outside the repeating block.**
Look at instruction `18 CALL 1` — that's the `range(3)` call. It appears **before** the jump target (`>> 28`), meaning it sits *outside* the section the PVM repeatedly jumps back into. Python evaluates `range(3)` exactly once, gets an iterator from it (`GET_ITER`), and then on every pass, `FOR_ITER` simply asks that same iterator for its next value — it never calls `range()` again.

Meanwhile, `BINARY_OP` (the `+` in `total = total + i`) sits **inside** the repeating section (between instructions 28 and 44), so it genuinely runs fresh on every single loop pass.

**The takeaway:** the bytecode structure directly reflects your source code's structure — what's written outside the loop body (setup, evaluated once) versus what's written inside it (repeated, evaluated every pass).

---

## Bytecode vs Machine Code — Going Deeper

This is a distinction worth getting completely solid, because it's easy to confuse the two.

### What is bytecode, actually?

Bytecode is a set of **low-level, simplified instructions** that represent what your Python code does — but it's not tied to any specific physical CPU. Think of it as Python's own private instruction language, designed specifically to be read and executed by the **Python Virtual Machine (PVM)**.

Each bytecode instruction is small and simple — "load this variable," "add these two values," "call this function," "jump back to this point." You've already seen real examples of this:

```
LOAD_FAST    0 (total)
LOAD_FAST    1 (i)
BINARY_OP    0 (+)
STORE_FAST   0 (total)
```

That's bytecode. It's stored in a compact binary format (hence "byte" in bytecode) — not human-readable text like your `.py` file, but also not something a CPU can run directly either. It sits in between the two.

### Bytecode vs Machine Code — the actual difference

| | Bytecode | Machine Code |
|---|---|---|
| **Who executes it** | The Python Virtual Machine (software) | The CPU (hardware), directly |
| **Is it platform-specific?** | No — the same bytecode format works on Windows, Mac, or Linux, as long as CPython is installed | Yes — machine code is specific to a CPU architecture (x86, ARM, etc.) |
| **How it runs** | Interpreted — the PVM reads each instruction and performs the corresponding action in software | Executed directly by CPU circuits — no interpreter needed |
| **Speed** | Slower — there's a software layer in between | Faster — no middleman |
| **Example instruction** | `BINARY_OP` (add two values) | An actual CPU opcode, e.g. `ADD` in x86 assembly |

The key idea: **machine code is the actual language a CPU understands and runs natively.** Bytecode is *not* that — it's a Python-specific format that requires the PVM (a program itself, written in C) to interpret it and translate each instruction's meaning into real actions. Your bytecode itself never *becomes* a CPU instruction; it stays bytecode, and the PVM keeps interpreting it fresh every time the program runs.

This is also *why* Python is portable — the same `.pyc` bytecode can run on any machine with a compatible Python interpreter installed, regardless of CPU architecture, because bytecode was never tied to a specific CPU in the first place.

### Why does this make Python slower than a fully compiled language?

In a language like C, the compiler translates your code **directly into native machine code**, ahead of time. When you run the program, the CPU executes those instructions **directly** — no middleman, no translation happening during execution.

In Python, even after compiling to bytecode, the **PVM still sits in between** your bytecode and the CPU. Every single bytecode instruction has to be read and interpreted by the PVM *every time* it runs — that interpretation step is real, ongoing overhead that a fully compiled language doesn't have, because its "interpretation" already happened once, permanently, at compile time.

**The takeaway:** Python sits in the middle of a spectrum — faster than a pure text interpreter (thanks to compiling to bytecode once), but slower than a language that compiles straight to machine code (because the PVM still has to interpret that bytecode on every run). That extra software layer — the PVM interpreting bytecode — is exactly why Python trades some raw speed for portability and flexibility.

### Why was the AST created? (Why not go straight from text to bytecode?)

Going from raw text directly to bytecode in one step would actually be messier than doing it in two clean stages. Here's why the AST exists as a middle step:

1. **Parsing text into structure is a different problem from generating instructions.** The AST's only job is to answer: "what does this code *mean*, grammatically?" — is this an assignment, a function call, an if-statement, a loop? It turns flat, ambiguous text into a structured tree that represents your code's logical shape, unambiguously.

2. **Once you have a clean structural tree, generating bytecode becomes straightforward.** The compiler can walk through the AST node by node ("this node is an addition — emit a `BINARY_OP` instruction") without simultaneously worrying about parsing grammar. Separating "understand the structure" from "generate instructions" keeps each stage simpler and more reliable.

3. **The AST is useful on its own too**, independent of bytecode generation — tools that check code style, catch syntax errors, or analyze code for issues often work directly on the AST, because it's a clean structural representation, not raw text.

**In short:** text is messy and ambiguous to work with directly; a tree structure is clean and unambiguous. Parsing text into structure (AST) and converting structure into instructions (bytecode) are genuinely different jobs — separating them makes each one simpler and more reliable than trying to do both at once.

### Why bytecode at all? (Why not execute straight from the AST?)

This connects back to the core efficiency idea from earlier in this document: bytecode exists so the **expensive analysis work** (parsing + understanding structure) only has to happen **once**, while the **cheap execution work** (running simple instructions) can happen **as many times as needed** — once per loop iteration, once per function call — without redoing the expensive part.

If Python executed directly from the AST every time (walking a tree structure on every single loop iteration), that would be slower and more wasteful than running a flat list of simple, pre-generated instructions repeatedly. Bytecode is a compact, efficient form specifically designed *for repeated execution* — that's its whole purpose.

---

## File Extensions, Demystified

| Extension | What it is |
|---|---|
| `.py` | Your source code — plain text, human-readable |
| `.pyc` | Compiled bytecode, automatically cached in a `__pycache__` folder |
| *(none)* | Python does **not** produce a standalone `.exe`-style executable by default — it always needs the Python interpreter present to run |

**Important nuance:** `.pyc` caching happens when a module is **imported**, not when you run a script directly with `python script.py`. This distinction is easy to miss but matters in practice.

### Two separate "reuse" mechanisms — don't confuse these

It's easy to blur these two ideas together, so keep them clearly separate:

1. **Within a single run:** bytecode is compiled once, then reused for every loop iteration or function call *in that same run*. This is the mechanism explained above with `JUMP_BACKWARD`.

2. **Across separate runs (different days, different program executions):** when you `import` a module, Python saves its bytecode to a `.pyc` file. The next time you run your program, Python checks whether the source file has changed (using timestamps/hashing). If it hasn't changed, Python skips re-parsing and re-compiling entirely and loads the saved `.pyc` bytecode directly — saving startup time.

Both mechanisms are about "don't redo work that's already been done," but one operates *inside* a running program (loops/function calls), and the other operates *between* separate runs of your program (the `.pyc` cache).

---

## Why This Matters Practically

Understanding this pipeline explains several things you'll run into as a working developer:

- **Startup overhead:** Python programs have a small delay before running because of the parse-and-compile step (though `.pyc` caching reduces this for imported modules on repeat runs).
- **The `__pycache__` folder:** now you know exactly why it exists and what's inside it.
- **Stale-cache confusion:** occasionally, editing an imported module and not seeing changes reflected can trace back to this caching mechanism — knowing it exists helps you debug that scenario instead of being confused by it.
- **Why Python is flexible but not the fastest for raw computation:** the interpretation step (executing bytecode instruction-by-instruction via the PVM) has real overhead compared to a fully compiled language producing native machine code directly. This is also foundational context for later topics like the GIL and Python's concurrency model.

---

## Interview-Ready Summary (memorize this version)

> "Python isn't purely interpreted — it's a hybrid. When you run a script, Python first parses your source code into an Abstract Syntax Tree, then compiles that AST into bytecode. That bytecode is then executed by the Python Virtual Machine, which is part of CPython, the standard Python implementation. The key reason for this two-step process is efficiency: parsing and compiling only happen once per piece of code, no matter how many times it actually runs — so a loop that executes 10,000 times, or a function called 500 times, only gets parsed and compiled once, and then the PVM just re-executes the already-prepared bytecode instructions repeatedly. You can actually see this by using Python's `dis` module — it shows real bytecode, including jump instructions that make loops work by reusing the same instructions rather than reading the source text again."

---

## Quick Self-Check Questions

Test yourself with these before moving on:

1. What are the four stages code goes through when you run `python script.py`?
2. What's the difference between bytecode and machine code?
3. Why does compiling to bytecode make loops and repeated function calls faster than pure text interpretation would?
4. What's the difference between the `.pyc` caching mechanism and the "compile once, execute repeatedly" behavior within a single loop?
5. When does a `.pyc` file get created — on every script run, or only in a specific circumstance?

*(Answers are all covered above — if any of these feel shaky, that's exactly where to re-read.)*