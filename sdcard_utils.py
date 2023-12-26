"""
Utils to use SD Card with MicroPython.

Requires sdcard.py from MicroPython libs.

Example usage:

Connection:
    sdcard = SdCardUtils(
        0,
        sck=sck,
        mosi=mosi,
        miso=miso,
        cs=cs,
        baudrate=1000000,  # Optional
        polarity=0,  # Optional
        phase=0,  # Optional
        bits=8  # optional
    )

Check errors:
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")

List dir:
    print(f'list dir \n {sdcard.dir()}')
    # or
    print(f'list dir \n {sdcard.dir(my_dir)}')

Create dir:
    sdcard.mkdir("/sd4")

Change dir:
    sdcard.cd("/sd4")

Create and change dir:
    sdcard.cd("other", create=True)

Delete dir:
    sdcard.rmdir('other')

Create file:
    sdcard.create_file('prueba.txt')

Change filename:
    sdcard.rename_file('prueba.txt', 'prueba1.doc')

Update file:
    sdcard.update_file('prueba1.doc', 'Hi')
    sdcard.update_file('prueba1.doc', 'world')

Read file data:
    data = sdcard.read_file('prueba1.doc')

Create JSON file:
   data = {
        'name': 'John',
        'age': 12
    }
    sdcard.create_json('prueba.json', data=data)

Read JSON file:
    data = sdcard.read_json('prueba.json')

Create CSV file:
    # from list of str
     csv_data = [
        'nombre;edad;activo',
        'John;22;True',
        'Nataly;28;False',
        'Eva;18;True',
        'Steve;44;True',
    ]
    sdcard.create_csv('prueba.csv', data=csv_data)

    # from list of lists
    csv_data = [
        ['nombre', 'edad', 'activo'],
        ['John', '22', True],
        ['Nataly', '28', False],
        ['Eva', '18', True],
        ['Steve', '44', True],
    ]
    sdcard.create_csv('prueba1.csv', data=csv_data)

Read CSV from file:
    # rows as str
    sdcard.read_csv('prueba.csv')

    # rows as list.
    sdcard.read_csv('prueba.csv', row_list=True)

Delete file:
    sdcard.delete_file('prueba1.doc')
"""

import json
import uos
from machine import Pin, SPI
from lib import sdcard


class SdCardUtils:
    JSON = 'json'
    CSV = 'csv'
    _error = ''
    _base_dir = '/sd'

    def __init__(
            self, channel: int, sck: int, mosi: int, miso: int, cs: int, mount: str = '',
            baudrate: int = 1000000, polarity: int = 0, phase: int = 0, bits: int = 8
    ):
        if not sck or not mosi or not miso or not cs:
            raise Exception('Invalid SCK or MOSI or MISO or sc')

        # required
        self._sck = Pin(sck, Pin.OUT)
        self._mosi = Pin(mosi, Pin.OUT)
        self._miso = Pin(miso, Pin.OUT)
        self._cs = Pin(cs, Pin.OUT)

        # Defaults
        self._mount = mount if mount else '/sd'
        self._channel = channel if channel else 0
        self._baudrate = baudrate
        self._polarity = polarity
        self._phase = phase
        self._bits = bits

        self._initialize()

    def _initialize(self):
        spi = SPI(
            self._channel,
            baudrate=self._baudrate,
            polarity=self._polarity,
            phase=self._phase,
            bits=self._bits,
            firstbit=SPI.MSB,
            sck=self._sck,
            mosi=self._mosi,
            miso=self._miso
        )

        # Initialize SD card
        sd = sdcard.SDCard(spi, self._cs)

        # Mount filesystem FAT, FAT32
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, self._mount)

    def _clean_error(self) -> None:
        """
        Clean error variable
        @return: Nothing
        @rtype: None
        """
        self._error = ''

    def get_error(self) -> str:
        """
        Getter for error variable
        @return: error
        @rtype: str
        """

        # OSError when creating new directory. the directory is created but throws this error
        if 'OSError' in self._error:
            self._error = ''
        return self._error

    def dir_exists(self, path: str) -> bool:
        """
        Check if dir exists
        @param path: Dir path
        @type path: str
        @return: True if exists or False if not
        @rtype: bool
        """
        self._clean_error()
        try:
            uos.chdir(path)
            return True
        except OSError:
            self._error = f'Error: {OSError}'
            return False
        except Exception as e:
            self._error = f'Unknow error: {e}'

    def file_exists(self, file_name: str, path: str) -> bool:
        """
        Check if file exists
        @param file_name: File name
        @type file_name: str
        @param path: Dir path
        @type path: str
        @return: True if exists or False if not
        @rtype: bool
        """
        self._clean_error()
        if not self.dir_exists(path):
            return False

        if file_name in uos.listdir(path):
            return True

        self._error = "File not exists"
        return False

    def exists(self, file_path: str) -> bool:
        """
        Check file path exists
        @param file_path: Dir path
        @type file_path: str
        @return: True if exists or False if not
        @rtype: bool
        """
        self._clean_error()

        find = file_path.rfind('/')

        # Not found
        if find == -1:
            self._error = 'file_path is not a path'
            return False

        path = file_path[:find]
        file_name = file_path[find + 1:]

        # dir not found
        if not self.dir_exists(path):
            return False

        return self.file_exists(file_name, path)

    def cd(self, dir_name: str, create: bool = False) -> bool:
        """
        Change dir if dir path exists
        @param dir_name: Dir path
        @type dir_name: str
        @param create: Create dir if it doesn't exist
        @type create: bool
        @return: True is dir is changed or False if not
        @rtype: bool
        """
        self._clean_error()
        if dir_name and not self.dir_exists(dir_name) and create:
            self.mkdir(dir_name)

        if dir_name and self.dir_exists(dir_name):
            try:
                uos.chdir(dir_name)
                return True
            except OSError as oe:
                if oe.errno == -2:
                    return True
            except Exception as e:

                print('Error change', e, type(e))
                return False

        self._error = f"Something has gone wrong, can't change to directory {dir_name}"
        return False

    def rmdir(self, dir_name: str) -> bool:
        """
        Remove directory
        @param dir_name: Name of directory to remove
        @type dir_name: str
        @return: True if success, False if not or error
        @rtype:
        """
        try:
            uos.rmdir(dir_name)
            return True
        except Exception as e:
            self._error = f'can\'t delete directory {dir_name} -> {e}'
            return False
    @staticmethod
    def dir(dir_name: str = '/') -> list:
        """
        List all files in a directory
        @param dir_name: directory path to list
        @type dir_name: str
        @return: list of files and folders
        @rtype: list
        """
        return uos.listdir(dir_name)

    def mkdir(self, dir_name: str) -> bool:
        """
        Create dir if it doesn't exist.
        @param dir_name: name of dir to create
        @type dir_name: str
        @return: True if dir was created False if not
        @rtype: bool
        """
        self._clean_error()

        if not dir_name:
            self._error = f'dir_name is empty'
            return False

        if self.dir_exists(dir_name):
            self._error = f'{dir_name} already exists'
            return False

        try:
            uos.mkdir(dir_name)

            return True

        except Exception as e:
            self._error = f'can\'t create directory {dir_name} -> {e}'
            return False

    @staticmethod
    def is_file(file_name: str) -> bool:
        """
        Check if file_name is a file
        @param file_name: name of the file
        @type file_name: str
        @return: True if file_name is a file or False if not
        @rtype: bool
        """
        try:
            f = open(file_name, 'r')
            f.close()
            return True
        finally:
            return False

    def is_dir(self, dir_name: str) -> bool:
        """
        Check if dir_name is a directory
        @param dir_name: name of the directory
        @type dir_name: str
        @return: True if is a directory or False if not
        @rtype: bool
        """
        actual = uos.getcwd()
        if self.cd(dir_name):
            self.cd(actual)
            return True

        return False

    def create_file(self, file_name: str, dir_name: str = '', data: str or list = None, force: bool = False) -> bool:
        """
        Create a file in the specified directory, if directory does not exist we can force create.
        @param file_name: Name of file to create
        @type file_name: str
        @param dir_name: Name or path of the directory
        @type dir_name: str
        @param data: Data to write in file
        @type data: str(one line) or list(multiple lines)
        @param force: force directory creation if not exists
        @type force: bool
        @return: True if file was created or False if not
        @rtype: bool
        """

        return self._create(file_name=file_name, dir_name=dir_name, data=data, force=force)

    def update_file(self, file_name: str, data: str or list) -> bool:
        """
        Update file contents.
        @param file_name: name of file to update
        @type file_name: str
        @param data: data to add to file
        @type data: str or list
        @return: True if update was done False if not or error
        @rtype: bool
        """
        return self._update(file_name, data)

    def delete_file(self, file_name: str) -> bool:
        """
        Delete file
        @param file_name: Name of the file to delete.
        @type file_name: str
        @return: True if file was deleted, False ir not or error.
        @rtype: bool
        """
        self._clean_error()
        file_name = f'{uos.getcwd()}{file_name}' if '/' not in file_name else file_name

        if self.exists(file_name):
            try:
                uos.remove(file_name)
                return True
            except Exception as e:
                self._error = f"{file_name} can't delete -> {e}"
                return False

        self._error = f'File {file_name} not exitsts or add path to filename ex; /file.txt'
        return False

    def rename_file(self, file_name: str, new_name: str) -> bool:
        """
        Change the name of a file
        @param file_name: name of actual file.
        @type file_name: str
        @param new_name: new name of file
        @type new_name: str
        @return: True if success False if not or error
        @rtype: bool
        """
        self._clean_error()

        file_name = f'{uos.getcwd()}{file_name}' if '/' not in file_name else file_name

        if not self.exists(file_name):
            self._error = f'{file_name} not exists or add path to filename ex; /file.txt'
            return False

        try:
            uos.rename(file_name, new_name)
            return True
        except Exception as e:
            self._error = f"can't rename {file_name} to {new_name} -> {e}"
            return False

    def read_file(self, file_name: str) -> str or list:
        """
        Read data of a file
        @param file_name: name of the file to be read
        @type file_name:str
        @return: data of the file
        @rtype: str or list
        """
        return self._read(file_name)

    def create_csv(self, file_name: str, dir_name: str = '', data: list = None, force: bool = False) -> bool:
        """
        Create a csv file.
        @param file_name: Name of the file to be create.
        @type file_name: str
        @param dir_name: path of the directory where the file will be created
        @type dir_name: str
        @param data: data to include in the file
        @type data: list or None
        @param force: True to create the directory if not exists, False if not (by default)
        @type force: bool
        @return: True if file was created, False if not or error
        @rtype: bool
        """
        return self._create(file_name=file_name, dir_name=dir_name, data=data, force=force, file_type=self.CSV)

    def read_csv(self, file_name: str, separator: str = ';', newline: str = '\n', row_list: bool = False) -> list:
        """
        read a csv file
        @param file_name: Name of the file to be read
        @type file_name: str
        @param separator: column separator for csv file, ';' by default
        @type separator: str
        @param newline: row separator for csv file, '\n' by default
        @type newline: str
        @param row_list: for csv file, rows in list.
        @type row_list: bool
        @return: Data of the file
        @rtype: list
        """
        return self._read(file_name, self.CSV, separator, newline, row_list)

    def update_csv(self, file_name: str, data: list) -> bool:
        """
        Add new data to a csv file.
        @param file_name: Name of the file to be update.
        @type file_name: str
        @param data: data to add
        @type data: list
        @return: True if success, False if not or error
        @rtype: bool
        """
        return self._update(file_name, data, self.CSV)

    def create_json(self, file_name: str, dir_name: str = '', data: dict = None, force: bool = False) -> bool:
        """
        Create a JSON File
        @param file_name: Name of the file to be create
        @type file_name: str
        @param dir_name: Directory where the file will be created
        @type dir_name: str
        @param data: Data to add to the file
        @type data: dict
        @param force: True to force to create the directory if not exists, False if not or error
        @type force: bool
        @return: True if success, False if not or error
        @rtype: bool
        """
        return self._create(file_name=file_name, dir_name=dir_name, data=data, force=force, file_type=self.JSON)

    def update_json(self, file_name: str, data: dict or json) -> bool:
        return self._update(file_name, data, self.JSON)

    def read_json(self, file_name: str) -> dict:
        return self._read(file_name, self.JSON)

    def _read(self, file_name: str, file_type: str = '',
              separator: str = ';', newline: str = '\n', row_list: bool = False) -> bool or list or dict or str:
        """
        Read data from file
        @param file_name: Name of the file to be read
        @type file_name: str
        @param file_type: Type of the file. Can be 'json' or 'csv' or None to other extensions
        @type file_type: str
        @param separator: column separator for csv file, ';' by default
        @type separator: str
        @param newline: row separator for csv file, '\n' by default
        @type newline: str
        @param row_list: for csv file, rows in list.
        @type row_list: bool
        @return: Data readed from the file
        @rtype: bool or list or dict or str
        """
        self._clean_error()
        file_name = f'{uos.getcwd()}{file_name}' if '/' not in file_name else file_name

        if not self.exists(file_name):
            self._error = f'{file_name} not exists'
            return False

        try:
            if file_type == self.JSON:
                data = self._read_json(file_name)
            elif file_type == self.CSV:
                data = self._read_csv(file_name, separator, newline, row_list)
            else:
                data = self._read_file(file_name)
            return data

        except Exception as e:
            self._error = f"can't read data from {file_name}  -> {e}"
            return False

    def _create(
            self, file_name: str, dir_name: str = '', data: list or str or dict = None, force: bool = False,
            file_type: str = ''
    ) -> bool:
        """
        Create new file
        @param file_name: Name of the file to be create
        @type file_name: str
        @param dir_name: Directory where the file will be created
        @type dir_name: str
        @param data: Data to be written to the file
        @type data: list or str or dict
        @param force: True to force to create directory if not exists, False by default
        @type force: bool
        @param file_type: Type of the file. Can be 'json' or 'csv' or None to other extensions
        @type file_type: str
        @return: Data readed from file
        @rtype: list or str or dict
        """
        self._clean_error()

        if not file_name:
            self._error = 'file_name is empty'
            return False

        # if not dir name, get actual directory
        dir_name = dir_name if dir_name and dir_name != '/' else uos.getcwd()

        if dir_name != '/' and self.dir_exists(dir_name) and not force:
            self._error = f'"{dir_name}" not exists, use forde=True to force creation'
            return False

        if force:
            uos.mkdir(dir_name)

        dir_name += '' if dir_name.endswith('/') else '/'
        dir_name = dir_name if dir_name != '/' else ''

        try:

            if file_type == self.JSON:
                self._write_json(data=data, file_name=file_name, dir_name=dir_name)
            elif file_type == self.CSV:
                self._write_csv(data=data, file_name=file_name, dir_name=dir_name)
            else:
                self._write_data(data=data, file_name=file_name, dir_name=dir_name)

            return True

        except Exception as e:
            self._error = f'Error creating file {dir_name}{file_name} -> {e}'
            return False

    def _update(self, file_name: str, data: str or list or dict, file_type: str = '') -> bool:
        """
        Update a file with the given data
        @param file_name: Name of the file to update
        @type file_name: str
        @param data: data to be added to the file
        @type data: str or list or dict
        @param file_type: Type of the file. Can be 'json' or 'csv' or None to other extensions
        @type file_type: str
        @return: True if success, False if not or error
        @rtype: bool
        """

        self._clean_error()
        file_name = f'{uos.getcwd()}{file_name}' if '/' not in file_name else file_name

        if self.exists(file_name):
            try:
                if file_type == self.JSON:
                    self._write_json(data=data, file_name=file_name, method='a')
                elif file_type == self.CSV:
                    self._write_csv(data=data, file_name=file_name, method='a')
                else:
                    self._write_data(data=data, file_name=file_name, method='a')

                return True
            except Exception as e:
                self._error = f'{file_name} File update error -> {e}'
                return False

        self._error = f'{file_name} not exists or add path to filename ex; /file.txt'
        return False

    def _write_data(self, data: str or list or dict, file_name: str, dir_name: str = '',  method: str = 'w') -> bool:
        """
        Write data into a file
        @param data: Data to be writted in a file
        @type data: str or list or dict
        @param file_name: Name of the file to write
        @type file_name: str
        @param dir_name: Directory name where the file is
        @type dir_name: str
        @param method: Method to use for writing. 'w' write (default), 'a' append.
        @type method: str
        @return: True if success, False if not or error
        @rtype: bool
        """
        try:
            if not data:
                f = open(f'{dir_name}{file_name}', method)
                f.close()
            else:
                with open(f'{dir_name}{file_name}', method) as f:
                    if isinstance(data, list):
                        f.writelines(data)
                    else:
                        f.write(data)
            return True

        except Exception as e:
            self._error = f'{file_name} File write error -> {e}'
            return False

    def _write_csv(
            self, data: list, file_name: str, dir_name: str = '',  method: str = 'w',
            separator: str = ';', newline: str = '\n') -> bool:

        """
        Write csv file.
        @param data: Data to be written
        @type data: list
        @param file_name: Name of the file to write
        @type file_name: str
        @param dir_name: Directory name where the file is
        @type dir_name: str
        @param method: Method to use for writing. 'w' write (default), 'a' append.
        @type method: str
        @param separator: Separator from csv columns, ';' by default
        @type separator: str
        @param newline: New line indicator for rows, '\n' by default
        @type newline: str
        @return: True if success, False if error
        @rtype: bool
        """

        try:
            with open(f'{dir_name}{file_name}', method) as f:
                for item in data:
                    print('Item', isinstance(item, list), item)
                    if isinstance(item, list):
                        item = self._str_join(item, separator)
                    print(item)
                    f.write(f'{item}{newline}')
                return True

        except Exception as e:
            self._error = f'{file_name} CSV File write error -> {e}'
            return False

    def _write_json(
            self, data: dict, file_name: str, dir_name: str = '',  method: str = 'w') -> bool:

        """
        Write data into a json file
        @param data: Data to be write
        @type data: dict
        @param file_name: Name of the file
        @type file_name: str
        @param dir_name: Name of the directory where the file is
        @type dir_name: str
        @param method: Method to use for writing. 'w' write (default), 'a' append.
        @type method: str
        @return: True if success, False if not or error
        @rtype: bool
        """

        try:
            with open(f'{dir_name}{file_name}', method) as f:
                f.write(json.dumps(data))
            return True

        except Exception as e:
            self._error = f'{file_name} File write (json) error -> {e}'
            return False

    @staticmethod
    def _read_file(file_name: str) -> str or list:
        """
        Read data from file
        @param file_name: Name of the file to be read
        @type file_name: str
        @return: Data readed from the file
        @rtype: str or list
        """
        with open(file_name, 'r') as f:
            data = f.readlines()

        return data

    @staticmethod
    def _read_csv(file_name: str, separator: str = ';', newline: str = '\n', row_list: bool = False) -> list:
        """
        Read data from csv file
        @param file_name: Name of the file to be read
        @type file_name: str
        @param separator: column separator for csv file, ';' by default
        @type separator: str
        @param newline: row separator for csv file, '\n' by default
        @type newline: str
        @param row_list: for csv file, rows in list.
        @type row_list: bool
        @return: Data readed from the file
        @rtype: list
        """
        with open(file_name, 'r') as f:
            data = f.readlines()
            data = [item.replace(newline, '') for item in data]

            if row_list:
                data = [item.split(separator) for item in data]

        return data

    @staticmethod
    def _read_json(file_name: str) -> dict:
        """
        Read data from json file
        @param file_name: Name of the file to be read
        @type file_name: str
        @return: Data readed from the file
        @rtype: dict
        """
        with open(file_name, 'r') as f:
            reader = json.load(f)

        return reader

    @staticmethod
    def _str_join(data: list, separator: str = ';') -> str:
        """
        Convert a list and his elements to string with the indicated separator
        @param data: list to convert
        @type data: list
        @param separator: separator for csv file, ';' by default
        @type separator:str
        @return: str joined elements of the list
        @rtype: str
        """
        return separator.join(list(map(lambda x: x if isinstance(x, str) else str(x), data)))
