import subprocess
from typing import List

class CustomFFmpeg:
    def __init__(self):
        pass
        
    def run(self, cmd_list: List[str], timeout: int = 20, capture_output: bool = True, text: bool = True) -> subprocess.CompletedProcess:
        """
        Run system command and return CompletedProcess (stdout, stderr, returncode).
        """
        return subprocess.run(
            cmd_list,
            capture_output=capture_output,
            text=text,
            timeout=timeout,
        )
        # process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # stdout, stderr = process.communicate()
        # return subprocess.CompletedProcess(returncode=process.returncode, stdout=stdout, stderr=stderr)
    
    def ffprobe_info(self, link_file: str) -> subprocess.CompletedProcess:
        """
        Get information of the file: ffprobe -i <input_file>
        """
        command = [
            'ffprobe', 
            "-show_streams", "-show_format",
            "-print_format", "json",
            link_file
        ]
        return self.run(command, timeout=20)
    
    def convert_video(self, link_file: str, output_file: str) -> subprocess.CompletedProcess:
        """
        Convert video: abc
        """
        command = [
            'ffmpeg', '-y',
            '-i', link_file,
            '-vf', 'transpose=1',
            '-b:v', '20422k',
            '-color_range', 'pc',
            '-movflags', '+faststart',
            '-c:a', 'copy',
            output_file,
        ]
        self.run(command, timeout=120, capture_output=False)
    
    def check_ffmpeg(self) -> bool:
        """
        Check if ffmpeg and ffprobe are installed.
        """
        command = [
            'ffmpeg', '-version',
            'ffprobe', '-version',
        ]
        res = self.run(command, timeout=10)
        if res.returncode == 0:
            print("FFmpeg and ffprobe are installed.")
            return True
        else:
            print("FFmpeg and ffprobe are not installed.")
            return False