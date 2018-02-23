from cs50 import get_int

def main():


    while True:

        try:
            cardNum = get_int("Number: ")
            break
        except TypeError:
            cardNum = get_int("Number: ")


    i = 1
    total, partial = 0, 0

    while (10 ** i) < cardNum:
        partial = (cardNum // (10 ** i)) % 10

        partial = partial * 2
        # print("Partial: {}".format(partial))

        if partial >= 10:
            total += 1 + (partial % 10)
            # print("Total: {}".format(total))
        else:
            total += partial
            # print("Total: {}".format(total))

        i += 2

    i = 0
    while (10 ** i) < cardNum:
        total += (cardNum // (10 ** i)) % 10
        # print("Total (second pass): {}".format(total))
        i += 2

    i = 0
    while (10 ** i) < cardNum:
        i += 1

    lastTwoDigits = ((cardNum // (10 ** (i - 1))) * 10) + (cardNum // (10 ** (i - 2))) % 10
    # print("Last two digits: {}".format(lastTwoDigits))

    if total % 10 != 0:
        print("INVALID")
        return
    elif lastTwoDigits == 34 or lastTwoDigits == 37:
        print("AMEX")
        return
    elif 51 <= lastTwoDigits <= 55:
        print("MASTERCARD")
        return
    elif lastTwoDigits // 10 == 4:
        print("VISA")
        return
    else:
        print("Unknown")
        return

if __name__ == "__main__":
    main()