iimport sys, os, subprocess
from datetime import datetime
import argparse

print("\n!!!!!!!! DO NOT CLOSE THIS WINDOW WITHOUT SAVING !!!!!!!!\n")

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', action='store_true',
                    help='enable debug mode')
parser.add_argument('--load', '-l', default= None,
                    help='Load file for launchpad')

args = vars(parser.parse_args())

LOG_TITLE = "LPHK.log"

# Get platform information
@@ -90,18 +99,19 @@ def datetime_str():
lp = launchpad.Launchpad()

EXIT_ON_WINDOW_CLOSE = True

DEFAULT_LOAD_FILE = None

def init():
    global EXIT_ON_WINDOW_CLOSE
    if len(sys.argv) > 1:
        if ("--debug" in sys.argv) or ("-d" in sys.argv):
            EXIT_ON_WINDOW_CLOSE = False
            print("[LPHK] Debugging mode active! Will not shut down on window close.")
            print("[LPHK] Run shutdown() to manually close the program correctly.")
    global DEFAULT_LOAD_FILE

        else:
            print("[LPHK] Invalid argument: " + sys.argv[1] + ". Ignoring...")
    if args["debug"] is True:
        EXIT_ON_WINDOW_CLOSE = False
        print("[LPHK] Debugging mode active! Will not shut down on window close.")
        print("[LPHK] Run shutdown() to manually close the program correctly.")

    if args["load"] is not None:
        DEFAULT_LOAD_FILE = args["load"]

    files.init(USER_PATH)
    sound.init(USER_PATH)
def shutdown():
    if lp_events.timer != None:
        lp_events.timer.cancel()
    scripts.to_run = []
    for x in range(9):
        for y in range(9):
            if scripts.threads[x][y] != None:
                scripts.threads[x][y].kill.set()
    if window.lp_connected:
        scripts.unbind_all()
        lp_events.timer.cancel()
        launchpad_connector.disconnect(lp)
        window.lp_connected = False
    logger.stop()
    if window.restart:
        if IS_EXE:
            os.startfile(sys.argv[0])
        else:
            os.execv(sys.executable, ["\"" + sys.executable + "\""] + sys.argv)
    sys.exit("[LPHK] Shutting down...")

def main():
    init()
    window.init(lp, launchpad, PATH, PROG_PATH, USER_PATH, VERSION, PLATFORM)
    window.init(lp, launchpad, PATH, PROG_PATH, USER_PATH, VERSION, PLATFORM, DEFAULT_LOAD_FILE)
    if EXIT_ON_WINDOW_CLOSE:
        shutdown()

main()
