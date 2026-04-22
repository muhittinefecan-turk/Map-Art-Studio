import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, simpledialog, ttk
from PIL import Image, ImageTk, ImageDraw
import math
import json
import colorsys
import os
import sys

class MapArtStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Map Art Studio Pro - Dev: Muhittin Efecan Türk")
        self.geometry("1650x950")
        self.configure(bg="#1e1e2e") 

        # --- Durum Değişkenleri ---
        self.original_image = None
        self.placement_img = None
        self.preview_image_pil = None
        self.textured_preview_pil = None
        self.texture_cache = {}
        self.active_export_palette = {}
        
        # Grid ve render verileri
        self.current_disp_w = 0
        self.current_disp_h = 0
        self.current_disp_x0 = 0
        self.current_disp_y0 = 0

        # Palet ve Kategori Verileri
        self.MASTER_PALETTE = {}
        self.block_names_to_rgb = {}
        self.block_images = {}
        self.selected_blocks = set()
        
        # Renk Bazlı Kategoriler
        self.categories = {
            "Kırmızı": [], "Turuncu/Kahve": [], "Sarı": [], "Yeşil": [], 
            "Camgöbeği": [], "Mavi": [], "Mor": [], "Pembe": [], 
            "Beyaz/Açık": [], "Gri": [], "Siyah/Koyu": []
        }

        self.setup_variables()
        self.load_colors_from_json()
        self.setup_ui()
        
        self.show_startup_message()

    def show_startup_message(self):
        total_blocks = len(self.block_names_to_rgb)
        messagebox.showinfo("Hoş Geldiniz!", 
                            "Minecraft Map Art Studio Pro Başarıyla Başlatıldı!\n\n"
                            f"📦 Toplam {total_blocks} blok (colors.json) sisteme yüklendi.\n\n"
                            "🌟 Dev: Muhittin Efecan Türk\n"
                            "💬 Discord: efecan.turk0\n\n"
                            "Bu program size özel olarak tasarlanmıştır. İyi eğlenceler!")

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def setup_variables(self):
        self.size_x_var = tk.IntVar(value=1)
        self.size_y_var = tk.IntVar(value=1)
        self.scale_var = tk.IntVar(value=100)
        self.x_var = tk.IntVar(value=0)
        self.y_var = tk.IntVar(value=0)
        self.bg_color_var = tk.StringVar(value="black")
        self.show_grid_var = tk.BooleanVar(value=True)
        self.search_var = tk.StringVar()
        self.map_type_var = tk.StringVar(value="Zemin (Yatay)")
        
        self.rotation_var = tk.IntVar(value=0)
        self.flip_h_var = tk.BooleanVar(value=False)
        self.flip_v_var = tk.BooleanVar(value=False)
        self.dither_var = tk.BooleanVar(value=False)

    def categorize_by_color(self, h, s, l):
        if l < 18: return "Siyah/Koyu"
        if l > 85: return "Beyaz/Açık"
        if s < 15: return "Gri"
        if h < 15 or h > 345: return "Kırmızı"
        if h < 45: return "Turuncu/Kahve"
        if h < 70: return "Sarı"
        if h < 160: return "Yeşil"
        if h < 210: return "Camgöbeği"
        if h < 270: return "Mavi"
        if h < 315: return "Mor"
        return "Pembe"

    def get_turkish_name(self, eng_name):
        exact_matches = {
            "stone": "Taş", "cobblestone": "Kırık Taş", "dirt": "Toprak", "coarse_dirt": "İri Taneli Toprak",
            "rooted_dirt": "Köklü Toprak", "sand": "Kum", "red_sand": "Kırmızı Kum", "gravel": "Çakıl", 
            "obsidian": "Obsidyen", "crying_obsidian": "Ağlayan Obsidyen", "bedrock": "Katman Kayası", 
            "sponge": "Sünger", "wet_sponge": "Islak Sünger", "glass": "Cam", "tinted_glass": "Renkli Cam", 
            "clay": "Kil", "tuff": "Tüf", "calcite": "Kalsit", "diorite": "Diorit", "granite": "Granit", 
            "andesite": "Andezit", "coal_block": "Kömür Bloğu", "iron_block": "Demir Bloğu", 
            "gold_block": "Altın Bloğu", "diamond_block": "Elmas Bloğu", "emerald_block": "Zümrüt Bloğu", 
            "lapis_block": "Lapis Lazuli Bloğu", "copper_block": "Bakır Bloğu", "raw_iron_block": "Ham Demir Bloğu", 
            "raw_gold_block": "Ham Altın Bloğu", "raw_copper_block": "Ham Bakır Bloğu", "netherite_block": "Netherit Bloğu",
            "redstone_block": "Kızıltaş Bloğu", "snow": "Kar", "ice": "Buz", "packed_ice": "Paketlenmiş Buz",
            "blue_ice": "Mavi Buz", "glowstone": "Işık Taşı", "shroomlight": "Mantarışığı", "magma_block": "Magma Bloğu", 
            "netherrack": "Nether Taşı", "soul_sand": "Ruh Kumu", "soul_soil": "Ruh Toprağı", "bone_block": "Kemik Bloğu",
            "end_stone": "End Taşı", "purpur_block": "Purpur Bloğu", "prismarine": "Prizmarin",
            "dark_prismarine": "Koyu Prizmarin", "prismarine_bricks": "Prizmarin Tuğlası", "melon": "Karpuz", 
            "pumpkin": "Balkabağı", "hay_block": "Saman Balyası", "target": "Hedef", "honey_block": "Bal Bloğu", 
            "honeycomb_block": "Petek Bloğu", "slime_block": "Balçık Bloğu", "amethyst_block": "Ametist Bloğu", 
            "budding_amethyst": "Tomurcuklanan Ametist", "mud": "Çamur", "packed_mud": "Paketlenmiş Çamur", 
            "mud_bricks": "Çamur Tuğlası", "deepslate": "Derin Arduvaz", "cobbled_deepslate": "Kırık Derin Arduvaz",
            "polished_deepslate": "Cilalı Derin Arduvaz", "deepslate_bricks": "Derin Arduvaz Tuğlası",
            "deepslate_tiles": "Derin Arduvaz Karoları", "blackstone": "Karataş", "polished_blackstone": "Cilalı Karataş", 
            "polished_blackstone_bricks": "Cilalı Karataş Tuğlası", "gilded_blackstone": "Yaldızlı Karataş", 
            "basalt": "Bazalt", "polished_basalt": "Cilalı Bazalt", "smooth_basalt": "Düz Bazalt", 
            "smooth_stone": "Düz Taş", "stone_bricks": "Taş Tuğla", "mossy_cobblestone": "Yosunlu Kırık Taş", 
            "mossy_stone_bricks": "Yosunlu Taş Tuğla", "bricks": "Tuğla", "bookshelf": "Kitaplık", 
            "note_block": "Nota Bloğu", "spawner": "Canavaran", "terracotta": "Terakota", "moss_block": "Yosun Bloğu", 
            "nether_wart_block": "Nether Siğili Bloğu", "warped_wart_block": "Çarpık Siğil Bloğu", 
            "structure_block": "Yapı Bloğu", "suspicious_sand": "Şüpheli Kum", "suspicious_gravel": "Şüpheli Çakıl",
            "mushroom_stem": "Mantar Sapı", "red_mushroom_block": "Kırmızı Mantar Bloğu", "brown_mushroom_block": "Kahverengi Mantar Bloğu",
            "red_nether_bricks": "Kırmızı Nether Tuğlası", "nether_bricks": "Nether Tuğlası",
            "cracked_nether_bricks": "Çatlak Nether Tuğlası", "chiseled_nether_bricks": "Oyma Nether Tuğlası",
            "chiseled_polished_blackstone": "Oyma Cilalı Karataş", "cracked_polished_blackstone_bricks": "Çatlak Cilalı Karataş Tuğlası",
            "cracked_deepslate_bricks": "Çatlak Derin Arduvaz Tuğlası", "cracked_deepslate_tiles": "Çatlak Derin Arduvaz Karoları",
            "chiseled_deepslate": "Oyma Derin Arduvaz", "cracked_stone_bricks": "Çatlak Taş Tuğla",
            "chiseled_stone_bricks": "Oyma Taş Tuğla", "chiseled_sandstone": "Oyma Kumtaşı", "chiseled_red_sandstone": "Oyma Kırmızı Kumtaşı",
            "chiseled_quartz_block": "Oyma Kuvars Bloğu", "quartz_bricks": "Kuvars Tuğla", "quartz_pillar": "Kuvars Sütun",
            "purpur_pillar": "Purpur Sütun", "redstone_lamp": "Kızıltaş Lambası", "redstone_lamp_on": "Yanan Kızıltaş Lambası",
            "coal_ore": "Kömür Cevheri", "iron_ore": "Demir Cevheri", "gold_ore": "Altın Cevheri",
            "diamond_ore": "Elmas Cevheri", "emerald_ore": "Zümrüt Cevheri", "lapis_ore": "Lapis Lazuli Cevheri",
            "redstone_ore": "Kızıltaş Cevheri", "copper_ore": "Bakır Cevheri", "nether_gold_ore": "Nether Altın Cevheri",
            "nether_quartz_ore": "Nether Kuvars Cevheri", "deepslate_coal_ore": "Derin Arduvaz Kömür Cevheri",
            "deepslate_iron_ore": "Derin Arduvaz Demir Cevheri", "deepslate_gold_ore": "Derin Arduvaz Altın Cevheri",
            "deepslate_diamond_ore": "Derin Arduvaz Elmas Cevheri", "deepslate_emerald_ore": "Derin Arduvaz Zümrüt Cevheri",
            "deepslate_lapis_ore": "Derin Arduvaz Lapis Lazuli Cevheri", "deepslate_redstone_ore": "Derin Arduvaz Kızıltaş Cevheri",
            "deepslate_copper_ore": "Derin Arduvaz Bakır Cevheri", "oxidized_copper": "Oksitlenmiş Bakır", "weathered_copper": "Yıpranmış Bakır",
            "exposed_copper": "Açık Bakır", "cut_copper": "Kesik Bakır", "oxidized_cut_copper": "Oksitlenmiş Kesik Bakır",
            "weathered_cut_copper": "Yıpranmış Kesik Bakır", "exposed_cut_copper": "Açık Kesik Bakır",
            "brain_coral_block": "Beyin Mercan Bloğu", "bubble_coral_block": "Baloncuk Mercan Bloğu",
            "fire_coral_block": "Ateş Mercan Bloğu", "horn_coral_block": "Boynuz Mercan Bloğu", "tube_coral_block": "Tüp Mercan Bloğu",
            "dead_brain_coral_block": "Ölü Beyin Mercan Bloğu", "dead_bubble_coral_block": "Ölü Baloncuk Mercan Bloğu",
            "dead_fire_coral_block": "Ölü Ateş Mercan Bloğu", "dead_horn_coral_block": "Ölü Boynuz Mercan Bloğu",
            "dead_tube_coral_block": "Ölü Tüp Mercan Bloğu", "flowering_azalea_leaves": "Çiçekli Açelya Yaprakları",
            "azalea_leaves": "Açelya Yaprakları", "ochre_froglight": "Sarı Kurbağaışığı", "verdant_froglight": "Yeşil Kurbağaışığı",
            "pearlescent_froglight": "Sedefli Kurbağaışığı", "muddy_mangrove_roots": "Çamurlu Mangrov Kökleri",
            "bamboo_mosaic": "Bambu Mozaik", "lodestone": "Manyetit", "quartz_block": "Kuvars Bloğu"
        }

        colors = {
            "white": "Beyaz", "orange": "Turuncu", "magenta": "Eflatun", "light_blue": "Açık Mavi",
            "yellow": "Sarı", "lime": "Açık Yeşil", "pink": "Pembe", "gray": "Gri",
            "light_gray": "Açık Gri", "cyan": "Camgöbeği", "purple": "Mor", "blue": "Mavi",
            "brown": "Kahverengi", "green": "Yeşil", "red": "Kırmızı", "black": "Siyah"
        }
        materials = {
            "concrete_powder": "Beton Tozu", "concrete": "Beton", "wool": "Yün",
            "terracotta": "Terakota", "stained_glass": "Vitray", "shulker_box": "Shulker Kutusu"
        }
        woods = {
            "oak": "Meşe", "spruce": "Ladin", "birch": "Huş", "jungle": "Orman Ağacı",
            "acacia": "Akasya", "dark_oak": "Koyu Meşe", "mangrove": "Mangrov", "cherry": "Kiraz",
            "crimson": "Kızıl", "warped": "Çarpık", "bamboo": "Bambu"
        }
        wood_types = {
            "planks": "Tahtası", "leaves": "Yaprakları", "log": "Kütüğü", "stem": "Sapı",
            "wood": "Odunu", "hyphae": "Hifleri", "stripped_log": "Soyulmuş Kütüğü",
            "stripped_stem": "Soyulmuş Sapı", "stripped_wood": "Soyulmuş Odunu", "stripped_hyphae": "Soyulmuş Hifleri",
            "block": "Bloğu", "stripped_block": "Soyulmuş Bloğu"
        }
        suffixes = {
            "_top": " (Üst)", "_side": " (Yan)", "_bottom": " (Alt)", "_0": " (0)", "_1": " (1)", "_2": " (2)", "_3": " (3)"
        }

        suffix_str = ""
        temp_name = eng_name
        for suf, tr_suf in suffixes.items():
            if temp_name.endswith(suf):
                suffix_str = tr_suf
                temp_name = temp_name[:-len(suf)]
                break

        res = temp_name
        if temp_name in exact_matches:
            res = exact_matches[temp_name]
        else:
            matched_color = False
            for col_en, col_tr in colors.items():
                if temp_name.startswith(col_en + "_"):
                    mat_en = temp_name[len(col_en)+1:]
                    if mat_en in materials:
                        res = f"{col_tr} {materials[mat_en]}"
                        matched_color = True
                        break
            if not matched_color:
                is_stripped = False
                wood_name = temp_name
                if wood_name.startswith("stripped_"):
                    is_stripped = True
                    wood_name = wood_name[9:]
                for w_en, w_tr in woods.items():
                    if wood_name.startswith(w_en + "_"):
                        type_en = wood_name[len(w_en)+1:]
                        full_type_en = ("stripped_" if is_stripped else "") + type_en
                        if full_type_en in wood_types:
                            res = f"{w_tr} {wood_types[full_type_en]}"
                            break
                        elif type_en in wood_types:
                            res = f"{w_tr} {wood_types[type_en]}"
                            if is_stripped: res = "Soyulmuş " + res
                            break
        if res == temp_name:
            res = temp_name.replace("_", " ").title()
        return res + suffix_str

    def load_colors_from_json(self):
        json_path = self.resource_path("colors.json")
        if not os.path.exists(json_path):
            print("colors.json dosyası bulunamadı!")
            return
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                colors_data = json.load(f)

            for item in colors_data:
                name = item["name"]
                h, s, l = item["hsl"]
                image_file = item.get("image", "")
                
                r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
                rgb = (int(r * 255), int(g * 255), int(b * 255))
                block_id = "minecraft:" + name.replace("_top", "").replace("_side", "").replace("_bottom", "")
                
                tr_name = self.get_turkish_name(name)
                
                self.MASTER_PALETTE[rgb] = (tr_name, block_id, name)
                self.block_names_to_rgb[tr_name] = rgb
                self.block_images[tr_name] = image_file
                self.selected_blocks.add(tr_name)

                cat = self.categorize_by_color(h, s, l)
                self.categories[cat].append(tr_name)
        except Exception as e:
            print("JSON Hatası:", e)

    def get_block_texture(self, tr_name):
        if tr_name in self.texture_cache:
            return self.texture_cache[tr_name]
        
        img_file = self.block_images.get(tr_name, "")
        img_path = self.resource_path(os.path.join("blocks", img_file)) if img_file else ""
        
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path).convert("RGB")
                img = img.resize((16, 16), Image.Resampling.NEAREST)
                self.texture_cache[tr_name] = img
                return img
            except: pass
        
        rgb = self.block_names_to_rgb.get(tr_name, (0,0,0))
        img = Image.new("RGB", (16, 16), rgb)
        self.texture_cache[tr_name] = img
        return img

    def setup_ui(self):
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#1e1e2e", sashwidth=6, sashrelief=tk.FLAT)
        self.paned.pack(fill=tk.BOTH, expand=True)

        left_bg = "#282a36"
        self.left_panel = tk.Frame(self.paned, bg=left_bg, width=640)
        self.paned.add(self.left_panel)

        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=left_bg, borderwidth=0)
        style.configure('TNotebook.Tab', background="#44475a", foreground="white", padding=[10, 5], font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#6272a4')], foreground=[('selected', 'white')])

        self.notebook = ttk.Notebook(self.left_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_layout = tk.Frame(self.notebook, bg=left_bg)
        self.tab_palette = tk.Frame(self.notebook, bg=left_bg)
        self.notebook.add(self.tab_layout, text="📐 Yerleşim ve 3D Düzenleyici")
        self.notebook.add(self.tab_palette, text="🎨 Renk & Filtre & Profil")

        self.build_layout_tab(left_bg)
        self.build_palette_tab(left_bg)

        # AKSİYON VE İMZA PANELİ
        action_frame = tk.Frame(self.left_panel, bg=left_bg)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(action_frame, text="⛏️ BLOKLARA ÇEVİR (TEXTURE RENDER)", command=self.process_map_art, bg="#50fa7b", fg="black", font=("Arial", 12, "bold"), height=2).pack(fill=tk.X, pady=5)
        
        out_f = tk.Frame(action_frame, bg=left_bg)
        out_f.pack(fill=tk.X)
        tk.Button(out_f, text="💾 Resim Kaydet", command=self.save_png, bg="#8be9fd", fg="black").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(out_f, text="🧊 Litematica İndir", command=self.export_litematica, bg="#f1fa8c", fg="black").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        tk.Label(action_frame, text="Dev: Muhittin Efecan Türk | Discord: efecan.turk0", bg=left_bg, fg="#ff79c6", font=("Arial", 8, "bold")).pack(pady=5)

        # --- SAĞ PANEL (CANVAS VE VİTRİN) ---
        self.right_panel = tk.Frame(self.paned, bg="#1e1e2e")
        self.paned.add(self.right_panel)

        self.canvas = tk.Canvas(self.right_panel, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        used_frame = tk.LabelFrame(self.right_panel, text="Bu Haritada Kullanılacak Bloklar", bg="#282a36", fg="#f1fa8c", font=("Arial", 10, "bold"), padx=5, pady=5)
        used_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(used_frame, text="▲ Yukarı Kaydır", command=lambda: self.vitrin_canvas.yview_scroll(-1, "units"), bg="#44475a", fg="white", bd=0, font=("Arial", 8)).pack(fill=tk.X)
        
        list_container = tk.Frame(used_frame, bg="#282a36")
        list_container.pack(fill=tk.X, pady=2)
        
        self.vitrin_canvas = tk.Canvas(list_container, bg="#282a36", height=150, highlightthickness=0)
        v_scroll = ttk.Scrollbar(list_container, orient="vertical", command=self.vitrin_canvas.yview)
        self.vitrin_inner = tk.Frame(self.vitrin_canvas, bg="#282a36")
        
        self.vitrin_inner.bind("<Configure>", lambda e: self.vitrin_canvas.configure(scrollregion=self.vitrin_canvas.bbox("all")))
        self.vitrin_canvas.create_window((0, 0), window=self.vitrin_inner, anchor="nw")
        self.vitrin_canvas.configure(yscrollcommand=v_scroll.set)
        
        self.vitrin_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.vitrin_canvas.bind_all("<MouseWheel>", lambda e: self.vitrin_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        tk.Button(used_frame, text="▼ Aşağı Kaydır", command=lambda: self.vitrin_canvas.yview_scroll(1, "units"), bg="#44475a", fg="white", bd=0, font=("Arial", 8)).pack(fill=tk.X)

        self.update_lists()

    def build_layout_tab(self, bg_col):
        """Yerleşim Sekmesi: Çok daha düzenli ve gelişmiş araçlarla dolu!"""
        # 1. TEMEL İŞLEMLER
        file_f = tk.LabelFrame(self.tab_layout, text="1. Görsel Kaynağı ve Hızlı Ayarlar", bg=bg_col, fg="#8be9fd", font=("Arial", 10, "bold"), padx=10, pady=5)
        file_f.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Button(file_f, text="📸 Görsel Yükle", command=self.load_image, bg="#bd93f9", fg="black", font=("Arial", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(file_f, text="⤢ Ekrana Sığdır", command=self.fit_to_canvas, bg="#f1fa8c", fg="black", font=("Arial", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(file_f, text="↺ Sıfırla", command=self.reset_placement, bg="#ff5555", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # 2. DÖNDÜRME VE AYNALAMA
        trans_f = tk.LabelFrame(self.tab_layout, text="2. Döndürme ve Aynalama", bg=bg_col, fg="#8be9fd", font=("Arial", 10, "bold"), padx=10, pady=5)
        trans_f.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Button(trans_f, text="↩️ Sola 90°", command=lambda: self.rotate_image(90), bg="#44475a", fg="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(trans_f, text="↪️ Sağa 90°", command=lambda: self.rotate_image(-90), bg="#44475a", fg="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(trans_f, text="↔️ Yatay Aynala", command=lambda: self.flip_image('h'), bg="#44475a", fg="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(trans_f, text="↕️ Dikey Aynala", command=lambda: self.flip_image('v'), bg="#44475a", fg="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # 3. İNŞA VE HARİTA AYARLARI
        place_group = tk.LabelFrame(self.tab_layout, text="3. Oyun İçi İnşa ve Harita", bg=bg_col, fg="#8be9fd", font=("Arial", 10, "bold"), padx=10, pady=5)
        place_group.pack(fill=tk.X, pady=5, padx=10)

        type_f = tk.Frame(place_group, bg=bg_col)
        type_f.pack(fill=tk.X, pady=5)
        tk.Label(type_f, text="İnşa Tipi:", bg=bg_col, fg="white", width=12, anchor="w").pack(side=tk.LEFT)
        type_cb = ttk.Combobox(type_f, textvariable=self.map_type_var, values=["Zemin (Yatay)", "Duvar (Dikey)", "3D (Merdivenli)"], state="readonly")
        type_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        type_cb.bind("<<ComboboxSelected>>", self.check_height_limit)

        size_f = tk.Frame(place_group, bg=bg_col)
        size_f.pack(fill=tk.X, pady=5)
        tk.Label(size_f, text="Harita Miktarı:", bg=bg_col, fg="white", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Spinbox(size_f, from_=1, to=10, textvariable=self.size_x_var, width=3, command=self.update_placement).pack(side=tk.LEFT)
        tk.Label(size_f, text="X", bg=bg_col, fg="white", padx=5).pack(side=tk.LEFT)
        tk.Spinbox(size_f, from_=1, to=10, textvariable=self.size_y_var, width=3, command=self.check_height_limit).pack(side=tk.LEFT)
        tk.Checkbutton(size_f, text="Grid Numaraları", variable=self.show_grid_var, bg=bg_col, fg="#ffb86c", selectcolor="#444", command=self.update_placement).pack(side=tk.LEFT, padx=10)

        bg_f = tk.Frame(place_group, bg=bg_col)
        bg_f.pack(fill=tk.X, pady=5)
        tk.Label(bg_f, text="Boşluk Rengi:", bg=bg_col, fg="white", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Radiobutton(bg_f, text="Siyah", variable=self.bg_color_var, value="black", bg=bg_col, fg="white", selectcolor="#444", command=self.update_placement).pack(side=tk.LEFT)
        tk.Radiobutton(bg_f, text="Beyaz", variable=self.bg_color_var, value="white", bg=bg_col, fg="white", selectcolor="#444", command=self.update_placement).pack(side=tk.LEFT)

        # 4. GÖRÜNTÜ İŞLEME
        render_f = tk.LabelFrame(self.tab_layout, text="4. Görüntü İşleme", bg=bg_col, fg="#8be9fd", font=("Arial", 10, "bold"), padx=10, pady=5)
        render_f.pack(fill=tk.X, pady=5, padx=10)
        tk.Checkbutton(render_f, text="Dithering (Gelişmiş Renk Harmanlama / Pikselleri Yumuşat)", variable=self.dither_var, bg=bg_col, fg="#50fa7b", selectcolor="#444").pack(anchor="w")

        # 5. YENİ: HASSAS KONTROLLER (SÜRGÜSÜZ, ARTI-EKSİ BUTONLU)
        ctrl_group = tk.LabelFrame(self.tab_layout, text="5. Hassas Kaydırma ve Boyutlandırma", bg=bg_col, fg="#8be9fd", font=("Arial", 10, "bold"), padx=10, pady=5)
        ctrl_group.pack(fill=tk.X, pady=5, padx=10)
        
        self.create_step_control_row(ctrl_group, "Boyut (%)", self.scale_var, step=1, big_step=10, v_min=1, v_max=2000)
        self.create_step_control_row(ctrl_group, "X Ekseni", self.x_var, step=1, big_step=10, v_min=-5000, v_max=5000)
        self.create_step_control_row(ctrl_group, "Y Ekseni", self.y_var, step=1, big_step=10, v_min=-5000, v_max=5000)

    def create_step_control_row(self, parent, label, var, step, big_step, v_min, v_max):
        """Sürgü (Slider) yerine hassas Ayar (+/-) butonları oluşturur."""
        f = tk.Frame(parent, bg="#282a36")
        f.pack(fill=tk.X, pady=4)
        tk.Label(f, text=label, bg="#282a36", fg="white", width=12, anchor="w", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        def adjust(val):
            new_val = var.get() + val
            if new_val < v_min: new_val = v_min
            if new_val > v_max: new_val = v_max
            var.set(new_val)
            self.update_placement()

        # Eksi Butonları
        tk.Button(f, text=f"-{big_step}", command=lambda: adjust(-big_step), bg="#ff5555", fg="white", width=3, bd=1).pack(side=tk.LEFT, padx=1)
        tk.Button(f, text="-", command=lambda: adjust(-step), bg="#ff5555", fg="white", width=2, bd=1).pack(side=tk.LEFT, padx=1)
        
        # Sayı Giriş Kutusu
        e = tk.Entry(f, textvariable=var, width=6, bg="#44475a", fg="#50fa7b", insertbackground="white", justify="center", font=("Arial", 11, "bold"), bd=0)
        e.pack(side=tk.LEFT, padx=10, ipady=3)
        e.bind("<Return>", lambda event: self.update_placement())
        
        # Artı Butonları
        tk.Button(f, text="+", command=lambda: adjust(step), bg="#50fa7b", fg="black", width=2, bd=1).pack(side=tk.LEFT, padx=1)
        tk.Button(f, text=f"+{big_step}", command=lambda: adjust(big_step), bg="#50fa7b", fg="black", width=3, bd=1).pack(side=tk.LEFT, padx=1)

    # --- YENİ EKLENEN YERLEŞİM (LAYOUT) FONKSİYONLARI ---
    def fit_to_canvas(self):
        if not self.original_image: return
        
        mw = self.size_x_var.get() * 128
        mh = self.size_y_var.get() * 128
        img_w, img_h = self.original_image.size
        
        if self.rotation_var.get() % 180 != 0:
            img_w, img_h = img_h, img_w
            
        scale_x = mw / img_w
        scale_y = mh / img_h
        best_scale = min(scale_x, scale_y) * 100
        
        self.scale_var.set(int(best_scale))
        self.x_var.set(0)
        self.y_var.set(0)
        self.update_placement()

    def reset_placement(self):
        self.scale_var.set(100)
        self.x_var.set(0)
        self.y_var.set(0)
        self.rotation_var.set(0)
        self.flip_h_var.set(False)
        self.flip_v_var.set(False)
        self.update_placement()

    def rotate_image(self, angle):
        curr_angle = self.rotation_var.get()
        self.rotation_var.set((curr_angle + angle) % 360)
        self.update_placement()

    def flip_image(self, mode):
        if mode == 'h':
            self.flip_h_var.set(not self.flip_h_var.get())
        elif mode == 'v':
            self.flip_v_var.set(not self.flip_v_var.get())
        self.update_placement()

    def check_height_limit(self, *args):
        m_type = self.map_type_var.get()
        y_val = self.size_y_var.get()
        if m_type == "Duvar (Dikey)" and y_val > 2:
            messagebox.showwarning("Yükseklik Limiti", "Minecraft'ta yükseklik sınırı 320 bloktur.\nDikey (Duvar) modunda 2 haritadan (256 blok) fazlası dünyaya sığmayabilir!\nDeğer 2'ye sabitlendi.")
            self.size_y_var.set(2)
        self.update_placement()

    def build_palette_tab(self, bg_col):
        profile_frame = tk.LabelFrame(self.tab_palette, text="Renk Profili (İçe/Dışa Aktar)", bg=bg_col, fg="white", font=("Arial", 10, "bold"), padx=5, pady=5)
        profile_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(profile_frame, text="📂 Profili Yükle (Import)", command=self.import_profile, bg="#8be9fd", fg="black").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(profile_frame, text="💾 Profili Kaydet (Export)", command=self.export_profile, bg="#f1fa8c", fg="black").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        cat_group = tk.LabelFrame(self.tab_palette, text="Renk Ailesine Göre Aç/Kapat", bg=bg_col, fg="white", font=("Arial", 10, "bold"), padx=5, pady=5)
        cat_group.pack(fill=tk.X, pady=5)
        
        self.cat_btns = {}
        btn_container = tk.Frame(cat_group, bg=bg_col)
        btn_container.pack(fill=tk.X)
        r, c = 0, 0
        for cat in self.categories.keys():
            b = tk.Button(btn_container, text=cat, font=("Arial", 8, "bold"), width=12, bg="#50fa7b", fg="black", command=lambda x=cat: self.toggle_category(x))
            b.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            btn_container.grid_columnconfigure(c, weight=1)
            self.cat_btns[cat] = b
            c += 1
            if c > 2: r += 1; c = 0

        list_group = tk.Frame(self.tab_palette, bg=bg_col)
        list_group.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(list_group, text="🔍 Türkçe Kelime ile Ara:", bg=bg_col, fg="white").pack(anchor="w")
        tk.Entry(list_group, textvariable=self.search_var, bg="#44475a", fg="white", insertbackground="white").pack(fill=tk.X, pady=2)
        self.search_var.trace_add("write", self.update_lists)

        tk.Label(list_group, text="(İpucu: Shift'e basılı tutarak aralıktaki tüm blokları seçebilirsiniz)", bg=bg_col, fg="#f1fa8c", font=("Arial", 8)).pack(anchor="w", pady=(5,0))

        # YENİ: Liste başlıkları ve dinamik blok sayaçları eklendi
        lbl_frame = tk.Frame(list_group, bg=bg_col)
        lbl_frame.pack(fill=tk.X, pady=(5,0))
        
        self.lbl_unselected_title = tk.Label(lbl_frame, text="Kullanılmayanlar (0)", bg=bg_col, fg="#ff5555", font=("Arial", 9, "bold"))
        self.lbl_unselected_title.pack(side=tk.LEFT, padx=5)
        
        self.lbl_selected_title = tk.Label(lbl_frame, text="Kullanılacaklar (0)", bg=bg_col, fg="#50fa7b", font=("Arial", 9, "bold"))
        self.lbl_selected_title.pack(side=tk.RIGHT, padx=5)

        boxes_frame = tk.Frame(list_group, bg=bg_col)
        boxes_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        left_lb_frame = tk.Frame(boxes_frame, bg=bg_col)
        left_lb_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_x_left = tk.Scrollbar(left_lb_frame, orient=tk.HORIZONTAL)
        self.lb_unselected = tk.Listbox(left_lb_frame, selectmode=tk.EXTENDED, bg="#44475a", fg="#ff5555", font=("Arial", 9), xscrollcommand=sc_x_left.set)
        sc_x_left.config(command=self.lb_unselected.xview)
        sc_x_left.pack(side=tk.BOTTOM, fill=tk.X)
        self.lb_unselected.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        move_btn_frame = tk.Frame(boxes_frame, bg=bg_col)
        move_btn_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(move_btn_frame, text=">>", command=self.move_to_selected, bg="#6272a4", fg="white").pack(pady=5)
        tk.Button(move_btn_frame, text="<<", command=self.move_to_unselected, bg="#6272a4", fg="white").pack(pady=5)
        
        right_lb_frame = tk.Frame(boxes_frame, bg=bg_col)
        right_lb_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_x_right = tk.Scrollbar(right_lb_frame, orient=tk.HORIZONTAL)
        self.lb_selected = tk.Listbox(right_lb_frame, selectmode=tk.EXTENDED, bg="#2b303b", fg="#50fa7b", font=("Arial", 9), xscrollcommand=sc_x_right.set)
        sc_x_right.config(command=self.lb_selected.xview)
        sc_x_right.pack(side=tk.BOTTOM, fill=tk.X)
        self.lb_selected.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        btn_all_frame = tk.Frame(list_group, bg=bg_col)
        btn_all_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_all_frame, text="Bulunanları Ekle", command=self.add_all_searched, fg="black", bg="#f1fa8c").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        tk.Button(btn_all_frame, text="Bulunanları Çıkar", command=self.remove_all_searched, fg="black", bg="#ff5555").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

    def export_profile(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Renk Profili", "*.json")], title="Profili Kaydet")
        if not path: return
        try:
            profile_data = list(self.selected_blocks)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Başarılı", "Renk profili başarıyla kaydedildi!\nBu dosyayı başka haritalar için yükleyebilirsiniz.")
        except Exception as e:
            messagebox.showerror("Hata", f"Profil kaydedilirken hata oluştu:\n{e}")

    def import_profile(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Renk Profili", "*.json")], title="Profil Seç")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            
            self.selected_blocks.clear()
            for block in profile_data:
                if block in self.block_names_to_rgb:
                    self.selected_blocks.add(block)
            
            self.update_category_buttons()
            self.update_lists()
            messagebox.showinfo("Başarılı", f"Renk profili yüklendi!\nToplam {len(self.selected_blocks)} blok paletinize eklendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Profil yüklenirken hata oluştu:\n{e}")

    def update_category_buttons(self):
        for cat_name, blocks in self.categories.items():
            is_all_selected = all(b in self.selected_blocks for b in blocks)
            if is_all_selected:
                self.cat_btns[cat_name].config(bg="#50fa7b", fg="black")
            else:
                self.cat_btns[cat_name].config(bg="#ff5555", fg="white")

    def toggle_category(self, cat_name):
        blocks = self.categories[cat_name]
        is_active = any(b not in self.selected_blocks for b in blocks)
        if is_active:
            for b in blocks: self.selected_blocks.add(b)
        else:
            for b in blocks: self.selected_blocks.discard(b)
        self.update_category_buttons()
        self.update_lists()

    def update_lists(self, *args):
        query = self.search_var.get().lower()
        self.lb_unselected.delete(0, tk.END)
        self.lb_selected.delete(0, tk.END)
        
        unselected_count = 0
        selected_count = 0
        
        for name in sorted(self.block_names_to_rgb.keys()):
            if query in name.lower():
                if name in self.selected_blocks: 
                    self.lb_selected.insert(tk.END, name)
                    selected_count += 1
                else: 
                    self.lb_unselected.insert(tk.END, name)
                    unselected_count += 1
                    
        # YENİ: Dinamik blok sayaçlarını anlık olarak güncelle
        if hasattr(self, 'lbl_unselected_title'):
            self.lbl_unselected_title.config(text=f"Kullanılmayanlar ({unselected_count})")
            self.lbl_selected_title.config(text=f"Kullanılacaklar ({selected_count})")

    def move_to_selected(self):
        selection = self.lb_unselected.curselection()
        for i in reversed(selection):
            self.selected_blocks.add(self.lb_unselected.get(i))
        self.update_category_buttons()
        self.update_lists()

    def move_to_unselected(self):
        selection = self.lb_selected.curselection()
        for i in reversed(selection):
            self.selected_blocks.discard(self.lb_selected.get(i))
        self.update_category_buttons()
        self.update_lists()

    def add_all_searched(self):
        for i in range(self.lb_unselected.size()):
            self.selected_blocks.add(self.lb_unselected.get(i))
        self.update_category_buttons()
        self.update_lists()

    def remove_all_searched(self):
        for i in range(self.lb_selected.size()):
            self.selected_blocks.discard(self.lb_selected.get(i))
        self.update_category_buttons()
        self.update_lists()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Görseller", "*.png;*.jpg;*.jpeg;*.webp")])
        if path:
            self.original_image = Image.open(path)
            self.fit_to_canvas()

    def update_placement(self):
        if not self.original_image: return
        
        mw = self.size_x_var.get() * 128
        mh = self.size_y_var.get() * 128
        scale = self.scale_var.get() / 100.0
        
        img_temp = self.original_image.copy().convert("RGBA")
        if self.flip_h_var.get():
            img_temp = img_temp.transpose(Image.FLIP_LEFT_RIGHT)
        if self.flip_v_var.get():
            img_temp = img_temp.transpose(Image.FLIP_TOP_BOTTOM)
        if self.rotation_var.get() != 0:
            img_temp = img_temp.rotate(self.rotation_var.get(), expand=True, resample=Image.Resampling.NEAREST)

        nw = max(1, int(img_temp.width * scale))
        nh = max(1, int(img_temp.height * scale))
        img_temp = img_temp.resize((nw, nh), Image.Resampling.NEAREST)
        
        bg_color = (0,0,0) if self.bg_color_var.get() == "black" else (255,255,255)
        self.placement_img = Image.new("RGB", (mw, mh), bg_color)
        
        cx = (mw - nw) // 2 + self.x_var.get()
        cy = (mh - nh) // 2 + self.y_var.get()
        self.placement_img.paste(img_temp, (cx, cy), img_temp)

        self.render_canvas_preview(mw, mh)

    def render_canvas_preview(self, mw, mh):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10: cw, ch = 900, 900
        
        ratio = min(cw/mw, ch/mh)
        dw, dh = int(mw * ratio), int(mh * ratio)
        
        disp = self.placement_img.resize((dw, dh), Image.Resampling.NEAREST)
        self.tk_img = ImageTk.PhotoImage(disp)
        self.canvas.delete("all")
        
        x_center, y_center = cw//2, ch//2
        self.canvas.create_image(x_center, y_center, image=self.tk_img)
        
        self.draw_grid(cw, ch, dw, dh, mw, mh, ratio)

    def draw_grid(self, cw, ch, dw, dh, mw, mh, ratio):
        if not self.show_grid_var.get(): return
        
        x0 = cw//2 - dw//2
        y0 = ch//2 - dh//2
        step = 128 * ratio
        
        grid_color = "#ff5555" if self.bg_color_var.get() == "black" else "#00aaff"
        
        for i in range(self.size_x_var.get()):
            bx = x0 + i * step
            self.canvas.create_line(bx, y0, bx, y0 + dh, fill=grid_color, dash=(4,4))
            for j in range(self.size_y_var.get()):
                by = y0 + j * step
                
                # Gölgeli Grid Yazısı (Okunabilirliği Artırır)
                text_x, text_y = bx + 6, by + 6
                self.canvas.create_text(text_x+1, text_y+1, text=f"Map\n{i+1}x{j+1}", fill="#000000", anchor="nw", font=("Arial", 10, "bold"))
                self.canvas.create_text(text_x, text_y, text=f"Map\n{i+1}x{j+1}", fill="#f1fa8c", anchor="nw", font=("Arial", 10, "bold"))
                
        for j in range(self.size_y_var.get() + 1):
            by = y0 + j * step
            self.canvas.create_line(x0, by, x0 + dw, by, fill=grid_color, dash=(4,4))
        self.canvas.create_line(x0 + dw, y0, x0 + dw, y0 + dh, fill=grid_color, dash=(4,4))

    def process_map_art(self):
        if not self.placement_img: 
            messagebox.showwarning("Hata", "Önce bir resim yüklemelisiniz!")
            return
        
        palette = {self.block_names_to_rgb[n]: n for n in self.selected_blocks}
        if not palette: 
            messagebox.showwarning("Hata", "Lütfen kullanılacak blokları seçin!")
            return

        w, h = self.placement_img.size
        pix = self.placement_img.load()
        
        self.preview_image_pil = Image.new("RGB", (w, h))
        self.textured_preview_pil = Image.new("RGB", (w * 16, h * 16))
        
        block_counts = {}
        
        # Renk Optimizasyonu (Cache)
        color_cache = {}
        def get_closest(curr):
            if curr in color_cache: return color_cache[curr]
            best = min(palette.keys(), key=lambda c: math.dist(curr, c))
            color_cache[curr] = best
            return best

        do_dither = self.dither_var.get()
        if do_dither:
            err_r = [[0.0]*w for _ in range(h)]
            err_g = [[0.0]*w for _ in range(h)]
            err_b = [[0.0]*w for _ in range(h)]

        for y in range(h):
            for x in range(w):
                curr_color = pix[x, y]
                
                if do_dither:
                    old_r = min(255, max(0, curr_color[0] + err_r[y][x]))
                    old_g = min(255, max(0, curr_color[1] + err_g[y][x]))
                    old_b = min(255, max(0, curr_color[2] + err_b[y][x]))
                    
                    best_rgb = get_closest((old_r, old_g, old_b))
                    
                    quant_error_r = old_r - best_rgb[0]
                    quant_error_g = old_g - best_rgb[1]
                    quant_error_b = old_b - best_rgb[2]
                    
                    if x + 1 < w:
                        err_r[y][x+1] += quant_error_r * 7 / 16
                        err_g[y][x+1] += quant_error_g * 7 / 16
                        err_b[y][x+1] += quant_error_b * 7 / 16
                    if y + 1 < h:
                        if x - 1 >= 0:
                            err_r[y+1][x-1] += quant_error_r * 3 / 16
                            err_g[y+1][x-1] += quant_error_g * 3 / 16
                            err_b[y+1][x-1] += quant_error_b * 3 / 16
                        err_r[y+1][x] += quant_error_r * 5 / 16
                        err_g[y+1][x] += quant_error_g * 5 / 16
                        err_b[y+1][x] += quant_error_b * 5 / 16
                        if x + 1 < w:
                            err_r[y+1][x+1] += quant_error_r * 1 / 16
                            err_g[y+1][x+1] += quant_error_g * 1 / 16
                            err_b[y+1][x+1] += quant_error_b * 1 / 16
                else:
                    best_rgb = get_closest(curr_color)

                tr_name = palette[best_rgb]
                
                block_counts[tr_name] = block_counts.get(tr_name, 0) + 1
                self.preview_image_pil.putpixel((x, y), best_rgb)
                
                tex = self.get_block_texture(tr_name)
                self.textured_preview_pil.paste(tex, (x * 16, y * 16))

        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        ratio = min(cw/(w*16), ch/(h*16))
        dw, dh = int(w * 16 * ratio), int(h * 16 * ratio)
        
        final_disp = self.textured_preview_pil.resize((dw, dh), Image.Resampling.NEAREST)
        self.tk_final = ImageTk.PhotoImage(final_disp)
        self.canvas.delete("all")
        self.canvas.create_image(cw//2, ch//2, image=self.tk_final)
        
        self.draw_grid(cw, ch, dw, dh, w, h, ratio * 16)
        
        self.update_used_blocks_vitrin(block_counts)

    def update_used_blocks_vitrin(self, block_counts):
        for widget in self.vitrin_inner.winfo_children():
            widget.destroy()
            
        self.vitrin_icons = []
        sorted_blocks = sorted(block_counts.items(), key=lambda x: x[1], reverse=True)
        
        for tr_name, count in sorted_blocks:
            f = tk.Frame(self.vitrin_inner, bg="#282a36", pady=2)
            f.pack(fill=tk.X, anchor="w")
            
            tex = self.get_block_texture(tr_name).resize((24, 24), Image.Resampling.NEAREST)
            icon = ImageTk.PhotoImage(tex)
            self.vitrin_icons.append(icon)
            tk.Label(f, image=icon, bg="#282a36").pack(side=tk.LEFT, padx=5)
            
            stacks = count // 64
            rem = count % 64
            
            tk.Label(f, text=f"{count:>5} Adet", bg="#282a36", fg="#50fa7b", font=("Consolas", 10, "bold"), width=10, anchor="w").pack(side=tk.LEFT)
            tk.Label(f, text=f"({stacks:>3} st, {rem:>2})", bg="#282a36", fg="#f1fa8c", font=("Consolas", 9), width=12, anchor="w").pack(side=tk.LEFT)
            tk.Label(f, text=tr_name, bg="#282a36", fg="white", font=("Arial", 10, "bold"), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def save_png(self):
        if not self.textured_preview_pil: return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Görseli", "*.png")])
        if path: 
            self.textured_preview_pil.save(path)
            messagebox.showinfo("Başarılı", "Yüksek çözünürlüklü dokulu görsel kaydedildi.")

    def export_litematica(self):
        if not self.preview_image_pil: return
        try:
            from litemapy import Schematic, Region, BlockState
        except ImportError:
            messagebox.showerror("Eksik Kütüphane", "litemapy kütüphanesi yüklü değil!")
            return

        path = filedialog.asksaveasfilename(defaultextension=".litematic", filetypes=[("Litematica Dosyası", "*.litematic")])
        if not path: return

        w, h = self.preview_image_pil.size
        map_type = self.map_type_var.get()
        
        if map_type == "Duvar (Dikey)":
            reg = Region(0, 0, 0, w, h, 1) 
        elif map_type == "3D (Merdivenli)":
            reg = Region(0, 0, 0, w, h, h) 
        else:
            reg = Region(0, 0, 0, w, 1, h) 

        # Dev İmzası Şematik İsminde
        schem = Schematic(name=f"MapArt_{map_type.split()[0]}", author="Muhittin Efecan Türk", regions={"main": reg})
        
        pix = self.preview_image_pil.load()
        id_palette = {rgb: self.MASTER_PALETTE[rgb][1] for rgb in self.MASTER_PALETTE.keys()}

        for z in range(h):
            for x in range(w):
                bid = id_palette.get(pix[x, z], "minecraft:stone")
                block = BlockState(bid)
                
                if map_type == "Duvar (Dikey)":
                    reg.setblock(x, h - z - 1, 0, block) 
                elif map_type == "3D (Merdivenli)":
                    reg.setblock(x, h - z - 1, z, block) 
                else:
                    reg.setblock(x, 0, z, block) 
        
        schem.save(path)
        messagebox.showinfo("Başarılı", f"Şematik ({map_type}) Muhittin Efecan Türk Tarafından Üretildi!\n{path}")

if __name__ == "__main__":
    app = MapArtStudio()
    app.mainloop()