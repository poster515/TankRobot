import sys
from cs50 import get_string

def main():
    if (len(sys.argv) != 2):
        print("Usage: python caesar.py [int]")
        sys.exit(1)

    while True:
        try:
            plaintext = get_string("plaintext: ")
            break
        except TypeError:
            plaintext = get_string("plaintext: ")

    ciphertext = ""
    for c in plaintext:
        if c.isalpha() and c.islower():
            if ord(c) - ord("a") + int(sys.argv[1]) >= 26:
                ciphertext += chr(ord(c) + int(sys.argv[1]) - (26 * ((ord(c) - ord("a") + int(sys.argv[1])) // 26)))
            else:
                ciphertext += chr(ord(c) + int(sys.argv[1]))

        elif c.isalpha() and c.isupper():
            if ord(c) - ord("A") + int(sys.argv[1]) >= 26:
                ciphertext += chr(ord(c) + int(sys.argv[1]) - (26 * ((ord(c) - ord("A") + int(sys.argv[1])) // 26)))
            else:
                ciphertext += chr(ord(c) + int(sys.argv[1]))

        else:
            ciphertext += c

    print("ciphertext: {}".format(ciphertext))

if __name__ == "__main__":
    main()