from __future__ import print_function
import sys
import argparse


parser = argparse.ArgumentParser(description="A utility that can either set the display resolution, show the current display resolution, or list available display resolution modes.")
group = parser.add_mutually_exclusive_group()
group.add_argument('--set', '-s', dest="dimensions", metavar=('N', 'M'), type=int, nargs=2,
                    help='Set the desired resolution of width N and height M. Only available resolutions shown by --list are supported.')
group.add_argument('--current', '-c', action="store_true",
                    help='Show the current display resolution.')
group.add_argument('--list', '-l', dest="modes", action="store_true",
                    help='List the available display resolution modes.')


class DisplayResUtil(object):
    @classmethod
    def set(cls, width=None, height=None, depth=32):
        '''
        Set the primary display to the specified mode
        '''
        current_mode = cls.get()
        if current_mode == (width, height):
            print(f'Resolution is already set to {width} x {height}')
            return

        modes = cls.get_modes()
        if (width, height) not in modes:
            print(f'{width} x {height} is not an available mode.')
            print("Available Modes:")
            modes = cls.get_modes_sorted()
            for mode in modes:
                if mode == current_mode:
                    print(f"    {mode[0]} x {mode[1]} *")
                else:
                    print(f"    {mode[0]} x {mode[1]}")
            return

        if width and height:
            print(f'Setting resolution to {width} x {height}')
        else:
            print('Setting resolution to defaults')

        if sys.platform == 'win32':
            cls._win32_set(width, height, depth)
        elif sys.platform.startswith('linux'):
            cls._linux_set(width, height, depth)
        elif sys.platform.startswith('darwin'):
            cls._osx_set(width, height, depth)

    @classmethod
    def get(cls):
        if sys.platform == 'win32':
            return cls._win32_get()
        elif sys.platform.startswith('linux'):
            return cls._linux_get()
        elif sys.platform.startswith('darwin'):
            return cls._osx_get()

    @classmethod
    def get_modes_sorted(cls):
        return sorted(cls.get_modes(), key=lambda x: x[0] * x[1], reverse=True)

    @classmethod
    def get_modes(cls):
        if sys.platform == 'win32':
            return cls._win32_get_modes()
        elif sys.platform.startswith('linux'):
            return cls._linux_get_modes()
        elif sys.platform.startswith('darwin'):
            return cls._osx_get_modes()

    @staticmethod
    def _win32_get_modes():
        '''
        Get the primary windows display width and height
        '''
        import win32api
        from pywintypes import error

        modes = set()
        i = 0
        try:
            while True:
                mode = win32api.EnumDisplaySettings(None, i)
                modes.add((int(mode.PelsWidth), int(mode.PelsHeight)))
                i += 1
        except error:
            pass

        return modes

    @staticmethod
    def _win32_get():
        '''
        Get the primary windows display width and height
        For some reason this only returns the physical resolution,
        I'm not sure how to get the actual display resolution
        '''
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    @staticmethod
    def _win32_set(width=None, height=None, depth=32):
        '''
        Set the primary windows display to the specified mode
        '''
        import win32api
        import win32con

        if not depth:
            depth = 32

        if not width or not height:
            win32api.ChangeDisplaySettings(None, 0)
            return

        mode = win32api.EnumDisplaySettings()
        mode.PelsWidth = width
        mode.PelsHeight = height
        mode.BitsPerPel = depth
        mode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

        win32api.ChangeDisplaySettings(mode, 0)

    @staticmethod
    def _win32_set_default():
        '''
        Reset the primary windows display to the default mode
        '''
        import ctypes

        user32 = ctypes.windll.user32
        user32.ChangeDisplaySettingsW(None, 0)

    @staticmethod
    def _linux_set(width=None, height=None, depth=32):
        raise NotImplementedError()

    @staticmethod
    def _linux_get():
        raise NotImplementedError()

    @staticmethod
    def _linux_get_modes():
        raise NotImplementedError()

    @staticmethod
    def _osx_set(width=None, height=None, depth=32):
        raise NotImplementedError()

    @staticmethod
    def _osx_get():
        raise NotImplementedError()

    @staticmethod
    def _osx_get_modes():
        raise NotImplementedError()


if __name__ == "__main__":
    args = parser.parse_args()
    if args.dimensions:
        DisplayResUtil.set(*args.dimensions)
    elif args.current:
        mode = DisplayResUtil.get()
        print(f"Current Mode: {mode[0]} x {mode[1]}")
    elif args.modes:
        print("Available Modes:")
        modes = DisplayResUtil.get_modes_sorted()
        current_mode = DisplayResUtil.get()
        for mode in modes:
            if mode == current_mode:
                print(f"    {mode[0]} x {mode[1]} *")
            else:
                print(f"    {mode[0]} x {mode[1]}")
    else:
        parser.print_help()
