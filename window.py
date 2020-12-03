import tkinter as tk
import tkinter.filedialog, tkinter.scrolledtext, tkinter.messagebox, tkcolorpicker
from PIL import ImageTk, Image
import os, sys
from functools import partial
import webbrowser
import scripts, files, lp_colors, lp_events
from utils import launchpad_connector as lpcon
BUTTON_SIZE = 40
HS_SIZE = 200
V_WIDTH = 50
STAT_ACTIVE_COLOR = "#080"
STAT_INACTIVE_COLOR = "#444"
SELECT_COLOR = "#f00"
DEFAULT_COLOR = [0, 0, 255]
MK1_DEFAULT_COLOR = [0, 255, 0]
INDICATOR_BPM = 480
BUTTON_FONT = ("helvetica", 11, "bold")
PATH = None
PROG_PATH = None
USER_PATH = None
VERSION = None
PLATFORM = None
MAIN_ICON = None
launchpad = None
root = None
app = None
root_destroyed = None
restart = False
lp_object = None

DEFAULT_LOAD_FILE = None

load_layout_filetypes = [('LPHK layout files', [files.LAYOUT_EXT, files.LEGACY_LAYOUT_EXT])]
load_script_filetypes = [('LPHK script files', [files.SCRIPT_EXT, files.LEGACY_SCRIPT_EXT])]
save_layout_filetypes = [('LPHK layout files', [files.LAYOUT_EXT])]
save_script_filetypes = [('LPHK script files', [files.SCRIPT_EXT])]
lp_connected = False
lp_mode = None
colors_to_set = [[DEFAULT_COLOR for y in range(9)] for x in range(9)]


def init(lp_object_in, launchpad_in, path_in, prog_path_in, user_path_in, version_in, platform_in):
def init(lp_object_in, launchpad_in, path_in, prog_path_in, user_path_in, version_in, platform_in, default_load_file):
    global lp_object
    global launchpad
    global PATH
    global PROG_PATH
    global USER_PATH
    global VERSION
    global PLATFORM
    global MAIN_ICON
    global DEFAULT_LOAD_FILE
    lp_object = lp_object_in
    launchpad = launchpad_in
    PATH = path_in
    PROG_PATH = prog_path_in
    USER_PATH = user_path_in
    VERSION = version_in
    PLATFORM = platform_in
    DEFAULT_LOAD_FILE = default_load_file

    if PLATFORM == "windows":
        MAIN_ICON = os.path.join(PATH, "resources", "LPHK.ico")
    else:
        MAIN_ICON = os.path.join(PATH, "resources", "LPHK.gif")
    make()
class Main_Window(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.init_window()
        
        self.about_image = ImageTk.PhotoImage(Image.open(PATH + "/resources/LPHK-banner.png"))
        self.info_image = ImageTk.PhotoImage(Image.open(PATH + "/resources/info.png"))
        self.warning_image = ImageTk.PhotoImage(Image.open(PATH + "/resources/warning.png"))
        self.error_image = ImageTk.PhotoImage(Image.open(PATH + "/resources/error.png"))
        self.alert_image = ImageTk.PhotoImage(Image.open(PATH + "/resources/alert.png"))
        self.scare_image = ImageTk.PhotoImage(Image.open(PATH + "/resources/scare.png"))
        self.grid_drawn = False
        self.grid_rects = [[None for y in range(9)] for x in range(9)]
        self.button_mode = "edit"
        self.last_clicked = None
        self.outline_box = None

    def init_window(self):
        global root
        

        self.master.title("LPHK - Novation Launchpad Macro Scripting System")
        self.pack(fill="both", expand=1)

        self.m = tk.Menu(self.master)
        self.master.config(menu=self.m)
        self.m_Launchpad = tk.Menu(self.m, tearoff=False)
        self.m_Launchpad.add_command(label="Redetect (Restart)", command=self.redetect_lp)
        self.m.add_cascade(label="Launchpad", menu=self.m_Launchpad)
        self.m_Layout = tk.Menu(self.m, tearoff=False)
        self.m_Layout.add_command(label="New Layout", command=self.unbind_lp)
        self.m_Layout.add_command(label="Load Layout", command=self.load_layout)
        self.m_Layout.add_command(label="Save Layout", command=self.save_layout)
        self.m_Layout.add_command(label="Save Layout As...", command=self.save_layout_as)
        self.m.add_cascade(label="Layout", menu=self.m_Layout)
        self.disable_menu("Layout")
        
        self.m_Help = tk.Menu(self.m, tearoff=False)
        open_readme = lambda: webbrowser.open("https://github.com/nimaid/LPHK#lphk-launchpad-hotkey")
        self.m_Help.add_command(label="Open README...", command=open_readme)
        open_scripting = lambda: webbrowser.open("https://github.com/nimaid/LPHK#what-is-lphkscript-table-of-contents")
        self.m_Help.add_command(label="Scripting Help...", command=open_scripting)
        open_user_folder = lambda: files.open_file_folder(USER_PATH)
        self.m_Help.add_command(label="User Folder...", command=open_user_folder)
        open_prog_folder = lambda: files.open_file_folder(PROG_PATH)
        self.m_Help.add_command(label="Program Folder...", command=open_prog_folder)
        display_info = lambda: self.popup(self, "About LPHK", self.about_image, "A Novation Launchpad Macro Scripting System\nMade by Ella Jameson (nimaid)\n\nVersion: " + VERSION + "\nFile format version: " + files.FILE_VERSION, "Done")
        self.m_Help.add_command(label="About LPHK", command=display_info)
        self.m.add_cascade(label="Help", menu=self.m_Help)
        c_gap = int(BUTTON_SIZE // 4)
        c_size = (BUTTON_SIZE * 9) + (c_gap * 9)
        self.c = tk.Canvas(self, width=c_size, height=c_size)
        self.c.bind("<Button-1>", self.click)
        self.c.grid(row=0, column=0, padx=round(c_gap/2), pady=round(c_gap/2))
        self.stat = tk.Label(self, text="No Launchpad Connected", bg=STAT_INACTIVE_COLOR, fg="#fff")
        self.stat.grid(row=1, column=0, sticky=tk.EW)
        self.stat.config(font=("Courier", BUTTON_SIZE // 3, "bold"))




    def raise_above_all(self):
        self.master.attributes('-topmost', 1)
        self.master.attributes('-topmost', 0)
    
    def enable_menu(self, name):
        self.m.entryconfig(name, state="normal")
    def disable_menu(self, name):
        self.m.entryconfig(name, state="disabled")
    
    def connect_dummy(self):
        # WIP
        global lp_connected
        global lp_mode
        global lp_object
        
        lp_connected = True
        lp_mode = "Dummy"
        self.draw_canvas()
        self.enable_menu("Layout")
    def connect_lp(self):
        global lp_connected
        global lp_mode
        global lp_object
        global DEFAULT_LOAD_FILE

        lp = lpcon.get_launchpad()

        if lp is -1:
            self.popup(self, "Connect to Unsupported Device", self.error_image,
                       """The device you are attempting to use is not currently supported by LPHK,
                       and there are no plans to add support for it.
                       Please voice your feature requests on the Discord or on GitHub.""",
                       "OK")
        if lp is None:
            self.popup_choice(self, "No Launchpad Detected...", self.error_image,
                              """Could not detect any connected Launchpads!
                              Disconnect and reconnect your USB cable,
                              then click 'Redetect Now'.""",
                              [["Ignore", None], ["Redetect Now", self.redetect_lp]]
                              )
            return
        if lpcon.connect(lp):
            lp_connected = True
            lp_object = lp
            lp_mode = lpcon.get_mode(lp)
            if lp_mode is "Pro":
                self.popup(self, "Connect to Launchpad Pro", self.error_image,
                           """This is a BETA feature! The Pro is not fully supported yet,as the bottom and left rows are not mappable currently.
                           I (nimaid) do not have a Launchpad Pro to test with, so let me know if this does or does not work on the Discord! (https://discord.gg/mDCzB8X)
                           You must first put your Launchpad Pro in Live (Session) mode. To do this, press and holde the 'Setup' key, press the green pad in the
                           upper left corner, then release the 'Setup' key. Please only continue once this step is completed.""",
                           "I am in Live mode.")
            lp_object.ButtonFlush()
            # special case?
            if lp_mode is not "Mk1":
                lp_object.LedCtrlBpm(INDICATOR_BPM)
            lp_events.start(lp_object)
            self.draw_canvas()
            self.enable_menu("Layout")
            self.stat["text"] = f"Connected to {lpcon.get_display_name(lp)}"
            self.stat["bg"] = STAT_ACTIVE_COLOR

        if lp_connected is True and DEFAULT_LOAD_FILE is not None:
            if os.path.isabs(DEFAULT_LOAD_FILE):
                file_name = DEFAULT_LOAD_FILE
            else:
                file_name = os.path.join(files.LAYOUT_PATH, DEFAULT_LOAD_FILE)

            if os.path.exists(file_name):
                files.load_layout_to_lp(file_name)
            else:
                self.popup(self, "Unable to load layout", self.error_image,
                           "The system cannot find the file specified in the command line argument.", "Okay")


    def disconnect_lp(self):
        global lp_connected
        try:
            scripts.unbind_all()
            lp_events.timer.cancel()
            lpcon.disconnect(lp_object)
        except:
            self.redetect_lp()
        lp_connected = False
        self.clear_canvas()
        self.disable_menu("Layout")
        self.stat["text"] = "No Launchpad Connected"
        self.stat["bg"] = STAT_INACTIVE_COLOR
    def redetect_lp(self):
        global restart
        restart = True
        close()
    def unbind_lp(self, prompt_save=True):
