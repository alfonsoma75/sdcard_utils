import os
import uos
from sdcard_utils import SdCardUtils

# Declaración de Pins
sck = 18  # sck pin number
mosi = 19  # mosi pin number
miso = 16  # miso pin number
cs = 17  # cs pin number


def test():
    # Intialize SPI peripheral (start with 1 MHz)
    sdcard = SdCardUtils(
        0,
        sck=sck,
        mosi=mosi,
        miso=miso,
        cs=cs,
        baudrate=1000000,
        polarity=0,
        phase=0,
        bits=8,
    )

    print(f'Inicio - {uos.getcwd()}')
    print('-'*8)

    print(f"Create file prueba.txt -> {sdcard.create_file('prueba.txt')}")
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return
    print(f'list dir \n {sdcard.dir()}')

    print(f"Change filename prueba.txt to prueba1.doc -> {sdcard.rename_file('prueba.txt', 'prueba1.doc')}")
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return
    print(f'list dir \n {sdcard.dir()}')

    print(f"Update file prueba.doc 'Hi' {sdcard.update_file('prueba1.doc', 'Hi')}")
    print(f"Update file prueba.doc 'world' {sdcard.update_file('prueba1.doc', 'world')}")
    if sdcard.get_error():
        print(f"Errores -> {sdcard.get_error()}")
        return

    print(f"Read file prueba.doc -> \n {sdcard.read_file('prueba1.doc')}")

    print('Create JSON file')
    data = {
        'name': 'John',
        'age': 12
    }
    print(f"Create file prueba.json -> {sdcard.create_json('prueba.json', data=data)}")
    if sdcard.get_error():
        print(f"Errores -> {sdcard.get_error()}")
        return
    print(f"Read file prueba.json -> \n {sdcard.read_json('prueba.json')}")

    print(f"Delete prueba1.doc {sdcard.delete_file('prueba1.doc')} y prueba.json {sdcard.delete_file('prueba.json')} ")
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return
    print(f'list dir \n {sdcard.dir()}')

    print(f'Create dir /sd4 {sdcard.mkdir("/sd4")}')
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return
    print(f'list dir \n {sdcard.dir()}')

    print(f'Change dir /sd4 {sdcard.cd("/sd4")}')
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return
    print(f'list dir \n {sdcard.dir(os.getcwd())}')

    print(f'Change dir /sd4/other {sdcard.cd("other", create=True)}')
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return
    print(f'List dir of {os.getcwd()} \n {sdcard.dir(os.getcwd())}')
    print(f'change to / {sdcard.cd("/")}')
    print(f'list dir of {os.getcwd()} \n {sdcard.dir(os.getcwd())}')

    csv_data = [
        'nombre;edad;activo',
        'John;22;True',
        'Nataly;28;False',
        'Eva;18;True',
        'Steve;44;True',
    ]
    print(f"Create csv file prueba.csv -> {sdcard.create_csv('prueba.csv', data=csv_data)}")
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return
    print(f'list dir {os.getcwd()} \n {sdcard.dir(os.getcwd())}')
    csv_data = [
        ['nombre', 'edad', 'activo'],
        ['John', '22', True],
        ['Nataly', '28', False],
        ['Eva', '18', True],
        ['Steve', '44', True],
    ]
    print(f"Create csv file based on list of lists prueba1.csv -> {sdcard.create_csv('prueba1.csv', data=csv_data)}")
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return
    print(f'list dir {os.getcwd()} \n {sdcard.dir(os.getcwd())}')
    print(f"Read file prueba.csv -> \n {sdcard.read_csv('prueba.csv')}")
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return

    print(f"Read file prueba.csv with rows as list-> \n {sdcard.read_csv('prueba.csv', row_list=True)}")
    if sdcard.get_error():
        print(f"Errors -> {sdcard.get_error()}")
        return


if __name__ == '__main__':
    test()
