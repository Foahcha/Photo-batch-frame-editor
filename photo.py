import os
from PIL import Image, ImageOps
from tkinter import filedialog, Tk, Label, Button, Scale, HORIZONTAL, colorchooser
import tkinter as tk

# === FONCTION PRINCIPALE DE RECADRAGE ===
def convert_to_4_5(image, border_outer=0, bg_color=(255, 255, 255, 255), border_inner=0, bg_color_inner=(255, 255, 255, 255)):
    original = image.convert("RGBA")
    ow, oh = original.size

    target_ratio = 4 / 5
    new_height = int(ow / target_ratio)

    if new_height < oh:
        new_height = oh + border_outer
        new_width = int(new_height * target_ratio)
    else:
        new_width = ow + border_outer

    final_w = new_width
    final_h = new_height

    # Crée les calques
    inner_img = Image.new("RGBA", (ow + border_inner * 2, oh + border_inner * 2), bg_color_inner)
    outer_img = Image.new("RGBA", (final_w, final_h), bg_color)

    # Centrer
    paste_x_inner = (inner_img.width - ow) // 2
    paste_y_inner = (inner_img.height - oh) // 2
    inner_img.paste(original, (paste_x_inner, paste_y_inner), mask=original)

    paste_x_outer = (final_w - inner_img.width) // 2
    paste_y_outer = (final_h - inner_img.height) // 2
    outer_img.paste(inner_img, (paste_x_outer, paste_y_outer), mask=inner_img)

    return outer_img


# === TRAITEMENT D'IMAGES ===
def process_images(root, border, bg_color, border_inner, bg_color_inner):
    # Ouvre les boîtes de dialogue en utilisant la même fenêtre Tk principale
    input_dir = filedialog.askdirectory(parent=root, title="Dossier source")
    if not input_dir:
        print("❌ Aucun dossier source sélectionné.")
        return

    output_dir = filedialog.askdirectory(parent=root, title="Dossier destination")
    if not output_dir:
        print("❌ Aucun dossier destination sélectionné.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            filepath = os.path.join(input_dir, filename)
            try:
                with Image.open(filepath) as img:
                    new_img = ImageOps.exif_transpose(img)
                    new_img = convert_to_4_5(new_img, border, bg_color, border_inner, bg_color_inner)
                    output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + "_framed.png")
                    new_img.save(output_path, format="PNG")
                    print(f"✅ Image convertie : {filename}")
            except Exception as e:
                print(f"⚠️ Erreur avec {filename} : {e}")

    print("✅ Toutes les images ont été traitées.")

# === INTERFACE GRAPHIQUE ===
def main():
    root = Tk()
    root.title("🖼️ Recadrage 4:5 - Contrôle du border et couleur")
    root.geometry("500x500")


    border_var = tk.IntVar(value=0)
    border_inner_var = tk.IntVar(value=0)
    rgba_color = [255, 255, 255, 255]        # [R, G, B, A]
    rgba_color_inner = [255, 255, 255, 255]  # [R, G, B, A]

    def choose_color(target_color, color_label):
        color = colorchooser.askcolor(title="Choisis une couleur")
        if color[0]:  # color[0] = (R,G,B)
            r, g, b = map(int, color[0])
            target_color[0:3] = [r, g, b]  # On garde alpha inchangé
            color_label.config(bg=color[1])

    Label(root, text="Bordure extérieure (pixels) :").pack(pady=5)
    border_slider = Scale(root, from_=0, to=1000, orient=HORIZONTAL, variable=border_var)
    border_slider.pack(padx=20, pady=5, fill="x")

    Button(root, text="🎨 Couleur fond", command=lambda: choose_color(rgba_color, color_label)).pack(pady=5)
    color_label = Label(root, text=" ", bg="#FFFFFF", width=20, height=2)
    color_label.pack()
    
    Label(root, text="Bordure intérieure (pixels) :").pack(pady=5)
    border_inner_slider = Scale(root, from_=0, to=500, orient=HORIZONTAL, variable=border_inner_var)
    border_inner_slider.pack(padx=20, pady=5, fill="x")

    Button(root, text="🎨 Couleur cadre", command=lambda: choose_color(rgba_color_inner, color_label_2)).pack(pady=5)
    color_label_2 = Label(root, text=" ", bg="#FFFFFF", width=20, height=2)
    color_label_2.pack()
    
    Label(root, text="Alpha (transparence globale) :").pack(pady=5)
    alpha_slider = Scale(root, from_=0, to=255, orient=HORIZONTAL)
    alpha_slider.set(255)
    alpha_slider.pack(padx=20, pady=5, fill="x")

    def run_conversion():
        rgba_color[3] = alpha_slider.get()
        rgba_color_inner[3] = alpha_slider.get()
        print(f"➡️ Border : {border_var.get()}, Couleur : {rgba_color}")
        process_images(root, border_var.get(), tuple(rgba_color), border_inner_var.get(), tuple(rgba_color_inner))


    Button(root, text="🚀 Lancer le recadrage", command=run_conversion, bg="#4CAF50", fg="white").pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
