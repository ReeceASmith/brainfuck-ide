# Brainfuck IDE
#### A development environment for writing and debugging Brainfuck code
## What is Brainfuck IDE?
Brainfuck IDE is a Python 3.10 development environment built to help facilitate the writing and debugging of Brainfuck code.

## What features are included?
Brainfuck IDE includes many useful features that help with Brainfuck coding; with an output box; a list of memory locations and their values; error detection, catching, identification and location; and the option to step through code with a live view of the Brainfuck data pointer, memory locations and values, and current code execution position.
A full list of features can be found [here](https://github.com/ReeceASmith/brainfuck-ide/blob/main/features.md).

## How do I install?
Full instructions can be found [here](https://github.com/ReeceASmith/brainfuck-ide/blob/main/Install%20Instructions.md)  
Prerequisites:
- Python 3.10+ (may work with any Python <3.10 version - untested)
- Python tkinter
- Python ttk
- Windows 10 (may work with other Windows versions - untested)

Just copy the single "Brainfuck IDE.pyw" file to any location and run it standalone.

## Notes
- This project started as one quick program with a function plugged into it, with another plugged into it and so on; there are no classes or code organisation so code is very messy and slow, and is not optimised in any way.
- Version 1.0 is purely a base working program, nothing else.
- There are no comments within code as (one again) the intention was to create a working program.
- In future, I hope to clean up the code, and possibly re-write the full program to optimise execution and create cleaner code.

## About Brainfuck
Brainfuck is an esoteric programming language, not initially designed for any genuine programming, but it is fun to play around with.
Brainfuck uses 8 commands, a data pointer and a set of memory.
In this IDE, you can choose a number of memory locations equal to some power of 2 with a maximum of 2^16 (due to speed and performance limitations). It is suggested to use 2^8 memory locations.
Each memory location stores 0 <= values <= 255
The data pointer starts at memory location 0, and all memory locations are initialised at 0.

## Brainfuck Commands
*>* - Move the data pointer to the next (+1) memory location
*<* - Move the data pointed to the previous memory location
*+* - Increment the value at the currently selected memory location by 1
*-* - Decrement the value at the currently selected memory location by 1
*.* - Print the ASCII character with the value at the current memory location (65 prints "A")
*,* - Get a character input from the user and place the ASCII value of this character in the current memory location ("A" places 65)
*\[* - Start a loop, if the value at the current memory location is 0, skip the code to the matching closed bracket
*]* - If the value at the current memory location is not 0, skip the code back to the previous matching open bracket

## Brainfuck Program Examples
### Adding 2+5
```
++
>+++++
[
  <+>-
]<
```
The first line adds 2 to the first memory location  
The second line moves the data pointer to the next location and adds 5  
The third line starts a loop  
Line 4 move back, adds one, moves forward and subtracts one  
Line 5 moves the data pointer back to the result once the second memory location equals 0

### Hello World!
This Brainfuck code was taken from the official [Wikipedia page](https://en.wikipedia.org/wiki/Brainfuck#Hello_World!).
```
++++++++
[
  >++++
  [
    >++
    >+++
    >+++
    >+
    <<<<-
  ]
  >+
  >+
  >-
  >>+
  [<]
  <-
]

>>.
>---.+++++++..+++.
>>.
<-.
<.+++.------.--------.
>>+.
>++.
```
As seen, Brainfuck code can be quite extensive for simple tasks.
