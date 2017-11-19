"""
Control a Somfy 5-channel remote (e.g. Somfy Situo 5 io Pure) with GPIOs from a Raspberry Pi.
See: https://github.com/rfkd/somfy-control
"""

import argparse
import RPi.GPIO as GPIO
import sys

from time import sleep

# LED input pin assignments (use GPIO header pin numbers, NOT Broadcom channel numbers)
LEDS = {
    'LED1': 31,
    'LED2': 32,
    'LED3': 33,
    'LED4': 35
}

# Button output pin assignments (GPIO header pin numbers, NOT Broadcom channel numbers)
BUTTONS = {
    'UP':     36,
    'MY':     37,
    'DOWN':   38,
    'SELECT': 40
}

# Number of seconds after which the remote switches off automatically
TIMEOUT = 5

# Flag to control verbosity output
verbose_output = False


def vprint(*arguments):
    """
    Verbose print, only prints if verbose_output is True.
    :param arguments: Arguments to be printed.
    """

    if verbose_output:
        print(" ".join(map(str, arguments)))


def clean_exit(code):
    """
    Gracefully terminate the script with the given exit code.
    :param code: Exit code to use.
    """

    GPIO.cleanup()
    sys.exit(code)


def press_button(button):
    """
    Press the given button on the remote.
    :param button: Button to be pressed (UP, STOP, DOWN, SELECT).
    """

    # Delay during which the given button remains pressed
    delay_press = 0.25

    GPIO.output(BUTTONS[button], GPIO.LOW)
    sleep(delay_press)
    GPIO.output(BUTTONS[button], GPIO.HIGH)

    vprint("Button " + button + " pressed.")


def get_channel():
    """
    Get the currently active channel from the remote.
    :return: Currently active channel (1..5), 0 if none is active or None upon errors.
    """

    current_channel = None

    if (GPIO.input(LEDS['LED1']) == GPIO.HIGH
            and GPIO.input(LEDS['LED2']) == GPIO.HIGH
            and GPIO.input(LEDS['LED3']) == GPIO.HIGH
            and GPIO.input(LEDS['LED4']) == GPIO.HIGH):
        current_channel = 0
    elif (GPIO.input(LEDS['LED1']) == GPIO.LOW
            and GPIO.input(LEDS['LED2']) == GPIO.HIGH
            and GPIO.input(LEDS['LED3']) == GPIO.HIGH
            and GPIO.input(LEDS['LED4']) == GPIO.HIGH):
        current_channel = 1
    elif (GPIO.input(LEDS['LED1']) == GPIO.HIGH
            and GPIO.input(LEDS['LED2']) == GPIO.LOW
            and GPIO.input(LEDS['LED3']) == GPIO.HIGH
            and GPIO.input(LEDS['LED4']) == GPIO.HIGH):
        current_channel = 2
    elif (GPIO.input(LEDS['LED1']) == GPIO.HIGH
            and GPIO.input(LEDS['LED2']) == GPIO.HIGH
            and GPIO.input(LEDS['LED3']) == GPIO.LOW
            and GPIO.input(LEDS['LED4']) == GPIO.HIGH):
        current_channel = 3
    elif (GPIO.input(LEDS['LED1']) == GPIO.HIGH
            and GPIO.input(LEDS['LED2']) == GPIO.HIGH
            and GPIO.input(LEDS['LED3']) == GPIO.HIGH
            and GPIO.input(LEDS['LED4']) == GPIO.LOW):
        current_channel = 4
    elif (GPIO.input(LEDS['LED1']) == GPIO.LOW
            and GPIO.input(LEDS['LED2']) == GPIO.LOW
            and GPIO.input(LEDS['LED3']) == GPIO.LOW
            and GPIO.input(LEDS['LED4']) == GPIO.LOW):
        current_channel = 5

    return current_channel


def set_channel(channel):
    """
    Setup the channel on the remote.
    :param channel: Channel number to set (1..5).
    """

    # Delay between two channel reads (polling delay)
    delay_get = 0.25

    # Delay between two SELECT button presses
    delay_press = 0.5

    # Wait until the remote is off to avoid race conditions
    if get_channel() == 0:
        vprint("Remote is active, waiting for switch off...")
        safety_buffer = 1
        retries = int((TIMEOUT + safety_buffer) // delay_get)
        for i in range(0, retries):
            if get_channel() == 0:
                break
            if i == retries - 1:
                print("Error: Remote doesn't seem to switch off. Is the script configuration correct?")
                clean_exit(1)
            sleep(delay_get)
        vprint("Remote is now off.")

    # Activate the remote and check the currently selected channel
    press_button('SELECT')
    current_channel = get_channel()
    vprint("Channel {} is currently selected.".format(current_channel))
    if current_channel == channel:
        return

    # Select the correct channel
    number_of_channels = 5
    button_presses_needed = (number_of_channels - current_channel + int(channel)) % number_of_channels
    for i in range(0, button_presses_needed):
        press_button('SELECT')
        sleep(delay_press)

    # Exit if the channel switch was not successful
    current_channel = get_channel()
    if current_channel != channel:
        print("Error: Unable to select the specified channel. Current channel is {}.".format(current_channel))
        clean_exit(1)


def main():
    """
    Main entry point.
    """

    global verbose_output

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Control a Somfy 5-channel remote from a Raspberry Pi using GPIOs.\n'
                                                 'See: https://github.com/rfkd/somfy-control',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--channel', dest='channel', choices=['1', '2', '3', '4', '5'],
                        help='remote control channel number', required=True)
    parser.add_argument('-b', '--button', dest='button', choices=['UP', 'STOP', 'DOWN'],
                        help='remote control button', required=True)
    parser.add_argument('-o', '--override-warnings', dest='warnings', action='store_false',
                        help='override all warnings')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='enable verbose output')
    arguments = parser.parse_args()
    verbose_output = arguments.verbose

    # Configure RPi.GPIO (use pin numbers instead of Broadcom channel numbers)
    GPIO.setwarnings(arguments.warnings)
    GPIO.setmode(GPIO.BOARD)
    for name in LEDS:
        GPIO.setup(LEDS[name], GPIO.IN)
    for name in BUTTONS:
        GPIO.setup(BUTTONS[name], GPIO.OUT, initial=GPIO.HIGH)

    # Select the channel
    set_channel(arguments.channel)

    # Press the button
    press_button(arguments.button)

    # Terminate the script gracefully
    clean_exit(0)


if __name__ == '__main__':
    main()
