import os


def clear_screen():
    # Cách 1: gọi lệnh hệ điều hành
    os.system('cls' if os.name == 'nt' else 'clear')
    # Cách 2 (tuỳ chọn, nhanh, không cần subprocess):
    # print("\033[2J\033[H", end="")  # ANSI escape: xoá toàn bộ & đưa con trỏ về đầu