# Brainfuck IDE Full Feature List
The Brainfuck IDE contains a number of features. All are listed here with descriptions.


## The Menu Bar
The menu bar hosts all of the app commands. Here you can:
#### File
- `New Ctrl+N` Create a new file
- `Open Ctrl+O` Open an existing `.bf` or `.b` file
- `Save Ctrl+S` Save the current file
- `Save As Ctrl+Alt+S` Save a file to a location with a name
- `Save Program Memory` Save a file with the current program memory data values as a `.txt` file
- `Exit Brainfuck IDE Ctrl+Q` Exit the program
#### Run
- `Run F5` Run the entire script
- `Step Forward F6` Step through one command in the code
Note: if the code is edited after stepping through, the `Step forward` command will start from the beginning of the program
#### Options
- `Set Memory Bytes` Set the number of memory locations the program can use
- `Reset Memory F9` Reset all memory to 0 and reset the Step so that code will start stepping from the first command
#### Help
- `About F1` About the program
- `About Brainfuck F2` About Brainfuck
- `Help F3` Program help
- `Brainfuck Help F4` Brainfuck help
- `my brain is fucked.` Easter egg

## IDE Window
The IDE window can be scaled to any size, and is split in four panes:
- The Code Box
- The Memory Box
- The Output Box
- The Quick Commands Box
These can be resized and are scrollable.  
The title of the window is the current open file location and name.  
A star \* is displayed if the file is unsaved or modified since opening.


## The Code Box
The code box is where Brainfuck code is written.
- Code is highlighted in blue when being stepped through, or when a specific character is causing an error.
  - This is especially useful when identifying issues with your code, as you can pin down where errors are coming from.  
- The code box is also scrollable and multiline.
  - The interpreter ignores whitespace, so you can make your code (somewhat) more readable.  
  
Note: When the interpreter comes across a loop where the current memory value is 0, it will still step through the commands in that loop, but will not process them, meaning plain text can be inserted into known '0' loops without producing errors.  
This will slow execution.


## The Memory Box
The memory box lists all of the memory locations available to the program.
- Each memory location has an address (though they are not addressable directly by Brainfuck and are not related to any locations within the RAM or CPU registers)
- Each location lists the current decimal value at that location
- The memory location currenly pointed to by the data pointer is highlighted in dark blue
- The memory box updates dynamically while stepping through code
  - This is especially useful for debugging and identifying logical or arithmetic errors


## The Output Box
The output box is where Brainfuck output and errors are displayed.
- Errors are displayed in red, stating the error location and type, and highlighting the problem character in the code box in blue.
- Code will still attempt to run if errors occur


## The Quick Commands Box
This box contains 4 most-used commands as buttons.
- `Run` the program in full
- `Step` through the code
- `Save` the file
- `Reset Memory` and reset the Step from the beginning of the code


## The Input Box
The input box appears when the code requires input from the user.
- It only accepts one ASCII character as input
- The decimal value of this character overwrites the currently selected memory location value


## The Save As Dialog
- These are regular Windows dialogs that only allow saving as a `.bf` or `.b` file (or `.txt` if saving memory values)
- If a user tries to `Save Ctrl+S` a new, unsaved file, they are prompted with the Save As dialog


## The Open Dialog
- A regular Windows dialog that only allows opening of `.bf` or `.b` files


## Keyboard Shortcuts
The user can use the shortcuts defined in the menu bar (Ctrl+S to save etc.).  
Other commands such as Ctrl+A/C/X/V can be used to select all, copy, cut and paste code into the code box.  
Ctrl+A/C can also be used to select all and copy in the Memory Box and Output Box.
