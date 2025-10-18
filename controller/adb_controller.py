from helpers.custom_adb import CustomADB


class ADBController:
    def __init__(self):
        print('Initializing ADB Controller')
        self.custom_adb = CustomADB()

    def handle_nab(self, arg):
        device = None
        for _ in range(2):
            for device in self.custom_adb.devices:
                if "serial" in device:
                    if device["serial"] == arg:
                        device = device
                        break
            if not device:
                print(f"Device {arg} not found. Refreshing device...")
                self.custom_adb.refresh_device()
        if not device:
            print(f"Device {arg} not found.")
            return
        self.custom_adb.sn = device["serial"]
        if device.get('root', {}) == "yes":
            print("Device is already root.")
        else:
            self.custom_adb.install_kernelsu()
            root = self.custom_adb.check_root(self.custom_adb.sn)
            device["root"] = root["root"]
            device["detail"] = root["detail"]
            if device.get('root', {}) != "yes":
                print("Device is not root.")
                return
        print(device)
        self.custom_adb.start_frida()
        return
