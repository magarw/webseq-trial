
###################################################################
# Script Name	: tkin.py
# Description	: Required for launching a sever side dialog to get BAM
#                 full file paths for IGV Reports.
# Args          : None.
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################


import tkinter
import tkinter.filedialog

def main():
    root = tkinter.Tk()
    root.withdraw() # Close the root window
    # Make it almost invisible - no decorations, 0 size, top left corner.
    root.overrideredirect(True)
    root.geometry('0x0+0+0')

    # Show window again and lift it to top so it can get focus,
    # otherwise dialogs will end up behind the terminal.
    root.deiconify()
    root.lift()
    root.focus_force()
    in_path = tkinter.filedialog.askopenfilenames(parent=root)

    with open('bamFilesFullPaths.txt', 'w') as f:
        for item in in_path:
            f.write("%s\n" % item)
            print(item)
    # Get rid of the top-level instance once to make it actually invisible.
    root.destroy()

if __name__ == "__main__":
    main()
