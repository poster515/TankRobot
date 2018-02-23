from cs50 import get_int

def main():
    s = get_int("Height: ")
    while s < 0 or s > 23:
        s = get_int("Height: ")

    for i in range(s):
        print("{}".format(" " * (s - i - 1)), end="")
        print("{}".format("#" * (i + 1)), end="")
        print("  ", end="")
        print("{}".format('#' * (i + 1)))

if __name__ == "__main__":
    main()