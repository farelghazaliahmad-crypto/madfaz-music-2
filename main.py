import os
import threading
import certifi
import yt_dlp
from ytmusicapi import YTMusic

# Obat Anti SSL Error
os.environ['SSL_CERT_FILE'] = certifi.where()

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, TwoLineAvatarListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

class MusicApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light" 
        self.theme_cls.primary_palette = "Red"
        
        try:
            self.yt = YTMusic()
        except Exception as e:
            print(f"Gagal konek YTMusic: {e}")
        
        self.id_lagu_sekarang = ""
        self.player_suara = None

        layar_utama = MDScreen()
        nav_bawah = MDBottomNavigation()
        nav_bawah.text_color_active = self.theme_cls.primary_color

        # --- TAB HOME ---
        tab_home = MDBottomNavigationItem(name='home', text='Beranda', icon='home')
        layout_home = MDBoxLayout(orientation='vertical', padding=20, spacing=10)
        layout_home.add_widget(MDLabel(text="New for Ahmad", font_style="H4", bold=True, size_hint_y=None, height=50))
        
        scroll_home = MDScrollView()
        list_rekomendasi = MDList()
        songs = [
            ("Lo-fi Guitar Beats", "Chill Vibes"),
            ("Alternative Rock Hits", "Top Tracks"),
            ("Electric Guitar Solo", "Masterclass"),
            ("For Revenge Style", "Emotional Rock")
        ]
        for title, subtitle in songs:
            item = TwoLineAvatarListItem(text=title, secondary_text=subtitle)
            item.add_widget(IconLeftWidget(icon="music-note"))
            list_rekomendasi.add_widget(item)
            
        scroll_home.add_widget(list_rekomendasi)
        layout_home.add_widget(scroll_home)
        tab_home.add_widget(layout_home)

        # --- TAB SEARCH ---
        tab_search = MDBottomNavigationItem(name='search', text='Search', icon='magnify')
        layout_tumpuk = FloatLayout()

        self.bg_image = AsyncImage(source='', allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
        layout_tumpuk.add_widget(self.bg_image)

        lapisan_kaca = MDBoxLayout(md_bg_color=(1, 1, 1, 0.85), size_hint=(1, 1))
        layout_tumpuk.add_widget(lapisan_kaca)

        ui_layout = MDBoxLayout(orientation='vertical', padding=40, spacing=15)
        ui_layout.add_widget(MDLabel(text="Search", font_style="H3", bold=True, size_hint_y=None, height=80))
        
        self.input_lagu = MDTextField(hint_text="Cari Artis atau Lagu...", mode="round", size_hint_x=1)
        ui_layout.add_widget(self.input_lagu)
        
        btn_cari = MDFillRoundFlatButton(text="Cari", pos_hint={"center_x": 0.5}, size_hint_x=0.5)
        btn_cari.bind(on_press=self.cari_lagu)
        ui_layout.add_widget(btn_cari)
        
        self.label_hasil = MDLabel(text="", halign='center', size_hint_y=None, height=60, bold=True)
        ui_layout.add_widget(self.label_hasil)
        
        self.cover_album = AsyncImage(source='', size_hint_y=None, height=200)
        ui_layout.add_widget(self.cover_album)

        self.btn_play = MDFillRoundFlatButton(text="Play Lagu", pos_hint={"center_x": 0.5}, size_hint_x=0.5, disabled=True)
        self.btn_play.bind(on_press=self.putar_lagu)
        ui_layout.add_widget(self.btn_play)

        layout_tumpuk.add_widget(ui_layout)
        tab_search.add_widget(layout_tumpuk)

        # --- TAB LIBRARY ---
        tab_library = MDBottomNavigationItem(name='library', text='Library', icon='library-music')
        layout_lib = MDBoxLayout(orientation='vertical', padding=20)
        layout_lib.add_widget(MDLabel(text="Koleksi Lu", font_style="H4", bold=True, size_hint_y=None, height=50))
        
        self.list_history = MDList()
        scroll_lib = MDScrollView()
        scroll_lib.add_widget(self.list_history)
        layout_lib.add_widget(scroll_lib)
        tab_library.add_widget(layout_lib)

        nav_bawah.add_widget(tab_home)
        nav_bawah.add_widget(tab_search)
        nav_bawah.add_widget(tab_library)
        layar_utama.add_widget(nav_bawah)

        return layar_utama

    def cari_lagu(self, instance):
        judul = self.input_lagu.text
        if judul:
            self.label_hasil.text = "Mencari ke YouTube..."
            self.btn_play.disabled = True
            threading.Thread(target=self.proses_cari, args=(judul,), daemon=True).start()

    def proses_cari(self, judul):
        try:
            hasil = self.yt.search(judul, filter="songs")
            if hasil:
                Clock.schedule_once(lambda dt: self.update_ui_pencarian(hasil[0]), 0)
            else:
                Clock.schedule_once(lambda dt: self.tampil_error("Gak ketemu!"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.tampil_error("Koneksi Error"), 0)

    def update_ui_pencarian(self, lagu):
        self.id_lagu_sekarang = lagu['videoId']
        self.label_hasil.text = f"{lagu['title']}\n{lagu['artists'][0]['name']}"
        url_gambar = lagu['thumbnails'][-1]['url']
        self.cover_album.source = url_gambar
        self.bg_image.source = url_gambar 
        
        item_baru = TwoLineAvatarListItem(text=lagu['title'], secondary_text=lagu['artists'][0]['name'])
        item_baru.add_widget(IconLeftWidget(icon="history"))
        self.list_history.add_widget(item_baru)

        self.btn_play.disabled = False
        self.btn_play.text = "Play Lagu"

    def tampil_error(self, pesan):
        self.label_hasil.text = pesan

    def putar_lagu(self, instance):
        if self.id_lagu_sekarang:
            self.btn_play.text = "Loading Audio..."
            self.btn_play.disabled = True
            threading.Thread(target=self.proses_audio, daemon=True).start()

    def proses_audio(self):
        try:
            ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                url = f"https://www.youtube.com/watch?v={self.id_lagu_sekarang}"
                info = ydl.extract_info(url, download=False)
                url_audio = info['url']

            if self.player_suara:
                self.player_suara.stop()

            self.player_suara = SoundLoader.load(url_audio)
            if self.player_suara:
                self.player_suara.play()
                Clock.schedule_once(lambda dt: self.update_status_play("Playing 🎵", False), 0)
            else:
                Clock.schedule_once(lambda dt: self.update_status_play("Gagal Load Audio", False), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_status_play("Error Play", False), 0)

    def update_status_play(self, pesan, status_disabled):
        self.btn_play.text = pesan
        self.btn_play.disabled = status_disabled

if __name__ == '__main__':
    MusicApp().run()
      
