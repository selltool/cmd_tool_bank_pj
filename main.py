#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cmd
from controller.adb_controller import ADBController
from controller.ffmpeg_controller import FFmpegController

class CmdShell(cmd.Cmd):
    # intro = "Chào mừng bạn đến với shell Python. Gõ help hoặc ? để xem lệnh.\n"
    intro = "Welcome to shell of ST. \n Type help or ? to see the commands."
    prompt = "(CmdShell) "
    
    def __init__(self):
        super().__init__()
        self.adb_controller = ADBController()
        self.ffmpeg_controller = FFmpegController()
        
    def do_hello(self, arg):
        """
        Say hello: hello <name>
        """
        print(f"Hello {arg}!")

    def do_exit(self, arg):
        """
        Exit shell
        """
        print("Goodbye!")
        return True
    
    def emptyline(self):
        pass

    def do_nab(self, arg):
        """
        Say NamABank: nab <serial> or nab
        """
        arg = arg.strip()
        if not arg:
            print("Please enter a serial number.")
            return
        return self.adb_controller.handle_nab(arg)
        
    def do_cvvd(self, arg):
        """
        Convert video: abc
        """
        return self.ffmpeg_controller.handle_convert_video(arg)
    
    

if __name__ == '__main__':
    CmdShell().cmdloop()


# Command build with pyinstaller
# pyinstaller -F main.py --onefile -n st_shell -y -i data/icon.ico --clean