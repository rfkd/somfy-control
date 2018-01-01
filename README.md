# somfy-control

### DESCRIPTION

Control a Somfy 5-channel remote (e.g. Somfy Situo 5 io Pure) from a Raspberry Pi using GPIOs.

### REQUIREMENTS

* Raspberry Pi (should work with any revision)
* Somfy 5-channel remote
* Python 2.7 with [RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO), install with `apt-get install python-rpi.gpio`

### HARDWARE

It is quite simple to modify and connect a Somfy Situo 5 io Pure remote control as it kindly already provides soldering pads for all LEDs and buttons. Although this remote is originally powered by a CR2430 3V battery it can be supplied by the 3.3V of the Raspberry Pi.

**_Solder some resistors into the cables to limit the current in case something goes wrong._**

**LED connection schematic:**
```
3V3 (RPi)
 |
LED
 |
R=560
 |
 o  <--- R=10k --- RPi GPI
 |
Somfy µC GPO
```

**Button connection schematic:**
```
                          3V3 (RPi)
                           |
                          R=22k
                           |
Somfy µC GPI --- R=100 --- o  <--- R=330 --- RPi GPO
                           |
                            \  (Button)
                           |
                          GND (RPi)
```

In both schematics the `<---` indicates the position where the connection to the Raspberry Pi must be soldered to. The rest belongs to the original circuit of the remote control.

### CONFIGURATION

`somfy-control` can be configured by modifying the Python dictionaries `LEDS` and `BUTTONS` at the top of the file. Either wire the remote control to the Raspberry Pi as shown or change the dictionary values to the GPIO header pin numbers (**not** Broadcom channel numbers) the related wires are connected to. Do **not** change the dicionary keys (`LED1`, `UP`, ...).

**Example:** Change `'LED1': 32,` to `'LED1': 29,` to use pin number 29 instead of 32 for LED1.

### USAGE

Execute `somfy-control.py --help` to see a quick overview over all available command line parameters. The following parameters are available:

`-h`, `--help` &nbsp; Print the help message and exit.

`-c {1,2,3,4,5}`, `--channel {1,2,3,4,5}` &nbsp; Remote control channel number.

`-b {UP,MY,DOWN}`, `--button {UP,MY,DOWN}` &nbsp; Remote control button to press.

`-o`, `--override-warnings` &nbsp; Override all warnings.

`-v`, `--verbose` &nbsp; Enable verbose output.

Both parameters `--channel` and `--button` are mandatory. Please not that `somfy-control.py` must be run as **root** to control the GPIOs of the Raspberry Pi.

**Example:** `# somfy-control.py -c 3 -b DOWN`
