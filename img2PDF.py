import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageOps
import os
import shutil

root = ctk.CTk()
root.title("Img2PDF")
root.configure(fg_color="#F5F5F5")
root.after(0, lambda:root.state("zoomed"))

images_paths = []
conversion = False

def to_select_files(*args):
    global images_paths
    filepaths = filedialog.askopenfilenames(title="Img2PDF",filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.heif *.bmp *.tiff")])
    if filepaths:
        if not images_paths:
            frame1_1.pack_forget()
            frame2.pack(fill="both", expand=True)
        images_paths.extend(filepaths)
        preview_frame()

def preview_frame(*args):
    count_imgs.configure(text=str(len(images_paths)))
    for widget in images_container.winfo_children():
        widget.destroy()
    
    row = 0
    col = 0
    
    margin_preview = {"No Margin": 0, "Small Margin": 5, "Big Margin": 10}
    prev_marg = margin_preview.get(activness_mar, 0)
    is_landscape = (activness == "Landscape")
    pg_size = ps_dropdown.get()
    
    for i, path in enumerate(images_paths):
        imgs_frame = ctk.CTkFrame(images_container, fg_color="#FFFFFF", border_width=1, border_color="#E5E5EE", corner_radius=10, width=180, height=210)
        imgs_frame.grid(row=row, column=col, padx=15, pady=15)
        imgs_frame.pack_propagate(False)
        imgs_frame.grid_propagate(False)
        
        btn_left = ctk.CTkButton(imgs_frame, text="◀", width=26, height=26, corner_radius=20, fg_color="#FFFFFF", text_color="#161616", hover_color="#F5F5F5", font=("Segoe UI", 16, "bold"), command=lambda idx=i: move_left(idx))
        btn_left.place(x=10, y=5)
                
        btn_right = ctk.CTkButton(imgs_frame, text="▶", width=26, height=26, corner_radius=20, fg_color="#FFFFFF", text_color="#161616", hover_color="#F5F5F5", font=("Segoe UI", 16, "bold"), command=lambda idx=i: move_right(idx))
        btn_right.place(x=42, y=5)
                
        btn_del = ctk.CTkButton(imgs_frame, text="✕", width=20, height=26, corner_radius=20, fg_color="#FFFFFF", text_color="#555555", hover_color="#E5322D", font=("Segoe UI", 16, "bold"), command=lambda idx=i: del_img(idx))
        btn_del.place(x=125, y=5)
        
        fname = os.path.basename(path)
        if len(fname) > 13:
            fname = fname[:10] + "..."
        name_label = ctk.CTkLabel(imgs_frame, text=fname, text_color="#555555", font=("Segoe UI", 12))
        name_label.place(x=10, y=175)
        
        num_label = ctk.CTkLabel(imgs_frame, text=str(i+1), fg_color="#161616", text_color="#FFFFFF", width=22, height=22, corner_radius=11, font=("Segoe UI", 10, "bold"))
        num_label.place(x=148, y=175)
        
        try:
            pil_image = Image.open(path).convert("RGB")
            
            target_pw, target_ph = None, None
            if "A4" in pg_size:
                target_pw, target_ph = (842, 595) if is_landscape else (595, 842)
            elif "US Letter" in pg_size:
                target_pw, target_ph = (792, 612) if is_landscape else (612, 792)
                
            if target_pw and target_ph:
                scale = 120 / max(target_pw, target_ph)
                prev_pw = max(1, int(target_pw * scale))
                prev_ph = max(1, int(target_ph * scale))
                
                bg = Image.new('RGB', (prev_pw, prev_ph), (255, 255, 255))
                
                avail_w = max(1, prev_pw - (prev_marg * 2))
                avail_h = max(1, prev_ph - (prev_marg * 2))
                
                pil_image.thumbnail((avail_w, avail_h), Image.Resampling.LANCZOS)
                
                offset_x = (prev_pw - pil_image.width) // 2
                offset_y = (prev_ph - pil_image.height) // 2
                bg.paste(pil_image, (offset_x, offset_y))
                final_img = bg
            else:
                avail_w = max(1, 120 - (prev_marg * 2))
                avail_h = max(1, 120 - (prev_marg * 2))
                pil_image.thumbnail((avail_w, avail_h), Image.Resampling.LANCZOS)
                
                prev_pw = pil_image.width + (prev_marg * 2)
                prev_ph = pil_image.height + (prev_marg * 2)
                bg = Image.new('RGB', (prev_pw, prev_ph), (255, 255, 255))
                bg.paste(pil_image, (prev_marg, prev_marg))
                final_img = bg
                
            final_img = ImageOps.expand(final_img, border=1, fill="#D1D5DB")
            
            ctk_img = ctk.CTkImage(light_image=final_img, dark_image=final_img, size=final_img.size)
            
            img_label = ctk.CTkLabel(imgs_frame, image=ctk_img, text="")
            img_label.image = ctk_img 
            img_label.place(relx=0.5, rely=0.48, anchor="center")
            
        except Exception:
            err_label = ctk.CTkLabel(imgs_frame, text="Invalid Image", text_color="red")
            err_label.place(relx=0.5, rely=0.48, anchor="center")
        
        col += 1
        if col > 3:
            col = 0
            row += 1

def move_left(idx):
    if idx > 0:
        images_paths[idx], images_paths[idx-1] = images_paths[idx-1], images_paths[idx]
        preview_frame()

def move_right(idx):
    if idx < len(images_paths) - 1:
        images_paths[idx], images_paths[idx+1] = images_paths[idx+1], images_paths[idx]
        preview_frame()

def del_img(idx):
    images_paths.pop(idx)
    preview_frame()
    if not images_paths:
        frame2.pack_forget()
        frame1_1.pack(fill="both", expand=True)

def convert_into_pdf():
    global conversion
    if not images_paths:
        return
        
    ctp_button.configure(text="Converting...", state="disabled")
    root.update()
    
    margin_map = {"No Margin": 0, "Small Margin": 20, "Big Margin": 50}
    margin = margin_map.get(activness_mar, 0)
    is_landscape = (activness == "Landscape")
    
    pg_size = ps_dropdown.get()
    target_size = None
    if "A4" in pg_size:
        target_size = (842, 595) if is_landscape else (595, 842)
    elif "US Letter" in pg_size:
        target_size = (792, 612) if is_landscape else (612, 792)
        
    pdf_images = []
    for path in images_paths:
        try:
            img = Image.open(path).convert("RGB")
            if target_size:
                new_w = max(1, target_size[0] - (margin * 2))
                new_h = max(1, target_size[1] - (margin * 2))
                img.thumbnail((new_w, new_h), Image.Resampling.LANCZOS)
                bg = Image.new('RGB', target_size, (255, 255, 255))
                offset = ((target_size[0] - img.width) // 2, (target_size[1] - img.height) // 2)
                bg.paste(img, offset)
                pdf_images.append(bg)
            else:
                if margin > 0:
                    new_w = img.width + (margin * 2)
                    new_h = img.height + (margin * 2)
                    bg = Image.new('RGB', (new_w, new_h), (255, 255, 255))
                    bg.paste(img, (margin, margin))
                    pdf_images.append(bg)
                else:
                    pdf_images.append(img)
        except Exception:
            continue

    if not pdf_images:
        ctp_button.configure(text="Convert To Pdf →", state="normal")
        return

    separate_pdf = checkbox.get()
    
    if separate_pdf:
        if not os.path.exists("temp_pdfs"):
            os.makedirs("temp_pdfs")
        for i, p_img in enumerate(pdf_images):
            p_img.save(f"temp_pdfs/output_{i+1}.pdf")
    else:
        pdf_images[0].save("temp_output.pdf", save_all=True, append_images=pdf_images[1:])
        
    conversion = True
    ctp_button.configure(text="Download ↓", fg_color="#10B981", hover_color="#059669", state="normal", command=download)

def download():
    if checkbox.get():
        select_folder = filedialog.askdirectory()
        if select_folder:
            for f in os.listdir("temp_pdfs"):
                shutil.move(os.path.join("temp_pdfs", f), os.path.join(select_folder, f))
            os.rmdir("temp_pdfs")
            reset()
    else:
        in_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if in_file:
            shutil.move("temp_output.pdf", in_file)
            reset()

def reset():
    global conversion
    conversion = False
    ctp_button.configure(text="Convert To Pdf →", fg_color="#E5322D", hover_color="#9E0904", command=convert_into_pdf)
    images_paths.clear()
    preview_frame()
    frame2.pack_forget()
    frame1_1.pack(fill="both", expand=True)

# gui
frame1 = ctk.CTkFrame(root, fg_color="#FFFFFF", height=70, border_width=1, border_color="#E5E5EE", corner_radius=0)
frame1.pack(fill="x")
frame1.pack_propagate(False)

frame1_label = ctk.CTkLabel(frame1, text="Img2PDF", text_color="#000000", font=("Roboto",50,"bold"))
frame1_label.place(relx=0.5, rely=0.5, anchor="center")

frame1_1 = ctk.CTkFrame(root, fg_color="#F5F5F5")
frame1_1.pack(fill="both", expand=True)

heading = ctk.CTkLabel(frame1_1, text="Convert Images to PDF", text_color="#161616", font=("Helvetica", 50, "bold"))
heading.pack(pady=(50,0))

subheading = ctk.CTkLabel(frame1_1, text="Convert Multiple Images of any Format into PDF in Seconds for Free.", text_color="#555555", font=("Segoe UI",20))
subheading.pack(pady=(20,0))

select_button = ctk.CTkButton(frame1_1, text="📂 Choose Files", fg_color="#E5322D", hover_color="#9E0904" ,text_color="#FFFFFF" ,font=("Segoe UI",30), height=80, width=300, corner_radius=10, command=to_select_files)
select_button.pack(pady=(50,0))

frame2 = ctk.CTkFrame(root, fg_color="#F5F5F5")

images_container = ctk.CTkScrollableFrame(frame2, fg_color="transparent")
images_container.pack(side="left", fill="both", expand=True, padx=20, pady=20)

af_frame = ctk.CTkFrame(frame2, height=50, fg_color="#E5322D", corner_radius=25, cursor="hand2")
af_frame.place(relx=0.65, rely=0.08, anchor="center")

af_label = ctk.CTkLabel(af_frame, text="+", font=("Helvetica", 28, "bold"), text_color="#FFFFFF")
af_label.pack(side="left", padx=(20, 10), pady=10)

count_imgs = ctk.CTkLabel(af_frame, text="1", width=28, height=28, corner_radius=14, fg_color="#161616", text_color="#FFFFFF", font=("Segoe UI", 14, "bold"),bg_color="transparent" )
count_imgs.pack(side="right", padx=(0, 15), pady=10)

def on_enter(event):
    af_frame.configure(fg_color="#9E0904")

def on_leave(event):
    af_frame.configure(fg_color="#E5322D")

def on_click(event):
    to_select_files()

for widget in (af_frame, af_label, count_imgs):
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
    widget.bind("<Button-1>", on_click)

frame2_2 = ctk.CTkFrame(frame2, fg_color="#FFFFFF",width=450 ,border_width=1, border_color="#E5E5EE", corner_radius=0)
frame2_2.pack(side="right" ,fill="y")
frame2_2.pack_propagate(False)

frame2_3 = ctk.CTkFrame(frame2_2, fg_color="#FFFFFF", width=450,height=80 ,border_width=1, border_color="#E5E5EE", corner_radius=0)
frame2_3.pack(anchor="n", fill="x")
frame2_3.pack_propagate(False)

label = ctk.CTkLabel(frame2_3, text="PDF Settings", text_color="#1c1c1e", fg_color="#FFFFFF", font=("Segoe UI",40))
label.place(relx=0.5, rely=0.5, anchor="center")

equal_padding = ctk.CTkScrollableFrame(frame2_2, fg_color="transparent", corner_radius=0, scrollbar_button_color="#E0E0E0", scrollbar_button_hover_color="#BDBDBD")
equal_padding._scrollbar.configure(width=15)
equal_padding.pack(fill="both", expand=True, padx=(20,0), pady=(10,0))

po_label = ctk.CTkLabel(equal_padding, text="Page Orientation", text_color="#1c1c1e", font=("Segoe UI",20))
po_label.pack(in_=equal_padding,side="top",anchor="w",pady=(10,0))

container = ctk.CTkFrame(equal_padding, fg_color="transparent")
container.pack(side="top", fill="x", pady=(10,0))

portrait_frame = ctk.CTkFrame(container, fg_color="#F5F5F5", bg_color="#FFFFFF" ,height=100, width=195, corner_radius=10, border_width=2, border_color="#F5F5F5")
portrait_frame.pack(in_=container, side="left", expand=True, fill="x", padx=(0,5))
portrait_frame.pack_propagate(False)

portrait_symbol = ctk.CTkLabel(portrait_frame, text="▯", fg_color="transparent", text_color="#999494", font=("Segoe UI",50), height=40)
portrait_symbol.place(relx=0.5, rely=0.35, anchor="center")

portrait_text = ctk.CTkLabel(portrait_frame, text="Portrait", fg_color="transparent", text_color="#999494", font=("Segoe UI",20), height=10)
portrait_text.place(relx=0.5, rely=0.70, anchor="center")

landscape_frame = ctk.CTkFrame(equal_padding, fg_color="#F5F5F5",bg_color="#FFFFFF" ,height=100, width=195, corner_radius=10, border_width=2, border_color="#F5F5F5")
landscape_frame.pack(in_=container, side="left", expand=True, fill="x", padx=(5,0))
landscape_frame.pack_propagate(False)

landscape_symbol = ctk.CTkLabel(landscape_frame, text="▭", fg_color="transparent", text_color="#999494", font=("Segoe UI",50), height=40)
landscape_symbol.place(relx=0.5, rely=0.35, anchor="center")

landscape_text = ctk.CTkLabel(landscape_frame, text="Landscape", fg_color="transparent", text_color="#999494", font=("Segoe UI",20), height=10)
landscape_text.place(relx=0.5, rely=0.70, anchor="center")

activness = "Portrait"
def selection(select):
    global activness
    activness = select
    if select == "Portrait":
        portrait_frame.configure(fg_color="#F5F5F5", border_color="#E5322D", border_width=2)
        portrait_symbol.configure(text_color="#E5322D")
        portrait_text.configure(text_color="#E5322D")
        landscape_frame.configure(fg_color="#F5F5F5", border_color="#999494", border_width=2)
        landscape_symbol.configure(text_color="#999494")
        landscape_text.configure(text_color="#999494")
    else:
        portrait_frame.configure(fg_color="#F5F5F5", border_color="#999494", border_width=2)
        portrait_symbol.configure(text_color="#999494")
        portrait_text.configure(text_color="#999494")
        landscape_frame.configure(fg_color="#F5F5F5", border_color="#E5322D", border_width=2)
        landscape_symbol.configure(text_color="#E5322D")
        landscape_text.configure(text_color="#E5322D")
    preview_frame()

def hover_in_portrait(event):
    if activness != "Portrait":
        portrait_frame.configure(fg_color="#CCBDBD", border_color="#161616", border_width=2)
        portrait_symbol.configure(text_color="#161616")
        portrait_text.configure(text_color="#161616")
def hover_out_portrait(event):
    if activness!= "Portrait":
        portrait_frame.configure(fg_color="#F5F5F5", border_color="#999494", border_width=2)
        portrait_symbol.configure(text_color="#999494")
        portrait_text.configure(text_color="#999494")
def hover_out_landscape(event):
    if activness != "Landscape":
        landscape_frame.configure(fg_color="#F5F5F5", border_color="#999494", border_width=2)
        landscape_symbol.configure(text_color="#999494")
        landscape_text.configure(text_color="#999494")
def hover_in_landscape(event):
    if activness != "Landscape":
        landscape_frame.configure(fg_color="#CCBDBD", border_color="#161616", border_width=2)
        landscape_symbol.configure(text_color="#161616")
        landscape_text.configure(text_color="#161616")

for widget in [portrait_frame, portrait_symbol, portrait_text]:
    widget.bind("<Button-1>", lambda e:selection("Portrait"))
    widget.bind("<Enter>", hover_in_portrait)
    widget.bind("<Leave>", hover_out_portrait)
for widget in [landscape_frame, landscape_symbol, landscape_text]:
    widget.bind("<Button-1>", lambda e:selection("Landscape"))
    widget.bind("<Enter>", hover_in_landscape)
    widget.bind("<Leave>", hover_out_landscape)

container = ctk.CTkFrame(equal_padding, fg_color="transparent")
container.pack(fill="x", pady=(30,0))

ps_label = ctk.CTkLabel(container, text="Page Size", text_color="#1c1c1e", font=("Segoe UI",20))
ps_label.pack(side="top", anchor="w")

border_frame = ctk.CTkFrame(container, fg_color="#FFFFFF", border_width=3)
border_frame.pack(fill="x", pady=(10,0))

ps_dropdown = ctk.CTkOptionMenu(border_frame,values=["Fit(Same page size as image)", "A4(297x210 mm)", "US Letter(215x279.4 mm)",],
                            text_color="#1c1c1e", font=("Segoe UI",20), fg_color="#F5F5F5", height=50, button_color="#F5F5F5", button_hover_color="#F5F5F5", dropdown_fg_color="#F5F5F5", dropdown_text_color="#1c1c1e", dropdown_hover_color="#3B82F6", command=preview_frame)
ps_dropdown.pack(fill="x",padx=5 ,pady=5)

mar_frame = ctk.CTkFrame(equal_padding, fg_color="transparent")
mar_frame.pack(fill="x", pady=(30,0))

mar_label = ctk.CTkLabel(mar_frame, text="Margin", text_color="#1c1c1e", font=("Segoe UI",20))
mar_label.pack(side="top", anchor="w")

nmar_button = ctk.CTkButton(mar_frame, text="No\nMargin", fg_color="#F5F5F5", text_color="#999494", font=("Segoe UI",20), width=130, height=140, hover_color="#CCBDBD", border_width=1)
nmar_button.pack(side="left", expand=True,fill="x" ,padx=(0,5), pady=(10,0))

smar_button = ctk.CTkButton(mar_frame, text="Small\nMargin", fg_color="#F5F5F5", text_color="#999494", font=("Segoe UI",20), width=130, height=140, hover_color="#CCBDBD", border_width=8)
smar_button.pack(side="left", expand=True,fill="x" ,padx=5, pady=(10,0))

bmar_button = ctk.CTkButton(mar_frame, text="Big\nMargin", fg_color="#F5F5F5", text_color="#999494", font=("Segoe UI",20), width=130, height=140, hover_color="#CCBDBD", border_width=16)
bmar_button.pack(side="left", expand=True,fill="x" ,padx=(5,0), pady=(10,0))

activness_mar = "No Margin"
def selection_mar(select_mar):
    global activness_mar
    activness_mar = select_mar
    if select_mar == "No Margin":
        nmar_button.configure(fg_color="#F5F5F5", border_color="#E5322D", text_color="#E5322D")
        smar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")
        bmar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")
    elif select_mar == "Small Margin":
        nmar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")
        smar_button.configure(fg_color="#F5F5F5", border_color="#E5322D", text_color="#E5322D")
        bmar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")
    else:
        nmar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")
        smar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")
        bmar_button.configure(fg_color="#F5F5F5", border_color="#E5322D", text_color="#E5322D")
    preview_frame()

def hover_in_nmar(event):
    if activness_mar != "No Margin":
        nmar_button.configure(fg_color="#CCBDBD", border_color="#161616", text_color="#161616")

def hover_out_nmar(event):
    if activness_mar != "No Margin":
        nmar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")

def hover_in_smar(event):
    if activness_mar != "Small Margin":
        smar_button.configure(fg_color="#CCBDBD", border_color="#161616", text_color="#161616")

def hover_out_smar(event):
    if activness_mar != "Small Margin":
        smar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")

def hover_in_bmar(event):
    if activness_mar != "Big Margin":
        bmar_button.configure(fg_color="#CCBDBD", border_color="#161616", text_color="#161616")

def hover_out_bmar(event):
    if activness_mar != "Big Margin":
        bmar_button.configure(fg_color="#F5F5F5", border_color="#999494", text_color="#999494")

nmar_button.bind("<Button-1>", lambda e: selection_mar("No Margin"))
nmar_button.bind("<Enter>", hover_in_nmar)
nmar_button.bind("<Leave>", hover_out_nmar)

smar_button.bind("<Button-1>", lambda e: selection_mar("Small Margin"))
smar_button.bind("<Enter>", hover_in_smar)
smar_button.bind("<Leave>", hover_out_smar)

bmar_button.bind("<Button-1>", lambda e: selection_mar("Big Margin"))
bmar_button.bind("<Enter>", hover_in_bmar)
bmar_button.bind("<Leave>", hover_out_bmar)

checkbox = ctk.CTkCheckBox(equal_padding, text="  Separate PDF", font=("Segoe UI",13), checkmark_color="#52D273", text_color="#555555", border_color="#161616", hover_color="#FFFFFF", border_width=1, fg_color="#FFFFFF")
checkbox.pack(anchor="w", pady=(30,0))

ctp_frame = ctk.CTkFrame(frame2_2, fg_color="transparent")
ctp_frame.pack(side="bottom",fill="x", pady=20)

ctp_button = ctk.CTkButton(ctp_frame, text="Convert To Pdf →", fg_color="#E5322D", text_color="#FFFFFF", height=80, corner_radius=10, hover_color="#9E0904", font=("Segoe UI",30), command=convert_into_pdf)
ctp_button.pack(fill="x", padx=5, pady=5)

selection_mar("No Margin")
selection("Portrait")
root.mainloop()