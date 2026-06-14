import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def open_texture_injector():

    exe_path = "./dist/DXT1Make.exe"
    


    if os.path.exists(exe_path):
        try:
        
            subprocess.Popen(exe_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch the tool:\n{e}")
    else:
        messagebox.showerror(
            "File Not Found", 
            f"Could not find the executable at:\n{exe_path}\n\n"
            "Please make sure the EXE file is compiled and placed in the correct directory."
        )


root = tk.Tk()
root.title("GCM Utility 0.1")
root.geometry("400x250+100+100")
root.minsize(300, 200)


title_label = tk.Label(root, text="GCM Utility v0.1", font=("Arial", 16, "bold"))
title_label.pack(pady=20)


info_label = tk.Label(root, text="Select the tool you want to launch:", font=("Arial", 10))
info_label.pack(pady=5)


tools_frame = tk.Frame(root)
tools_frame.pack(pady=20, fill=tk.X, padx=40)


btn_injector = tk.Button(
    tools_frame, 
    text="Launch GCM Texture Injector", 
    font=("Arial", 11, "bold"),
    bg="#2b2b2b",
    fg="white",
    padx=10,
    pady=10,
    command=open_texture_injector
)
btn_injector.pack(fill=tk.X)

root.mainloop()
