import subprocess
import shlex
import sys
from typing import List, Dict, Optional


class CustomADB:
    def __init__(self, sn: str = None):
        """
        :param sn: Serial number of the device
        """
        self.devices = []
        self.sn = sn

    def run(self, cmd_list: List[str], timeout: int = 20) -> subprocess.CompletedProcess:
        """
        Run system command and return CompletedProcess (stdout, stderr, returncode).
        """
        return subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def adb_cmd(self, args: List[str], serial: Optional[str] = None, timeout: int = 20) -> subprocess.CompletedProcess:
        """
        Call adb with optional -s <serial>.
        """
        base = ["adb"]
        if serial:
            base += ["-s", serial]
        return self.run(base + args, timeout=timeout)

    def fastboot_cmd(self, args: List[str], serial: Optional[str] = None,
                     timeout: int = 20) -> subprocess.CompletedProcess:
        """
        Call fastboot with optional -s <serial>.
        """
        base = ["fastboot"]
        if serial:
            base += ["-s", serial]
        return self.run(base + args, timeout=timeout)

    def parse_adb_devices(self, output: str) -> List[Dict[str, str]]:
        """
        Parse output from `adb devices -l` to list dict: {serial, state, info}
        """
        lines = output.strip().splitlines()
        devices = []
        for line in lines[1:]:  # bỏ dòng header "List of devices attached"
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            serial = parts[0]
            state = parts[1] if len(parts) > 1 else "unknown"
            info = " ".join(parts[2:]) if len(parts) > 2 else ""
            devices.append({"serial": serial, "state": state, "info": info})
        return devices

    def check_root(self, serial: str) -> Dict[str, str]:
        """
        Check root for a device:
          1) `which su` to check if binary su exists
          2) if yes, try `su -c id` to check uid=0
        """
        result = {"serial": serial, "root": "unknown", "detail": ""}

        # Ensure device is online
        state_proc = self.adb_cmd(["get-state"], serial)
        if state_proc.returncode != 0 or "device" not in state_proc.stdout.strip():
            result["root"] = "unavailable"
            result["detail"] = state_proc.stderr.strip() or state_proc.stdout.strip() or "Device not in 'device' state"
            print(f"Device {serial} is offline.")
            return result
        # 1) Check if su exists
        which_su = self.adb_cmd(["shell", "which su"], serial)
        has_su = (which_su.returncode == 0 and which_su.stdout.strip() != "")
        if not has_su:
            result["root"] = "no"
            result["detail"] = "Cannot find 'su' on the device (which su)."
            return result

        # 2) Try su -c id
        su_id = self.adb_cmd(["shell", "su", "0", "id"], serial)
        out = (su_id.stdout or "").strip()
        err = (su_id.stderr or "").strip()
        if su_id.returncode == 0 and "uid=0" in out:
            result["root"] = "yes"
            result["detail"] = out
            return result

        # Has su but no root permission (Magisk/manager blocked, denied permission, etc.)
        result["root"] = "no"
        result["detail"] = out or err or "Has 'su' but cannot run 'su -c id'. May be denied permission."
        return result

    def refresh_device(self):
        "Refresh device"
        process = self.adb_cmd(["devices", "-l"])
        if process.returncode != 0:
            print("Error: Failed to refresh device.", process.stderr.strip() or process.stdout.strip())
            return
        devices = self.parse_adb_devices(process.stdout)
        self.devices = devices
        for device in devices:
            root = self.check_root(device["serial"])
            print(f"Result root for {device['serial']}: {root['root']}")
            device["root"] = root["root"]
            device["detail"] = root["detail"]
        print(self.devices)

    def get_list_app(self):
        "Get list app"
        process = self.adb_cmd(["shell", "pm list packages"], self.sn)
        if process.returncode != 0:
            print("Error: Failed to get list app.", process.stderr.strip() or process.stdout.strip())
            return
        return process.stdout.strip()

    def get_a_prop(self, prop: str):
        "Get a property"
        process = self.adb_cmd(["shell", "getprop", prop], self.sn)
        if process.returncode != 0:
            print("Error: Failed to get property.", process.stderr.strip() or process.stdout.strip())
            return
        return process.stdout.strip()

    def install_kernelsu(self):
        list_app = self.get_list_app()
        if "me.weishu.kernelsu" in list_app:
            print("KernelSU is installed.")
        else:
            print("KernelSU is not installed. Please install it.")
            return
        fingerprint = self.get_a_prop("ro.odm.build.fingerprint")
        if "oriole" not in fingerprint or "userdebug" not in fingerprint:
            print("Device is not oriole or userdebug.")
            return
        # Reboot to bootloader
        self.adb_cmd(["reboot", "bootloader"], self.sn, timeout=10)
        print("Reboot to bootloader.")
        self.fastboot_cmd(["wait-for-device"], self.sn, timeout=10)
        process = self.fastboot_cmd(["devices"], self.sn, timeout=10)
        if process.returncode != 0:
            print("Error: Failed to reboot to bootloader.", process.stderr.strip() or process.stdout.strip())
            return
        temp = process.stdout.strip()
        if self.sn in temp:
            print("Device is in bootloader.")
        else:
            print("Device is not in bootloader.")
            return
        print("Boot to kernelsu...")
        self.fastboot_cmd(["boot", "kernelsu_boot_px6.img"], self.sn, timeout=10)
        print("Waiting for device...")
        self.adb_cmd(["wait-for-device"], self.sn, timeout=40)
        process = self.adb_cmd(["devices"], self.sn, timeout=10)
        if process.returncode != 0:
            print("Error: Failed to boot to kernelsu.", process.stderr.strip() or process.stdout.strip())
            return
        temp = process.stdout.strip()
        if self.sn in temp:
            print("Device boot with kernelsu success.")
            return True
        else:
            print("Device boot with kernelsu failed.")
            return

    def start_frida(self):
        "Start frida"
        # Check exist frida in data/local/tmp/frida-server
        process = self.adb_cmd(["shell", "ls", "/data/local/tmp"], self.sn)
        if process.returncode != 0:
            print("Error: Failed to check frida.", process.stderr.strip() or process.stdout.strip())
            return
        temp = process.stdout.strip()
        print(temp)
        if "frida-server" in temp:
            print("Frida is installed.")
        else:
            print("Frida is not installed.")
            process = self.adb_cmd(["push", "frida-server", "/data/local/tmp"], self.sn)
            if process.returncode != 0:
                print("Error: Failed to push frida.", process.stderr.strip() or process.stdout.strip())
                return
            print("Frida is installed.")
        print("Set permission for frida-server...")
        process = self.adb_cmd(["shell", "chmod", "755", "/data/local/tmp/frida-server"], self.sn)
        if process.returncode != 0:
            print("Error: Failed to chmod frida.", process.stderr.strip() or process.stdout.strip())
            return
        print("Start frida-server...")
        process = self.adb_cmd(["shell", "nohup", "/data/local/tmp/frida-server", "&"], self.sn)
        if process.returncode != 0:
            print("Error: Failed to start frida.", process.stderr.strip() or process.stdout.strip())
            return
        print(process.stdout.strip())
        print("Frida is started.")
        return
