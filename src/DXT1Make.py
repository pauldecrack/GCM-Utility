import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox  #Written by Jan 2005 and da best developer pauldecrack
from PIL import Image, ImageTk
import struct
from typing import NamedTuple
from texfury import Texture, BCFormat

class TextureHeader(NamedTuple):
    magic: int      # 4 byte (I)
    width: int      # 2 byte (H)
    height: int     # 2 byte (H)
    format_id: int  # 2 byte (H)

tk_img = None
file_path = None
file_pathgcm = None
lista_offset = []
indice_corrente = 0
current_pil_image = None


start_offset = 0
end_offset = 0
dimensione_byte = 0
LARGHEZZA = 0
ALTEZZA = 0


if not os.path.exists("Temp"):
    os.makedirs("Temp")

def selectImage():
    global file_path

    file_path = filedialog.askopenfilename()
    answer = messagebox.askokcancel("?", f"File path: {file_path}\n Are you sure to use this path?")
  
    if answer:
        dxt1 = Image.open(file_path)
        w, h = dxt1.size

        output_path = f"./Temp/1.dds"
        dxt1.save(output_path)

        num_file = 2

        while w > 4 and h >= 4:
            w = w // 2
            h = h // 2
            dxt1_scaled = dxt1.resize((w, h))
            output_path = f"./Temp/{num_file}.dds"
            dxt1_scaled.save(output_path)
            num_file += 1

def carica_texture_corrente():
    global tk_img
    global file_pathgcm
    global start_offset
    global end_offset
    global dimensione_byte
    global lista_offset
    global indice_corrente
    global current_pil_image
    global LARGHEZZA
    global ALTEZZA

    if not lista_offset:
        return

    
    start_offset = lista_offset[indice_corrente]
    
    target = b"DXT1"

    with open(file_pathgcm, "rb") as gcm:
        file_data = gcm.read()
        

        posizione_header = start_offset + len(target)
        

        if posizione_header + 6 > len(file_data):
            label_contatore.config(text=f"Match: {indice_corrente + 1} of {len(lista_offset)} (Wrong EOF)")
            return
            
        header_bytes = file_data[posizione_header : posizione_header + 6]
        
        try:
            #LITTLE ENDIAN
            LARGHEZZA, ALTEZZA = struct.unpack("<HH2x", header_bytes)
            
            
            if LARGHEZZA <= 0 or ALTEZZA <= 0 or LARGHEZZA > 8192 or ALTEZZA > 8192:
                label_contatore.config(text=f"Match: {indice_corrente + 1} di {len(lista_offset)} (Dimensioni Errate)")
                return
                
        except Exception:
            label_contatore.config(text=f"Match: {indice_corrente + 1} di {len(lista_offset)} (Errore Header)")
            return
        
        
        end_offset = posizione_header + 6
        
        
        dimensione_byte = int((LARGHEZZA * ALTEZZA) / 2)
        
        
        raw_data = file_data[end_offset : end_offset + dimensione_byte]

        
        if len(raw_data) < dimensione_byte:
            label_contatore.config(text=f"Match: {indice_corrente + 1} di {len(lista_offset)} (Incomplete data {LARGHEZZA}x{ALTEZZA})")
            return

        try:
            
            current_pil_image = Image.frombytes("RGBA", (LARGHEZZA, ALTEZZA), raw_data, "bcn", (1,))
            tk_img = ImageTk.PhotoImage(current_pil_image)
            
            imageDisplay.config(image=tk_img)
            imageDisplay.image = tk_img  

           
            label_contatore.config(text=f"Match: {indice_corrente + 1} di {len(lista_offset)} ({LARGHEZZA}x{ALTEZZA})")
        except Exception:
            label_contatore.config(text=f"Match: {indice_corrente + 1} di {len(lista_offset)} (Errore Render)")

def selectGCM():
    global tk_img
    global file_pathgcm
    global start_offset
    global end_offset
    global dimensione_byte
    global lista_offset       
    global indice_corrente     
     
    file_pathgcm = filedialog.askopenfilename()
    if not file_pathgcm:
        return
   
    target = b"DXT1"

    with open(file_pathgcm, "rb") as gcm:
        file_data = gcm.read()
        lista_offset = []
        pos = file_data.find(target)
        while pos != -1:
            lista_offset.append(pos)
            pos = file_data.find(target, pos + 1)
        
        if not lista_offset:
            messagebox.showerror("Error", "DXT1 string not found!")
            return
            
       
        indice_corrente = 0
        carica_texture_corrente()

def saveImage():
    global current_pil_image
    
    
    if current_pil_image is None:
        messagebox.showwarning("Avviso", "Nessuna immagine caricata da salvare!")
        return
        
    
    output_file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        title="Save Extracted Image As"
    )
    
    
    if output_file_path:
        try:
            current_pil_image.save(output_file_path)
            messagebox.showinfo("Successo", f"Image saved in:\n{output_file_path}")
        except Exception as e:
            messagebox.showerror("Errore", f"Cannot save image:\n{e}")


def injectTexture():
    global file_pathgcm
    global end_offset
    global dimensione_byte
    global LARGHEZZA
    global ALTEZZA

    if not file_pathgcm or end_offset == 0:
        messagebox.showerror("Error", "No GCM File open or selected texture!")
        return

    
    img_to_inject = filedialog.askopenfilename(
        title="Select image to inject",
        filetypes=[("Standard images", "*.png;*.jpg;*.jpeg;*.bmp")]
    )
    if not img_to_inject:
        return

    try:
        
        img_originale = Image.open(img_to_inject)
        inj_w, inj_h = img_originale.size

        if inj_w != LARGHEZZA or inj_h != ALTEZZA:
            messagebox.showerror(
                "Dimension error!", 
                f"Incorect dimensions!\nImage should be {LARGHEZZA}x{ALTEZZA}.\nYour choice: {inj_w}x{inj_h}."
            )
            return

        path_file_unico = "./Temp/inject_mipmaps.raw"
        
       
        with open(path_file_unico, "wb") as file_unico:
            w, h = inj_w, inj_h
            current_img = img_originale
            
            while True:
                path_temp_png = f"./Temp/mip_temp.png"
                path_temp_dds = f"./Temp/mip_temp.dds"
                
              
                current_img.save(path_temp_png)
                
           
                tex = Texture.from_image(path_temp_png, format=BCFormat.BC1, quality=1.0)
                tex.save_dds(path_temp_dds)
                
            
                with open(path_temp_dds, "rb") as dds_file:
                    dds_file.seek(128)
                    dim_mipmap_byte = int((w * h) / 2)
                    raw_data = dds_file.read(dim_mipmap_byte)
                    file_unico.write(raw_data)
                
               
                if w <= 4 or h <= 4:
                    break
                    
               
                w = max(4, w // 2)
                h = max(4, h // 2)
                current_img = img_originale.resize((w, h), Image.Resampling.LANCZOS)

        
        with open(path_file_unico, "rb") as file_unico:
            tutti_i_dati_raw = file_unico.read()

        
        with open(file_pathgcm, "r+b") as gcm:
            gcm.seek(end_offset)
            gcm.write(tutti_i_dati_raw)

        messagebox.showinfo("Success", "Texture injected succesfully!")
        
    
        carica_texture_corrente()

    except Exception as e:
        messagebox.showerror("Error Injecting", f"Error during compression:\n{e}")


def prossimo_match():
    global indice_corrente
    global lista_offset
    if idx := len(lista_offset):
        if indice_corrente < idx - 1:
            indice_corrente += 1
            carica_texture_corrente()
        else:
            messagebox.showinfo("End", "Already at the start")

def match_precedente():
    global indice_corrente
    if indice_corrente > 0:
        indice_corrente -= 1
        carica_texture_corrente()
    else:
        messagebox.showinfo("Start", "Already at the first match")


root = tk.Tk()
root.title("GTI")
root.state("zoomed")

tk.Label(root, text="GCM Texture Injector (GTI) V0.1").pack()

button2 = tk.Button(root, text="Select GCM File", command=selectGCM)
button2.pack(pady=5)


button3 = tk.Button(root, text="Save Image", command=saveImage)
button3.pack(pady=5)


button4 = tk.Button(root, text="Inject Texture", command=injectTexture)
button4.pack(pady=5)


frame_navigazione = tk.Frame(root)
frame_navigazione.pack(pady=5)

btn_precedente = tk.Button(frame_navigazione, text="⬅", command=match_precedente)
btn_precedente.pack(side=tk.LEFT, padx=5)

label_contatore = tk.Label(frame_navigazione, text="Match: 0 of 0")
label_contatore.pack(side=tk.LEFT, padx=5)

btn_prossimo = tk.Button(frame_navigazione, text="➡", command=prossimo_match)
btn_prossimo.pack(side=tk.LEFT, padx=5)

imageDisplay = tk.Label(root)
imageDisplay.pack(pady=10)

root.mainloop()
