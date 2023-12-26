# SD Utils for MicroPython


## Description

Utils for basic file and directory operations.

## Getting Started

### Dependencies

* Require sdcard.py from MicroPython lib (include in this repo)

### Example

* Copy sdcard_utils.py in your app
```python
from sdcard_utils import SdCardUtils
sck = 18  # sck pin number
mosi = 19  # mosi pin number
miso = 16  # miso pin number
cs = 17  # cs pin number

sdcard = SdCardUtils(
    0,
    sck=sck,
    mosi=mosi,
    miso=miso,
    cs=cs,
)
sdcard.create_file('myfile.txt')
```

## Author

Alfonso Merino !=
* [alfonsoma75@gmail.com](mailto:alfonsoma75@gmail.com)
* [LinkedIn](https://www.linkedin.com/in/alfonsomerino/)

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the [MIT] License - see the LICENSE.md file for details

## Acknowledgments

* [MicroPython](https://github.com/micropython/micropython)
* [MycroPython Lib](https://github.com/micropython/micropython-lib)
