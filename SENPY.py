from gevent import monkey as curious_george

curious_george.patch_all(thread=False, select=False)
import asyncio
import promptlib
from kivy.metrics import dp

import os
import time
from kivy.lang import Builder
from kivy.clock import Clock
from functools import partial
import re as reg
import requests as re
import grequests as gre
from bs4 import BeautifulSoup as bs
from pySmartDL import SmartDL
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.button import MDFlatButton
from time import sleep
import threading
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.textfield import MDTextField
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty, StringProperty
from kivymd.uix.spinner import MDSpinner
from pySmartDL import SmartDL
from kivymd.uix.progressloader import MDProgressLoader
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dropdownitem import MDDropDownItem
from kivy.animation import Animation
from kivymd.toast import toast

# colors list
colors = ["Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue", "LightBlue", "Cyan", "Teal", "Green", "LightGreen",
          "Lime", "Yellow", "Amber", "Orange", "DeepOrange", "Brown", "Gray", "BlueGray"
          ]
# index for incrementating main loop
index = 0


# The entirety of senpy and all its code
class MainApp(MDApp):
    # init function might add variables in it soon
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allowed = True
        self.remove = False
        self.sessioning = True
        self.exit = False
        self.Anime = []
        self.icon_num = 0
        self.is_downloading = False
        self.episode_names = []
        self.toasted_num = 1
        self.start_progress = False
        self.drop_downitems = []
        self.drop_downnames = []
        self.menud = False

    # caller for where the menu should be opened
    def callback(self):
        if self.menud:
            self.menu.open()
        else:
            pass

    # caller for what should happen when i press something in menu
    def menu_c(self, text_item):
        print("menu")
        self.menu.dismiss()
        print(text_item)

    # this func is called when kivy(the app) is started
    def on_start(self):
        self.kv.remove_widget(self.kv.ids.session_btn)
        self.start_progress = True

        # some widgets are already created using kv file so i need to remove them when the app starts
        self.kv.remove_widget(self.kv.ids.down_btn)
        self.kv.remove_widget(self.kv.ids.prog_bar)
        self.kv.remove_widget(self.kv.ids.spinner)
        self.call_opacity()
        # self.kv.remove_widget(self.spinner)

    # changes the opacity of the image over 5 secs
    def image_opacity(self, *args):
        change = True
        changer = Animation()
        if self.kv.ids.image.opacity == 0.1 or 0.2 and change:
            changer = Animation(opacity=0.5,
                                duration=5)

        if self.kv.ids.image.opacity <= 0.5:
            change = False
            changer += Animation(opacity=0.2,
                                 duration=5)
        changer.start(self.kv.ids.image)

    # call the function to change image opacity
    def call_opacity(self):
        Clock.schedule_interval(self.image_opacity, 10)

    # function to change numbers in the textfield
    def numerics(self, *args):
        icon_num = str(self.icon_num)
        self.md_field.icon_right = "numeric-" + icon_num + "-box-multiple-outline"
        self.limit_field.icon_right = "numeric-" + icon_num + "-box-multiple-outline"
        self.icon_num += 1
        if self.icon_num == 10:
            self.icon_num = 0

        if self.kv.ids.down_btn.icon == "download":
            self.kv.ids.down_btn.icon = "download-multiple"
        else:
            self.kv.ids.down_btn.icon = "download"

        # numeric-1-box-outline
        # numeric-1-box-multiple-outline

    # the numbers in the textfields are represented by icons so this function calls the numerics function
    def call_icons(self):
        self.icon_running = Clock.schedule_interval(self.numerics, 1)

    # function to change colors in the app
    def theme(self):
        # remove this global variable soon

        global index
        index += 1
        for i in colors:
            self.theme_cls.primary_palette = colors[index]

            if index == 18:
                index = 0

    # removes the spinner that's called when you press enter
    def remove_spin(self):
        self.kv.remove_widget(self.kv.ids.spinner)

    # build function allows you to add attrs to you screen(app) say button
    def build(self):
        self.theme_cls.primary_dark_hue = '400'
        self.theme_cls.theme_style = "Light"
        self.kv = Builder.load_file('demo.kv')

        self.screen = Screen()
        # im creating widgets in the kv file then calling them in the build function to be displayed
        # on the screen

        self.screen.add_widget(self.kv)

        return self.screen

    def dialogue(self):
        dia_text = "Senpy has found the anime, Please Click on the text field and select one of the options available. GILF                                                                                   By: IwasBachus"
        dialog = MDDialog(text=dia_text)
        dialog.open()

    # newer function that get multiple anime options that are available or related to your search
    def searcher(self):
        if self.kv.ids.field.text == "":
            pass
        else:
            anime = self.kv.ids.field.text
            self.kv.ids.field.text = ""
            anime = anime.lower()
            anime = anime.replace(" ", "%20")
            anime = anime.replace("(", "")
            anime = anime.replace(")", "")
            link = "https://www1.gogoanime.ai//search.html?keyword="
            url = link + anime
            session = re.get(url)
            soup = bs(session.text, 'html.parser')
            eps = soup.find("ul", {"class": "items"})

            ep = eps.find_all('li')
            if ep is None:
                pass
            else:
                self.kv.remove_widget(self.kv.ids.btn)
                self.kv.add_widget(self.kv.ids.session_btn)
            for li in ep:
                dname = li.div.a["title"]
                link = "https://www1.gogoanime.ai" + li.div.a["href"]
                self.drop_downitems.append(link)
                self.drop_downnames.append(dname)
            menu_items = [
                {
                    "text": i,
                    "height": dp(56),
                    "on_release": lambda x=f"Item {i}": self.set_item,
                } for i in self.drop_downnames
            ]
            self.menu = MDDropdownMenu(
                items=menu_items,
                width_mult=9,
                caller=self.kv.ids.field,
                position="bottom",
                callback=self.set_item
            )
            self.menud = True
            self.dialogue()

    def set_item(self, instance):

        self.kv.ids.field.text = instance.text
        self.kv.ids.field.hint_text = ""
        dex = self.drop_downnames.index(instance.text)
        self.full_link = self.drop_downitems[dex]
        self.menu.dismiss()

    # function thats called when the anime you typed is correct and found
    def right(self):

        self.downloadable = True

        episode = str(self.end_episodes)
        episodes = "Anime has ", episode, " Episodes"
        episodes = str(episodes)
        btn = self.kv.ids.btn
        field = self.kv.ids.field
        field.pos_hint = {"center_x": 0.5, "center_y": 0.9}
        # creates text field with python instead of kv bcos of reasons
        self.md_field = MDTextField()
        # for some reason i cant add these params in the MDTextField() param i need to add it to the variable
        # such a pain
        self.md_field.required = True
        self.md_field.icon_right_color = (0.62352941176, 0.58039215686, 1, 1)
        self.md_field.helper_text = episodes
        self.md_field.hint_text = "Enter First Episode as Digits"
        self.md_field.helper_text_mode = "on_focus"
        self.md_field.pos_hint = {'center_x': 0.5, 'center_y': 0.75}
        self.md_field.size_hint_x = None
        self.md_field.width = 300

        self.limit_field = MDTextField()
        self.limit_field.required = True
        self.limit_field.icon_right_color = (0.62352941176, 0.58039215686, 1, 1)
        self.limit_field.helper_text = episodes
        self.limit_field.hint_text = "Enter Number of Episodes as Digits"
        self.limit_field.helper_text_mode = "on_focus"
        self.limit_field.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
        self.limit_field.size_hint_x = None
        self.limit_field.width = 300
        self.kv.remove_widget(btn)
        self.kv.add_widget(self.md_field)
        self.kv.add_widget(self.limit_field)
        self.call_icons()

    # function to return episode name to be used in a chip that shows up after the anime is found
    def return_episode(self):
        return self.ep_name

    # might be used as a new downloader

    # fucntion thats used to get the link of the anime with just a name being presented
    def session(self, *args):
        self.t = True
        self.episodes = []
        # self.inlink = self.kv.ids.field.text
        # self.anime = self.inlink.lower()
        # self.anime = self.anime.replace(" ", "-")
        # self.anime = self.anime.replace("(", "")
        # self.anime = self.anime.replace(")", "")
        # self.beg_url = "https://gogoanime.ai/category/"
        # self.end_url = self.anime

        self.url = self.full_link
        self.first_ep = self.url.replace("/category", "").__add__("-episode-").__add__("1")
        # self.session = re.get(self.url)
        self.session = re.get(self.url)
        if self.exit:
            xx = nfuh

    # after some giga braining i found a ssolution to run web searches without freezing my application throughout the
    # process
    def thread_session(self):
        if self.kv.ids.field.text == "":
            pass
        else:
            self.a = threading.Thread(name='self.session', target=self.session)
            self.a.start()

    # function called if the site(anime) you entered is found
    def session_exists(self, *args):
        # if the site exists then go forward
        try:
            if self.session.status_code == 200:
                self.kv.ids.field.icon_right = "movie-filter-outline"
                self.kv.ids.field.mode = "rectangle"
                self.kv.add_widget(self.kv.ids.down_btn)
                self.soup = bs(self.session.content, 'html.parser')
                self.ep_contents = self.soup.find("ul", {"id": "episode_page"})
                self.ep_limits = self.ep_contents.findAll("li")
                self.end_limit = self.ep_limits[-1::]
                self.end_limit = str(self.end_limit)
                self.end_limit = self.end_limit[24:40:]
                self.end_limit = int(reg.sub("[^0-9]", "", self.end_limit))
                self.end_episodes = self.end_limit
                self.remove_spin()
                self.right()

                dia_text = "Senpy has found the Anime in Question", "                                                  ", "   Found:", self.end_limit, "Downloadable Episodes of the Anime"

                dia_text = str(dia_text)
                dia_text = dia_text.replace("(", "")
                dia_text = dia_text.replace(",", "")
                dia_text = dia_text.replace("'", "")
                dia_text = dia_text.replace(")", "")
                self.dia_text = dia_text
                self.sessioning = False
                self.qual = "HDP"
                self.steam_qual = "Download StreamSB"
                self.ver_qual = "Download\n            (" + self.qual + " - mp4)"
                dialog = MDDialog(text=self.dia_text)
                dialog.open()

                self.ep_num = 0
                self.unschedule()
            else:
                self.exit = True
                self.session_notexist()
                # self.b = threading.Thread(name='self.session', target=self.session)
        except:
            pass

    # i dont use this function bcos how threads work but imma leave it here might return
    def session_notexist(self):
        self.kv.add_widget(self.kv.ids.btn)
        self.kv.remove_widget(self.kv.ids.spinner)
        dia_text = "You probally typed the name in wrong, if problem persists check google for the animes official " \
                   "name(japanese or not)".capitalize()
        self.dia_text = dia_text
        self.qual = "HDP"
        self.steam_qual = "Download StreamSB"
        self.ver_qual = "Download\n            (" + self.qual + " - mp4)"
        dialog = MDDialog(text=self.dia_text)
        dialog.open()
        self.unschedule()
        self.ep_num = 0

    # this session removes the enter buttion and adds in new text fields to do new thing(download)
    def call_sessions(self):
        try:
            if self.kv.ids.field.text == "":
                pass
            else:
                self.kv.remove_widget(self.kv.ids.btn)
                self.kv.remove_widget(self.kv.ids.session_btn)
        except:
            pass
        if self.kv.ids.field.text == "":
            pass
        else:
            Clock.schedule_interval(self.session_exists, 0.2)

    # the self.a.exit doesnt work bcos threads are annoying and dont like being stopped
    def unschedule(self):
        self.a.exit()
        self.remove = True
        Clock.unschedule(self.session_exists)

    # functions are in a mess tbh, yes i made a function to remove something i havent created yet :P
    def spinner(self):
        if self.kv.ids.field.text == "":
            pass
        else:
            self.kv.add_widget(self.kv.ids.spinner)
            self.kv.ids.spinner.active = True

    # the bulk of SENPY the place where i can look back and think well that was a 🤬 mess
    def main_download_area(self):
        if self.limit_field.text == "" or self.md_field.text == "":
            pass
        else:
            self.file = self.file_manager()
            self.kv.ids.toolbar.title = "Click To see Download"
            self.num = self.md_field.text
            self.num = int(self.num)
            self.ep = self.limit_field.text
            self.ep = int(self.ep)

            # Loop to find downloads on the site
            for i in range(self.ep):
                self.get_end = -5
                # loop to return link without a number at the end
                for i in range(10):
                    try:
                        if self.first_ep[self.get_end::].__contains__("-") is False:
                            self.num_end = int(self.first_ep[self.get_end::])
                            self.end_indx = self.get_end
                            break
                    except:
                        pass
                    self.get_end += 1

                self.first_ep = self.first_ep[:self.end_indx:]
                self.first_ep = self.first_ep.__add__(str(self.num))
                self.episodes.append(self.first_ep)
                self.num += 1

            # uses the links in a psuedo async way for speed ,tbh i dont think it really increases spped but ive been using it since verssion 0.1
            self.session = (gre.get(episode) for episode in self.episodes)
            self.responses = gre.map(self.session)
            # loop to get download options, some stuff needed change so past this point the code gets redundant and
            # unnecessary but in earlier version it was necessary i just dont wanna let go of this code( might need it )
            for response in self.responses:
                self.html = response.content
                self.soup = bs(self.html, 'html.parser')
                self.page = self.soup.find("li", {"class": "dowloads"})
                self.content = self.page.find("a")
                self.new_link = self.content["href"]
                self.new_htmlink = re.get(self.new_link)
                self.new_html = self.new_htmlink.content
                self.new_soup = bs(self.new_html, 'html.parser')
                self.find = self.new_soup.findAll("div", {"class": "dowload"})
                self.Texts = []
                self.Hrefs = []
                self.tex = 0
                self.index = 0

                # loop to gather all the info about the downloads mainly the quality and link
                for i in self.find:
                    self.text = str(self.find[self.tex].text)

                    self.Texts.append(self.text)
                    self.href = str(self.find[self.tex].a["href"])
                    self.Hrefs.append(self.href)
                    self.tex += 1
                # loop to make specifications to print links according to quality
                for i in self.find:
                    # to check if the quality is in present used in older version e.g ver_qual might be 480p
                    if self.ver_qual in self.Texts:
                        # to get the links only if the quality is there
                        if self.Texts[self.index].__contains__(self.qual) is True:
                            # print("")
                            # anime = anime.replace("-", " ")

                            # print("\n",anime, " Episode", ep_num, " in ", qual)
                            self.dw_link = self.Hrefs[self.index]
                            # print("Episodes downloading: ","\n")
                            # Dw_manager(dw_link)
                            self.Ep_name = self.soup.find("div", {"class": "title_name"}).h2.text
                            self.episode_names.append(self.Ep_name)

                            url = self.dw_link
                            self.Anime.append(url)
                            break
                    # newer version uses the site stream SB they cucked me
                    elif self.steam_qual in self.Texts:
                        if self.Texts[self.index].__contains__("StreamSB") is True:

                            # Extreme list comprehensions ahead approach with caution

                            xurl = self.Hrefs[self.index]
                            xlink = re.get(xurl)
                            xsoup = bs(xlink.text, 'html.parser')
                            xtable = xsoup.find("table", {"width": "60%"})
                            xtext = xtable.findAll("a")
                            xtext = str(xtext[-1::])
                            xtext = xtext.split("onclick=", 1)[1]
                            xtext = xtext.replace("download_video(", "")
                            xtext = xtext.replace(")", "")
                            xtext = xtext.replace("'", "")
                            xtext = xtext.replace('"', "")
                            xtext = xtext.split(",")
                            full_link = "https://streamsb.net/dl?op=download_orig&id=", xtext[0], "&mode=", xtext[
                                1], "&hash=", \
                                        xtext[2]
                            full_link = str(full_link)
                            full_link = full_link.replace(",", "")
                            full_link = full_link.replace("'", "")
                            full_link = full_link.replace(" ", "")
                            full_link = full_link.replace("(", "")
                            full_link = full_link.replace(")", "")

                            if full_link.__contains__(">Normalquality</a>]"):
                                full_link = full_link.replace(">Normalquality</a>]", "")
                            elif full_link.__contains__(">Highquality</a>]"):
                                full_link = full_link.replace(">Highquality</a>]", "")

                            full_re = re.get(full_link)
                            pi_soup = bs(full_re.text, 'html.parser')
                            xspan = pi_soup.find("span",
                                                 {"style": "background:#f9f9f9;border:1px dotted #bbb;padding:7px;"})
                            apsolute_link = xspan.a["href"]
                            self.Ep_name = self.soup.find("div", {"class": "title_name"}).h2.text
                            self.episode_names.append(self.Ep_name)

                            url = apsolute_link
                            self.Anime.append(url)
                            break
                    self.index += 1
                self.ep_num += 1
            self.Thread_download()
            # also it makes SENPY stretch 500 lines so 😋😋

    # calls my MAIN function
    def call_main_download_area(self):
        # self.kv.add_widget(self.kv.ids.Episode_name)
        self.kv.ids.Episode_name.label = self.ep_name
        Clock.schedule_once(self.main_download_area)

    # useless function might remove when im finished
    def download_screen(self):
        self.kv.remove_widget(self.md_field)
        self.kv.remove_widget(self.limit_field)
        self.kv.remove_widget(self.kv.ids.field)
        self.kv.remove_widget(self.kv.ids.down_btn)

    # my sets the downlload popup back
    def set_chevron_back_screen(self):
        self.kv.ids.toolbar.right_action_items = []

    # another function that might replace my downloader, news flash it has replaced it
    # i had to implement my own async stuff for the downloader to run and update in SENPY but
    # the progressbar was acting up so nvm
    def download_progress_hide(self, instance_progress, value):
        '''Hides progress progress.'''

        self.kv.ids.toolbar.left_action_items = [['menu',
                                                  lambda x: self.download_progress_show(instance_progress)]]

    def download_progress_show(self, instance_progress):
        self.set_chevron_back_screen()
        instance_progress.open()
        instance_progress.animation_progress_from_fade()

    # main download function uses kivymd's MDProgressloader which
    # has like no documentation and i think it was removed so imma make this into an app before updating
    # to the new kivymd :(
    def downloader(self):

        ind = 0
        nex = 0
        size = len(self.Anime)
        length = size + ind
        name = "one"
        while True:

            if self.is_downloading is False:
                file_dir = str(self.file + self.episode_names[nex] + ".mp4")
                self.progress = MDProgressLoader(
                    url_on_image=self.Anime[nex],
                    path_to_file=file_dir,
                    download_complete=self.download_complete,
                    download_hide=self.download_progress_hide,

                )
                self.progress.start(self.screen)

                if self.progress.download_flag:
                    self.is_downloading = True
            if self.progress.download_flag is False:
                self.is_downloading = False
                name = "two"
                nex += 1
            if self.on_stop():
                break

            sleep(1)

    # useless function i think
    def Thread_download(self):
        a = threading.Thread(target=self.downloader)
        a.start()

    # shows you that your download is completed
    # or if ur downloading multiple it shows you which one is finished
    def download_complete(self):
        self.set_chevron_back_screen()

        if self.toasted_num == 1:
            toast(str(self.toasted_num) + self.kv.ids.field.text + " Episode downloaded")
        else:
            toast(str(self.toasted_num) + self.kv.ids.field.text + " Episodes downloaded")
        self.toasted_num += 1

    # where tf did this come from
    # kinda scared to removed it ngl
    def none(self):
        pass

    def downloading(self):
        # ohh here it is, wait wtf am i dumb, wait what, :O is this giga brain woahhh
        self.kv.remove_widget(self.kv.ids.down_btn)

    # function to open a prompt which allows you to select folders
    def file_manager(self, *args):
        if self.start_progress:
            prompter = promptlib.Files()
            dir = prompter.dir()
            dir = str(dir)
            dir = dir.replace("\\", "/").__add__("/")
            return dir
        else:
            pass


MainApp().run()

# my old downlaod function may you rest in peace with the hours i spent on making you
'''
    def update_progress(self, *args):
        self.kv.ids.prog_bar.value = 0
        self.kv.ids.prog_bar.value += 5.55555555556 * self.dw_loader.get_progress_bar().count("#")
        print(self.kv.ids.prog_bar.value)
        print(self.dw_loader.get_speed(human=True))  # download speed with kilobytes
        # print(d_load.get_status()) # downloading or not
        print(self.dw_loader.get_eta(human=True))  # how long in secs itll take to finsih
        # print(d_load.get_dl_time(human=True))  # idk but it says -1.0 but i think its how much time has gone bby
        print(self.dw_loader.filesize)  # file size
        print(self.dw_loader.get_dl_size(human=True))  # how muchh is downloaded so far
        if self.dw_loader.isFinished() == True:
            self.kv.ids.prog_bar.value = 100

    def call_progress(self):
        pass
        #Clock.schedule_interval(self.update_progress, 1)
    # uses the above function as well as links provided by my epic code to download to anime/episodes or just 1
    def downloader(self):
        self.dw_loader = SmartDL(self.url, self.file + self.ep_name, ".mp4", timeout=13)
        self.dw_loader.start(blocking=False)
        if self.dw_loader.isFinished() is False:
            # print(d_load.get_speed(human=True)) # download speed with kilobytes
            # print(d_load.get_status()) # downloading or not
            # print(d_load.get_eta(human=True))  # how long in secs itll take to finsih
            # print(d_load.get_dl_time(human=True))  # idk but it says -1.0 but i think its how much time has gone bby
            # print(d_load.filesize)  # file size
            # print(d_load.get_dl_size(human=True))  # how muchh is downloaded so far
            # print("buttom")
            time.sleep(self.dw_loader.get_eta())
'''
