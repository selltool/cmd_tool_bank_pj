import os, json, time, traceback
from helpers.custom_ffmpeg import CustomFFmpeg
from helpers.ter import clear_screen

class FFmpegController:
    def __init__(self):
        self.ffmpeg = CustomFFmpeg()
        
    
    def handle_convert_video(self, arg):
        """
        Convert video: cvvd <input_file>
        """
        try:
            if not self.ffmpeg.check_ffmpeg():
                print("FFmpeg and ffprobe not found, please install them.")
                return
            arg = arg.strip()
            if not arg:
                clear_screen()
                print("--------------------------------")
                print("Please enter the link of the file (Ctrl + Shift + C for copy full path file): ")
                print("--------------------------------")
                print("Enter 'exit' to exit.")
                link_file = None
                while True:
                    link_file = input("Link file: ")
                    if link_file == 'exit':
                        return
                    if not link_file:
                        clear_screen()
                        print("--------------------------------")
                        print("Please enter the link of the file (Ctrl + Shift + C for copy full path file): ")
                        print("--------------------------------")
                        print("Enter 'exit' to exit.")
                        continue
                    else:
                        break
            else:
                link_file = arg
            if '"' in link_file:
                link_file = link_file.replace('"', '')
            if "'" in link_file:
                link_file = link_file.replace("'", "")
            if "\\" not in link_file:
                print(f"File '{link_file}' is not an absolute path. Converting to absolute path...")
                if "mp4" not in link_file:
                    link_file = link_file + ".mp4"
                link_file = os.path.join(os.getcwd(), link_file)
            if not os.path.exists(link_file):
                print(f"File {link_file} not found.")
                return
            info = self.ffmpeg.ffprobe_info(link_file)
            data = info.stdout
            if "streams" not in data:
                print("Key 'streams' not found, check file or ffmpeg and try again." )
                print(info.stderr)
                print("--------------------------------")
                print(info.returncode)
                print("--------------------------------")
                print(data)
                print("--------------------------------")
                return
            data = json.loads(data)
            streams = data['streams'][0]
            video_width = streams.get('width')
            video_height = streams.get('height')
            if video_width != 1200 or video_height != 1600:
                print("This video not support, contact developer to support this video.")
                print(f"Video width: {video_width}, Video height: {video_height}")
                return
            
            # Convert time to hms
            time_str = time.strftime("%H%M%S", time.localtime(int(time.time())))
            output_file = link_file.replace('.mp4', f'_{time_str}_converted.mp4')
            # output_file = link_file.replace('.mp4', f'_converted.mp4')
            output_file = output_file.replace(' ', '_')
            self.ffmpeg.convert_video(link_file, output_file)
            print("--------------------------------")
            print(f"Convert video success: {output_file}")
            print("--------------------------------")
            return
        except Exception as e:
            print(traceback.format_exc())
    
    