# Imports
import tkinter as tk
import tkinter.filedialog
import ttk
import os
import sys
appfolder = os.getenv("LOCALAPPDATA") + "\\BFIDE\\"


#################
# Program Start #
#################

def start():
    global appfolder
    global appVars
    global fileSaved
    fileSaved = False

    try:
        file = open(appfolder + "data.dat", "r")
        fileData = file.readlines()
        file.close()

        appVars = {}
        for line in fileData:
            if line[-1] == "\n":
                line = line[:-1]
            try:
                (varname, varval) = line.split("=")
                appVars[varname] = varval
            except: pass

        try:
            appVars["memoryBits"]
        except:
            appVars["memoryBits"] = 0
        getMemoryBits()
            
    except FileNotFoundError:
        try: os.mkdir(appfolder)
        except FileExistsError: pass

        file = open(appfolder + "data.dat", "x")
        file.write("memoryBits=256\n")
        file.close()

        getNewMemoryBits()
        


###################
# Get Memory Bits #
###################

def getNewMemoryBits(key=""):
    global appVars
    global window

    try: window.destroy()
    except: pass

    try: appVars["memoryBits"] = 0
    except: appVars = {"memoryBits":0}
    
    getMemoryBits()

def getMemoryBits(key=""):
    global appfolder
    global appVars
    global window
    
    if appVars["memoryBits"] == 0:
        window = tk.Tk(className=" Set Memory Bits")
        window.geometry("300x100")
        window.rowconfigure(0, weight=1)
        window.rowconfigure(1, weight=1)
        window.rowconfigure(2, weight=1)
        window.columnconfigure(0, weight=1)

        window.bind("<Return>", startInitialization)

        labelMem = tk.Label(window, text="Number of Memory Bytes 2^n\n(default is 2^8, 256):")
        labelMem.grid(row=0, column=0)

        global entryMem
        entryMem = tk.Entry(window)
        entryMem.insert(tk.END, "8")
        entryMem.grid(row=1, column=0)

        button = tk.Button(window, text="Enter", command=startInitialization, width=8)
        button.grid(row=2, column=0)

        entryMem.focus()
    else:
        try:
            appVars["memoryBits"] = int(appVars["memoryBits"])
            if appVars["memoryBits"] > 2**16:
                appVars["memoryBits"] = 2**16
        except:
            appVars["memoryBits"] = 256
        initializeProgram()



###############################
###############################

#######################
# Brainfuck Functions #
#######################

def validateBFInput(P, D):
    global inputEntry
    
    if D == "0":
        return True
    
    try:
        P.encode("ascii")
        if len(P) <= 1:
            return True
        else:
            return False
    except:
        inputEntry.delete(0, tk.END)
        return False


def exeBF(bfcode, memoryPos, ifLoopPos, skipCommand, currentChar):
    global appVars
    global outputBox

    i = currentChar
    bfChars = [
        ">", "<",
        "+", "-",
        ",", ".",
        "[", "]",
        " "
    ]
    
    char = bfcode[i]
    if skipCommand:
        if char == "]":
            skipCommand = False
            ifLoopPos = ifLoopPos[:-1]
        i += 1
        currentChar = i
    else:
        if char not in bfChars:
            outputBox.insert(tk.END, f"\nError at char {i}    |    {char} is not a valid operator.\n", "error")
            selectChar(i)
        else:
            if char == ">":
                if memoryPos == (appVars["memoryBits"] - 1):
                    outputBox.insert(tk.END, f"\nError at char {i}    |    Cannot move pointer; memory limit reached\n", "error")
                    selectChar(i)
                else:
                    memoryPos += 1
            elif char == "<":
                if memoryPos == 0:
                    outputBox.insert(tk.END, f"\nError at char {i}    |    Cannot move pointer; memory limit reached\n", "error")
                    selectChar(i)
                else:
                    memoryPos -= 1
            elif char == "+":
                if appVars["memory"][memoryPos] == 255:
                    outputBox.insert(tk.END, f"\nError at char {i}    |    Cannot increment memory bit, ASCII limit reached at memory position {memoryPos}\n", "error")
                    selectChar(i)
                else:
                    appVars["memory"][memoryPos] += 1
            elif char == "-":
                if appVars["memory"][memoryPos] == 0:
                    outputBox.insert(tk.END, f"\nError at char {i}    |    Cannot decrement memory bit, ASCII limit reached at memory position {memoryPos}\n", "error")
                    selectChar(i)
                else:
                    appVars["memory"][memoryPos] -= 1
            elif char == ".":
                outputBox.insert(tk.END, chr(appVars["memory"][memoryPos]))
            elif char == ",":
                global window
                global inputWindow
                
                inputWindow = tk.Toplevel()
                inputWindow.geometry("200x100")
                inputWindow.rowconfigure(0, weight=1)
                inputWindow.rowconfigure(1, weight=1)
                inputWindow.rowconfigure(2, weight=1)
                inputWindow.columnconfigure(0, weight=1)
                inputWindow.attributes("-topmost", "true")

                inputLabel = tk.Label(inputWindow, text="Input:")
                inputLabel.grid(row=0, column=0)


                global inputEntry
                inputEntry = tk.Entry(inputWindow, validate="key", validatecommand=(inputWindow.register(validateBFInput), "%P", "%D"), width=4)
                inputEntry.grid(row=1, column=0)

                inputButton = tk.Button(inputWindow, text="Enter", command=getInput, width=8)
                inputButton.grid(row=2, column=0)
                
                inputWindow.bind("<Return>", lambda x: getInput(x, memoryPos))
                inputEntry.focus()
                
                window.wait_window(inputWindow)
                
            elif char == "[":
                if appVars["memory"][memoryPos] == 0 or skipCommand:
                    skipCommand = True
                ifLoopPos.append(i)
            elif char == "]":
                try:
                    if appVars["memory"][memoryPos] != 0:
                        i = ifLoopPos[-1] - 1
                    ifLoopPos = ifLoopPos[:-1]
                except:
                    outputBox.insert(tk.END, f"\nError at char {i}    |    Attempted to close non-existent loop\n", "error")
                    selectChar(i)
            
            i += 1
            currentChar = i
    return memoryPos, ifLoopPos, skipCommand, currentChar


def resetMemory(key=""):
    global codeBox
    global outputBox
    global memoryBox
    global appVars
    global stepVars
    

    stepVars = {
        "bfcode":"",
        "bfChars":[
            ">", "<",
            "+", "-",
            ".", ",",
            "[", "]"
        ],
        "memoryPos":0,
        "ifLoopPos":[],
        "skipCommand":False,
        "currentChar":0
    }

    try: codeBox.tag_remove("start", "1.0", tk.END)
    except: pass
    
    outputBox.delete("1.0", tk.END)
    outputBox.insert(tk.END, ">")

    for i in range(len(appVars["memory"])):
        appVars["memory"][i] = 0
    updateMemoryBox(0)
        


def stepBF(key=""):
    global codeBox
    global outputBox
    global memoryBox
    global memoryPos
    global appVars
    global stepVars

    try: codeBox.tag_remove("start", "1.0", tk.END)
    except: pass

    newbfcode = codeBox.get("1.0", tk.END).replace("\n", "")
    if stepVars["bfcode"] != newbfcode:
        resetMemory()
    stepVars["bfcode"] = newbfcode


    if stepVars["currentChar"] != len(stepVars["bfcode"]):
        selectChar(stepVars["currentChar"])
        stepVars["memoryPos"], stepVars["ifLoopPos"], stepVars["skipCommand"], stepVars["currentChar"] = exeBF(stepVars["bfcode"], stepVars["memoryPos"], stepVars["ifLoopPos"], stepVars["skipCommand"], stepVars["currentChar"])


        updateMemoryBox(stepVars["memoryPos"])
    else:
        try: codeBox.tag_remove("start", "1.0", tk.END)
        except: pass



def selectChar(charNum):
    global codeBox
    
    bfcodeRaw = codeBox.get("1.0", tk.END)
    i = charNum
    totalPos = 0
    charLine = 1
    charPos = 0
    
    while totalPos < i:
        if bfcodeRaw[totalPos+1] == "\n":
            charLine += 1
            charPos = -1
            i += 1
        elif bfcodeRaw[totalPos] == " ":
            charPos += 1
        else:
            charPos += 1
        totalPos += 1

    codeBox.tag_add("start", f"{charLine}.{charPos}", f"{charLine}.{charPos+1}")
    codeBox.tag_config("start", background="blue", foreground="white")



def runBF(key=""):
    global codeBox
    global outputBox
    global memoryBox
    global appVars


    outputBox.delete("1.0", tk.END)
    outputBox.insert(tk.END, ">")

    bfcode = codeBox.get("1.0", tk.END).replace("\n", "")

    bfChars = [
        ">", "<",
        "+", "-",
        ".", ",",
        "[", "]"
    ]
    memoryPos = 0
    ifLoopPos = []
    skipCommand = False
    for i in range(appVars["memoryBits"]):
        appVars["memory"][i] = 0
    


    global currentChar
    i = 0
    while i < len(bfcode):
        currentChar = i
        memoryPos, ifLoopPos, skipCommand, currentChar = exeBF(bfcode, memoryPos, ifLoopPos, skipCommand, currentChar)
        i = currentChar
        

    if len(ifLoopPos) > 0:
        outputBox.insert(tk.END, f"\nError at char {ifLoopPos[-1]}    |    Loop was never closed\n", "error")
        print(ifLoopPos[-1])
        selectChar(ifLoopPos[-1])
        


    updateMemoryBox(memoryPos)



def getInput(key="", memoryPos=0):
    global inputWindow
    global inputEntry
    
    try: appVars["memory"][memoryPos] = ord(inputEntry.get())
    except: pass

    updateMemoryBox(memoryPos)

    inputEntry.destroy()
    inputWindow.destroy()
    inputWindow.update()



def updateMemoryBox(memoryPos):
    memoryBox.config(state=tk.NORMAL)
    memoryBox.delete("1.0", tk.END)
    for i in range(len(appVars["memory"])):
        memoryBox.insert(tk.END, f"Memory {i}\t\t|    " + str(appVars["memory"][i]) + "\n")
    memoryBox.config(state=tk.DISABLED)
    memoryBox.tag_add("start", f"{memoryPos+1}.0", f"{memoryPos+1}.0 lineend")
    memoryBox.tag_config("start", background="darkblue", foreground="white")




##################
# Menu Functions #
##################

def doNothing(key=""):
    pass


def switchButton(key=""):
    global warningWindow
    global yBtn
    global nBtn
    
    if warningWindow.focus_get() == nBtn and key.keycode == 37:
        yBtn.focus()
    elif warningWindow.focus_get() == yBtn and key.keycode == 39:
        nBtn.focus()


def pressButton(key=""):
    global warningWindow
    global yBtn
    global nBtn

    if warningWindow.focus_get() == nBtn:
        quitNoSave()
    else:
        quitSave()


def quitSave(key=""):
    global warningWindow
    try:
        global window
        global inputWindow
    except: pass

    warningWindow.destroy()
    warningWindow.update()
    saveFile()

    safeQuit()


def quitNoSave(key=""):
    global warningWindow
    try:
        global window
        global inputWindow
    except: pass

    warningWindow.destroy()
    warningWindow.update()

    safeQuit()


def safeQuit():
    global appfolder
    file = open(appfolder + "data.dat", "w")
    for varname in appVars:
        if varname != "memory":
            file.write(varname + "=" + str(appVars[varname]) + "\n")
    file.close()
    
    try:
        global inputWindow
        inputWindow.destroy()
        inputWindow.update()
    except: pass
    try:
        global window
        window.destroy()
        window.update()
    except: pass
    sys.exit(0)


def quitBF(key=""):
    if not fileSaved:
        global window
        global warningWindow
        warningWindow = tk.Toplevel()
        warningWindow.geometry("200x80")
        warningWindow.rowconfigure(0, weight=1)
        warningWindow.rowconfigure(1, weight=1)
        warningWindow.columnconfigure(0, weight=1)
        warningWindow.columnconfigure(1, weight=1)
        warningWindow.attributes("-topmost", "true")

        warningWindow.bind("<Left>", switchButton)
        warningWindow.bind("<Right>", switchButton)
        warningWindow.bind("<Return>", pressButton)
        

        label = tk.Label(warningWindow, text="Save before exit?")
        label.grid(row=0, column=0, columnspan=2)

        global yBtn
        yBtn = tk.Button(warningWindow, text="Yes", command=quitSave, width=8)
        yBtn.grid(row=1, column=0)

        global nBtn
        nBtn = tk.Button(warningWindow, text="No", command=quitNoSave, width=8)
        nBtn.grid(row=1, column=1)
        nBtn.focus()
        
        window.wait_window(warningWindow)
        
    else:
        safeQuit()
        

def newFile(key=""):
    global codeBox
    global codeBoxContent
    global fileSaved
    global currentFilepath
    
    resetMemory()
    codeBox.delete("1.0", tk.END)
    codeBox.focus()

    currentFilepath = ""
    
    fileSaved = False
    window.winfo_toplevel().title(currentFilepath + "*")
    codeBoxContent = ""


def openFile(key="", start=False):
    global codeBox
    global codeBoxContent
    global currentFilepath
    global fileSaved
    
    codeBox.delete("1.0", tk.END)

    if not start:
        currentFilepath = tk.filedialog.askopenfilename(filetypes=(("Brainfuck files", "*.b"), ("Brainfuck files", "*.bf")))

    try:
        appVars["lastFilepath"] = currentFilepath
        global appfolder
        file = open(appfolder + "data.dat", "w")
        for varname in appVars:
            if varname != "memory":
                file.write(varname + "=" + str(appVars[varname]) + "\n")
        file.close()
        
        file = open(currentFilepath, "r")
        codeBox.insert(tk.END, file.read())
        file.close()
        fileSaved = True
        window.winfo_toplevel().title(currentFilepath)
        codeBoxContent = codeBox.get("1.0", tk.END)
    except e: print(e)


def saveFile(key=""):
    global currentFilepath
    global fileSaved
    global codeBox
    global codeBoxContent
    
    try:
        file = open(currentFilepath, "w")
        file.write(codeBox.get("1.0", tk.END)[:-1])
        file.close()
        fileSaved = True
        window.winfo_toplevel().title(currentFilepath)
        codeBoxContent = codeBox.get("1.0", tk.END)
    except FileNotFoundError:
        saveFileAs()


def saveFileAs(key=""):
    global codeBox
    global codeBoxContent
    global appVars
    global currentFilepath
    global fileSaved

    newFilepath = tk.filedialog.asksaveasfilename(filetypes=(("Brainfuck files", "*.b"), ("Brainfuck files", "*.bf")))

    try:
        if not (newFilepath[-3:] == ".bf" or newFilepath[-2:] == ".b"):
            newFilepath += ".bf"
        file = open(newFilepath, "w")
        file.write(codeBox.get("1.0", tk.END)[:-1])
        file.close()
        currentFilepath = newFilepath
        appVars["lastFilepath"] = currentFilepath

        global appfolder
        file = open(appfolder + "data.dat", "w")
        for varname in appVars:
            if varname != "memory":
                file.write(varname + "=" + str(appVars[varname]) + "\n")
        file.close()
        
        fileSaved = True
        window.winfo_toplevel().title(currentFilepath)
        codeBoxContent = codeBox.get("1.0", tk.END)
    except: pass


def saveProgramMemory(key=""):
    global appVars
    
    filepath = tk.filedialog.asksaveasfilename(filetypes=(("Text file", "*.txt"), ("Data file", "*.dat")))

    try:
        print(appVars["memory"])
        if not (filepath[-4:] == ".txt" or filepath[-4:] == ".dat"):
            filepath += ".txt"
        file = open(filepath, "w")
        for x in appVars["memory"][:-1]:
            file.write(str(x)+"\n")
        file.write(appVars["memory"][-1])
        file.close()
    except: pass


def fileModified(key=""):
    global window
    global currentFilepath
    global fileSaved
    global codeBox
    global codeBoxContent
    global memoryBox

    if codeBox.get("1.0", tk.END) != codeBoxContent:
        window.winfo_toplevel().title(currentFilepath + "*")
        fileSaved = False
        if (key.keycode != 117): codeBox.tag_delete("start")
    else:
        window.winfo_toplevel().title(currentFilepath)
        fileSaved = True
    


def showAbout(key=""):
    aboutWindow = tk.Toplevel()
    aboutWindow.geometry("400x150")
    aboutWindow.columnconfigure(0, weight=1)


    label = tk.Label(aboutWindow, text="About Brainfuck IDE", font="Arial 16 bold")
    label.grid(row=0, column=0)

    sep = ttk.Separator(aboutWindow, orient=tk.HORIZONTAL)
    sep.grid(row=1, column=0, sticky="we", padx=20)



    label = tk.Label(aboutWindow, justify=tk.CENTER, wraplength=360, font="TkDefaultFont 10 bold", text="Developed in full by Reece Smith, 2022")
    label.grid(row=2, column=0, padx=20)

    sep = ttk.Separator(aboutWindow, orient=tk.HORIZONTAL)
    sep.grid(row=3, column=0, sticky="we", padx=20)
    
    label = tk.Label(aboutWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9", text="This Brainfuck IDE was developed in full by Reece Smith using Python 3.10.7 and tkinter interface package on Windows 10, for Windows devices.")
    label.grid(row=4, column=0, padx=20)
    
    label = tk.Label(aboutWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9 bold", text="Version 1.0")
    label.grid(row=5, column=0, padx=20)


    
    aboutWindow.attributes("-topmost", "true")


def showHelp(key=""):
    helpWindow = tk.Toplevel()
    helpWindow.geometry("800x700")
    helpWindow.columnconfigure(0, weight=1)
    helpWindow.columnconfigure(1, weight=1)


    label = tk.Label(helpWindow, text="Help", font="Arial 16 bold")
    label.grid(row=0, column=0, columnspan=2)

    sep = ttk.Separator(helpWindow, orient=tk.HORIZONTAL)
    sep.grid(row=1, column=0, columnspan=2, sticky="we", padx=20)



    label = tk.Label(helpWindow, justify=tk.CENTER, wraplength=360, font="TkDefaultFont 10 bold", text="The interface is split into four re-sizeable sections.")
    label.grid(row=2, column=0, padx=20)


    labelData = [
        [
            "Top Left: The code box",
            "This is where you can input your brainfuck code. You can also use newlines and space characters, but anything else will return an error. You can use Ctrl+A to select all text, Ctrl+C and Ctrl+V to copy and paste and Ctrl+X to cut. If any errors occur, they will be highlighted in blue. If you step through your code, the previously executed command is also highlighted in blue."
        ],

        [
            "Top Right: The memory data box",
            "Here you can view the memory your program stores. It shows the address of each memory slot on the left and its value on the right. The memory location that your program is currently pointing to is highlighted in blue. If you step through your code, you can see the memory changing as the code executes."
        ],

        [
            "Bottom Left: The output console",
            "Any output created by your program is shown here. If any errors occur, the error type and character number causing the problem is shown here, and the problem character is highlighted in blue in the code box above."
        ],

        [
            "Bottom Right: The quick commands box",
            "Here there are four buttons. The \"Run\" button will run your program, while the \"Step\" button steps through your code one command at a time. You can also Save your code and reset your program memory (if you are stepping through your code and need to start over."
        ]
    ]

    rownum = 3
    for i in range(len(labelData)):
        sep = ttk.Separator(helpWindow, orient=tk.HORIZONTAL)
        sep.grid(row=rownum, column=0, sticky="we", padx=20)
        
        label = tk.Label(helpWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9 bold", text=labelData[i][0])
        label.grid(row=rownum+1, column=0, padx=20, pady=10)
        label = tk.Label(helpWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9", text=labelData[i][1])
        label.grid(row=rownum+2, column=0, padx=20, pady=10)
        rownum += 3



    label = tk.Label(helpWindow, justify=tk.CENTER, wraplength=360, font="TkDefaultFont 10 bold", text="The menu bar is very useful and contains many features. Keyboard shortcuts are shown beside each menu function that has a shortcut.")
    label.grid(row=2, column=1, padx=20)

    sep = ttk.Separator(helpWindow, orient=tk.HORIZONTAL)
    sep.grid(row=3, column=1, sticky="we", padx=20)


    labelData = [
        [
            "File Submenu",
            "Here you can create new files, open existing files, save a current file or save as a new file. You can also save your program's current memory to a separate file, and exit the program from here."
        ],

        [
            "Run Submenu",
            "Here you can either run your program in full, or step forward one command at a time. Both will update the memory box on the right as the data is changed, and stepping through your code will highlight the previously executed command."
        ],

        [
            "Options Submenu",
            "The amount of memory your program stores can be changed here. You can also reset your program memory if you are stepping through your code and need to clear the program."
        ],

        [
            "Help Submenu",
            "This submenu shows help windows. The \"About\" section shows a window giving information about the program, while the \"Help\" section shows this window. \"Brainfuck Help\" shows a list of commands you can use in Brainfuck and what they do. You can access any of these windows at any time, and they will always stay on top of any other windows so you can easily reference them while coding."
        ]
    ]

    rownum = 3
    for i in range(len(labelData)):
        sep = ttk.Separator(helpWindow, orient=tk.HORIZONTAL)
        sep.grid(row=rownum, column=1, sticky="we", padx=20)
        
        label = tk.Label(helpWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9 bold", text=labelData[i][0])
        label.grid(row=rownum+1, column=1, padx=20, pady=10)
        label = tk.Label(helpWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9", text=labelData[i][1])
        label.grid(row=rownum+2, column=1, padx=20, pady=10)
        rownum += 3

    
    helpWindow.attributes("-topmost", "true")


def openLink(link="https://en.wikipedia.org/wiki/Brainfuck"):
    import webbrowser
    webbrowser.open_new(link)


def showBFAbout(key=""):
    bfAboutWindow = tk.Toplevel()
    bfAboutWindow.geometry("400x250")
    bfAboutWindow.columnconfigure(0, weight=1)
    bfAboutWindow.rowconfigure(5, weight=1)


    label = tk.Label(bfAboutWindow, text="About Brainfuck", font="Arial 16 bold")
    label.grid(row=0, column=0)

    sep = ttk.Separator(bfAboutWindow, orient=tk.HORIZONTAL)
    sep.grid(row=1, column=0, sticky="we", padx=20)
    
    label = tk.Label(bfAboutWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9", text="Urban Müller created Brainfuck in 1993 to challenge and amuse programmers.")
    label.grid(row=2, column=0, padx=20)
    label = tk.Label(bfAboutWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9", text="The name \"Brainfuck\" refers to how complex the thought processes are to create even simple programs with the language. Brainfuck is noted for how extremely minimalistic it is, using only 8 commands.")
    label.grid(row=3, column=0, padx=20)
    label = tk.Label(bfAboutWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9", text="Brainfuck is turing complete, meaning it can (theoretically) replicate or simulate any computer system, albeit completely impractical.")
    label.grid(row=4, column=0, padx=20)

    label = tk.Label(bfAboutWindow, cursor="hand2", foreground="blue", justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9 underline bold", text="https://en.wikipedia.org/wiki/Brainfuck")
    label.grid(row=5, column=0, padx=20, pady=2)
    label.bind("<Button-1>", lambda x: openLink("https://en.wikipedia.org/wiki/Brainfuck"))


    
    bfAboutWindow.attributes("-topmost", "true")


def showBFHelp(key=""):
    bfHelpWindow = tk.Toplevel()
    bfHelpWindow.geometry("650x390")
    bfHelpWindow.columnconfigure(0, weight=1)
    bfHelpWindow.columnconfigure(1, weight=1)
    bfHelpWindow.columnconfigure(2, weight=1)


    label = tk.Label(bfHelpWindow, text="Brainfuck Help", font="Arial 16 bold")
    label.grid(row=0, column=0, columnspan=3)

    sep = ttk.Separator(bfHelpWindow, orient=tk.HORIZONTAL)
    sep.grid(row=1, column=0, columnspan=3, sticky="we", padx=20)



    label = tk.Label(bfHelpWindow, justify=tk.CENTER, wraplength=360, font="TkDefaultFont 10 bold", text="List of Brainfuck Commands")
    label.grid(row=2, column=0, columnspan=3, padx=20)

    sep = ttk.Separator(bfHelpWindow, orient=tk.HORIZONTAL)
    sep.grid(row=3, column=0, columnspan=3, sticky="we", padx=20)


    bfCmds = [
        [
            ">",
            "Right Arrow",
            "Moves the data pointer to the next location in the program memory"
        ],
        
        [
            "<",
            "Left Arrow",
            "Moves the data pointer to the previous location in the program memory"
        ],
        
        [
            "+",
            "Plus Symbol",
            "Adds one (1) to the data at the current memory location"
        ],
        
        [
            "-",
            "Negative Symbol",
            "Subtracts one (1) from the data at the current memory location"
        ],
        
        [
            ".",
            "Dot",
            "Outputs the ASCII character of the value at the current memory location"
        ],
        
        [
            ",",
            "Comma",
            "Gets input from the keyboard, and places the ASCII value of the character received into the current memory location"
        ],
        
        [
            "[",
            "Open Square Bracket",
            "Starts a loop that executes the code inside the square brackets"
        ],
        
        [
            "]",
            "Close Square Bracket",
            "If the current value at the data pointer is zero (0), the program moves to the next command, otherwise, it loops back to the previous open square bracket"
        ]
    ]

    for i in range(len(bfCmds)):
        label = tk.Label(bfHelpWindow, justify=tk.LEFT, wraplength=10, font="TkDefaultFont 10 bold", text=bfCmds[i][0])
        label.grid(row=i+4, column=0, padx=10, pady=5)

        label = tk.Label(bfHelpWindow, justify=tk.LEFT, wraplength=140, font="TkDefaultFont 9 bold", text=bfCmds[i][1])
        label.grid(row=i+4, column=1, padx=10, pady=5)

        label = tk.Label(bfHelpWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 9", text=bfCmds[i][2])
        label.grid(row=i+4, column=2, padx=10, pady=5)

    
    bfHelpWindow.attributes("-topmost", "true")


def myBrainIsFucked(key=""):
    mbifWindow = tk.Toplevel()
    mbifWindow.geometry("300x100")
    mbifWindow.columnconfigure(0, weight=1)
    mbifWindow.rowconfigure(2, weight=1)


    label = tk.Label(mbifWindow, text="my brain is fucked.", font="Arial 16 bold")
    label.grid(row=0, column=0)

    sep = ttk.Separator(mbifWindow, orient=tk.HORIZONTAL)
    sep.grid(row=1, column=0, sticky="we", padx=20)
    
    label = tk.Label(mbifWindow, justify=tk.LEFT, wraplength=360, font="TkDefaultFont 10", text="mine too codie, mine too")
    label.grid(row=2, column=0, padx=20)


    
    mbifWindow.attributes("-topmost", "true")



######################
# Initialize Program #
######################

def startInitialization(key=""):
    global window
    global entryMem
    global appVars
    try:
        appVars["memoryBits"] = 2**int(entryMem.get())
        if appVars["memoryBits"] > 2**16:
            appVars["memoryBits"] = 2**16
    except ValueError:
        appVars["memoryBits"] = 256


    try:
        file = open(appfolder + "data.dat", "r")
        fileData = file.readlines()
        file.close()
        fileData = fileData[1:]
        
    except FileNotFoundError:
        fileData = []

    try:
        file = open(appfolder + "data.dat", "w")
        file.write("memoryBits=" + str(appVars["memoryBits"]) + "\n")
        for line in fileData:
            file.write(line)
        file.close()

    except FileNotFoundError:
        try: os.mkdir(appfolder + "data.dat")
        except: pass
        
        file = open(appfolder + "data.dat", "x")
        file.write("memoryBits=" + str(appVars["memoryBits"]) + "\n")
        file.close()


        
    window.destroy()
    initializeProgram()

# Main Program
def initializeProgram():
    global window
    global memoryBits
    global appVars
    global currentFilepath

    appVars["memory"] = []
    for i in range(appVars["memoryBits"]):
        appVars["memory"].append(0)
    
    window = tk.Tk(className=" Brainfuck IDE")
    window.geometry("1000x600")

    # Window rows and cols weights
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)

    # Window Keybinds
    window.bind("<F1>", showAbout)
    window.bind("<F2>", showBFAbout)
    window.bind("<F3>", showHelp)
    window.bind("<F4>", showBFHelp)
    window.bind("<F5>", runBF)
    window.bind("<F6>", stepBF)
    window.bind("<F9>", resetMemory)
    window.bind("<Control-n>", newFile)
    window.bind("<Control-o>", openFile)
    window.bind("<Control-s>", saveFile)
    window.bind("<Control-Alt-s>", saveFileAs)
    window.bind("<Control-q>", quitBF)



    # Create top menu
    menuBar = tk.Menu(window)


    fileMenu = tk.Menu(menuBar, tearoff=0)
    fileMenu.add_command(label="New", accelerator="Ctrl+N", command=newFile)
    fileMenu.add_command(label="Open...", accelerator="Ctrl+O", command=openFile)
    fileMenu.add_command(label="Save", accelerator="Ctrl+S", command=saveFile)
    fileMenu.add_command(label="Save As...", accelerator="Ctrl+Alt+S", command=saveFileAs)
    fileMenu.add_command(label="Save Program Memory", command=saveProgramMemory)
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit Brainfuck IDE", accelerator="Ctrl+Q", command=quitBF)
    
    menuBar.add_cascade(label="File", menu=fileMenu)

    runMenu = tk.Menu(menuBar, tearoff=0)
    runMenu.add_command(label="Run", accelerator="F5", command=runBF)
    runMenu.add_command(label="Step Forward", accelerator="F6", command=stepBF)

    menuBar.add_cascade(label="Run", menu=runMenu)


    optionsMenu = tk.Menu(menuBar, tearoff=0)
    optionsMenu.add_command(label="Set Memory Bytes...", command=getNewMemoryBits)
    optionsMenu.add_command(label="Reset Memory", accelerator="F9", command=resetMemory)

    menuBar.add_cascade(label="Options", menu=optionsMenu)
    

    helpMenu = tk.Menu(menuBar, tearoff=0)
    helpMenu.add_command(label="About", accelerator="F1", command=showAbout)
    helpMenu.add_command(label="About Brainfuck", accelerator="F2", command=showBFAbout)
    helpMenu.add_separator()
    helpMenu.add_command(label="Help", accelerator="F3", command=showHelp)
    helpMenu.add_command(label="Brainfuck Help", accelerator="F4", command=showBFHelp)
    helpMenu.add_separator()
    helpMenu.add_command(label="my brain is fucked.", command=myBrainIsFucked)
    
    menuBar.add_cascade(label="Help", menu=helpMenu)

    #############
    # Add panes #
    #############

    # Create Panes
    parentPane = tk.PanedWindow(orient=tk.HORIZONTAL, height=600, sashwidth=5, sashrelief=tk.RIDGE, showhandle=True, handlepad=296)
    leftPane = tk.PanedWindow(orient=tk.VERTICAL, width=750, sashwidth=5, sashrelief=tk.RIDGE, showhandle=True, handlepad=371)
    rightPane = tk.PanedWindow(orient=tk.VERTICAL, width=250, sashwidth=5, sashrelief=tk.RIDGE, showhandle=True, handlepad=121)

    # Add frame to each corner
    frameTL = tk.Frame(leftPane)
    frameTL.rowconfigure(0, weight=0)
    frameTL.rowconfigure(1, weight=1)
    frameTL.columnconfigure(0, weight=1)
    
    frameBL = tk.Frame(leftPane)
    frameBL.rowconfigure(0, weight=0)
    frameBL.rowconfigure(1, weight=1)
    frameBL.columnconfigure(0, weight=1)

    frameTR = tk.Frame(rightPane)
    frameTR.rowconfigure(0, weight=0)
    frameTR.rowconfigure(1, weight=1)
    frameTR.columnconfigure(0, weight=1)

    frameBR = tk.Frame(rightPane)
    frameBR.rowconfigure(0, weight=0)
    frameBR.rowconfigure(1, weight=1)
    frameBR.columnconfigure(0, weight=1)


    ############
    # Top Left #
    ############

    label = tk.Label(frameTL, text="Brainfuck Code")
    label.grid(row=0, column=0, sticky="n")

    canvasCode = tk.Canvas(frameTL, highlightthickness=0)
    canvasCode.rowconfigure(0, weight=1)
    canvasCode.columnconfigure(0, weight=1)
    canvasCode.columnconfigure(1, weight=0)

    global codeBox
    codeBox = tk.Text(canvasCode, relief=tk.SUNKEN, borderwidth=2)
    codeBox.insert(tk.END, "")
    codeBox.grid(row=0, column=0, sticky="news")
    codeBox.bind("<KeyRelease>", fileModified)
    try:
        currentFilepath = appVars["lastFilepath"]
        openFile("", True)
    except:
        currentFilepath = ""
    

    scrollCode = tk.Scrollbar(canvasCode, orient="vertical")
    scrollCode.grid(row=0, column=1, sticky="ns")

    codeBox.config(yscrollcommand=scrollCode.set)
    scrollCode.config(command=codeBox.yview)
    canvasCode.grid(row=1, column=0, sticky="news")
    

    
    ###############
    # Bottom Left #
    ###############

    label = tk.Label(frameBL, text="Output")
    label.grid(row=0, column=0, sticky="n")

    global outputBox
    outputBox = tk.Text(frameBL, bg="black", fg="white", relief=tk.SUNKEN, borderwidth=2)
    outputBox.insert(tk.END, ">")
    outputBox.grid(row=1, column=0, sticky="news")
    outputBox.tag_config("error", foreground="red")

    
    #############
    # Top Right #
    #############

    label = tk.Label(frameTR, text="Memory (" + str(appVars["memoryBits"]) + " Bytes)")
    label.grid(row=0, column=0, sticky="news")
    
    canvasMem = tk.Canvas(frameTR, highlightthickness=0)
    canvasMem.rowconfigure(0, weight=1)
    canvasMem.columnconfigure(0, weight=1)
    canvasMem.columnconfigure(1, weight=0)

    global memoryBox
    memoryBox = tk.Text(canvasMem, width=25, relief=tk.SUNKEN, borderwidth=2)
    for i in range(appVars["memoryBits"]):
        memoryBox.insert(tk.END, f"Memory {i}\t\t|    0\n")
    memoryBox.config(state=tk.DISABLED)
    
    memoryBox.grid(row=0, column=0, sticky="news")
    memoryBox.tag_add("start", "1.0", "1.0 lineend")
    memoryBox.tag_config("start", background="darkblue", foreground="white")

    scroll = tk.Scrollbar(canvasMem, orient="vertical")
    scroll.grid(row=0, column=1, sticky="ns")

    memoryBox.config(yscrollcommand=scroll.set)
    scroll.config(command=memoryBox.yview)
    canvasMem.grid(row=1, column=0, sticky="news")
    

    
    ################
    # Bottom Right #
    ################

    label = tk.Label(frameBR, text="Quick Commands")
    label.grid(row=0, column=0, sticky="n")

    frameCmds = tk.Frame(frameBR, padx=5, pady=5, height=100)
    frameCmds.rowconfigure(0, weight=1)
    frameCmds.columnconfigure(0, weight=1)
    frameCmds.rowconfigure(1, weight=1)
    frameCmds.columnconfigure(1, weight=1)

    runBtn = tk.Button(frameCmds, text="Run", command=runBF)
    runBtn.grid(row=0, column=0, padx=4, pady=4, sticky="news")
    
    saveBtn = tk.Button(frameCmds, text="Save", padx=4, pady=4, command=saveFile)
    saveBtn.grid(row=1, column=0, padx=4, pady=4, sticky="news")


    global stepVars
    stepVars = {
        "bfcode":"",
        "bfChars":[
            ">", "<",
            "+", "-",
            ".", ",",
            "[", "]"
        ],
        "memoryPos":0,
        "ifLoopPos":[],
        "skipCommand":False,
        "currentChar":0
    }
    
    stepBtn = tk.Button(frameCmds, text="Step", command=stepBF)
    stepBtn.grid(row=0, column=1, padx=4, pady=4, sticky="news")
    
    resetBtn = tk.Button(frameCmds, text="Reset Memory", padx=4, pady=4, command=resetMemory)
    resetBtn.grid(row=1, column=1, padx=4, pady=4, sticky="news")

    frameCmds.grid(row=1, column=0, sticky="news")
    




    
    ################
    # Build Window #
    ################

    # Add frames to L/R panes
    leftPane.add(frameTL)
    leftPane.add(frameBL)
    rightPane.add(frameTR)
    rightPane.add(frameBR)

    # Add L/R panes to parent pane
    parentPane.add(leftPane)
    parentPane.add(rightPane)


    # Add parent pane to window
    parentPane.grid(row=0, column=0, sticky="news")
    codeBox.focus()
    
    # Add Sizegrip to window
    sg = ttk.Sizegrip(frameBR)
    sg.grid(row=1, column=1, sticky="se")

    # Add menu to window
    window.config(menu=menuBar)

    newFile()




start()
window.mainloop()
