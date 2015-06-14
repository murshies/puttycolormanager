
import configparser
import logging
import winreg

BASE_PUTTY_PATH = 'Software\\SimonTatham\\PuTTY\\Sessions\\'
PUTTY_COLOR_ORDER = ['Default Foreground',
                     'Default Bold Foreground',
                     'Default Background',
                     'Default Bold Background',
                     'Cursor Text',
                     'Cursor Color',
                     'ANSI Black',
                     'ANSI Black Bold',
                     'ANSI Red',
                     'ANSI Red Bold',
                     'ANSI Green',
                     'ANSI Green Bold',
                     'ANSI Yellow',
                     'ANSI Yelow Bold',
                     'ANSI Blue',
                     'ANSI Blue Bold',
                     'ANSI Magenta',
                     'ANSI Magenta Bold',
                     'ANSI Cyan',
                     'ANSI Cyan Bold',
                     'ANSI White',
                     'ANSI White Bold']
PUTTY_DEFAULT_COLORS = (
    (187, 187, 187), # 0
    (255, 255, 255), # 1
    (0, 0, 0),       # 2
    (85, 85, 85),    # 3
    (0, 0, 0),       # 4
    (0, 255, 0),     # 5
    (0, 0, 0),       # 6
    (85, 85, 85),    # 7
    (187, 0, 0),     # 8
    (255, 85, 85),   # 9
    (0, 187, 0),     # 10
    (85, 255, 85),   # 11
    (187, 187, 0),   # 12
    (255, 255, 85),  # 13
    (0, 0, 187),     # 14
    (85, 85, 255),   # 15
    (187, 0, 187),   # 16
    (255, 85, 255),  # 17
    (0, 187, 187),   # 18
    (85, 255, 255),  # 19
    (187, 187, 187), # 20
    (255, 255, 255)  # 21
)
PUTTY_REG_COLOR_TYPE = winreg.REG_SZ
# Used in Windows Registry API calls, where the calls have reserved parameters
# that are always set to zero.
WINDOWS_RESERVED = 0
# The INI section name for color themes read from an INI file.
COLOR_INI_SECTION_NAME = 'Colors'

def unpack_registry_color(reg_value):
    '''Given the value of a color read from the registry, return a list of
    integers of the RGB values. "reg_value" will be a tuple of 2 items,
    containing the value of the registry item (a string in our case), and an
    integer representing the item type (1 in our case). The colors in the
    registry are comma-separated (e.g. 255,255,255).'''
    return unpack_color(reg_value[0])

def unpack_color(color_val):
    '''Given a color in the form of a comma-separated RGB string, return a
    tuple of integers. Whitspace is allowed between integers.'''
    return tuple([int(x.strip()) for x in color_val.split(',')])

def pack_registry_colors(color_list):
    '''Converts a color in the form of an RGB list of integers into the format
    expected by PuTTY (a comma-separated list of integers in the form of a
    string).'''
    return ','.join([str(x) for x in color_list])

def read_session_colors(session_name):
    '''Read all of the color values for the PuTTY session with name
    "session_name".'''
    full_session_name = BASE_PUTTY_PATH + session_name
    colors_list = []
    
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        full_session_name) as session:
        for color_number in range(len(PUTTY_COLOR_ORDER)):
            reg_color_name = 'Colour{0}'.format(color_number)
            reg_value = winreg.QueryValueEx(session, reg_color_name)
            colors = unpack_registry_color(reg_value)
            colors_list.append(colors)
    
    return colors_list

def writeSessionColors(session_name, color_list):
    '''Given the name of a session "session_name" and a list of RGB integer
    lists, set color_list as the colors for session_name.'''
    full_session_name = BASE_PUTTY_PATH + session_name
    
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, full_session_name,
                        WINDOWS_RESERVED, winreg.KEY_WRITE) as session:
        for color_number, color_val in enumerate(color_list):
            reg_color_name = 'Colour{0}'.format(color_number)
            packed_color = pack_registry_colors(color_val)
            winreg.SetValueEx(session, reg_color_name, WINDOWS_RESERVED,
                              PUTTY_REG_COLOR_TYPE, packed_color)

def get_all_session_names():
    '''Get the name of all PuTTY sessions.'''
    session_names = []
    
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, BASE_PUTTY_PATH) as base:
        try:
            i = 0
            while True:
                session_names.append(winreg.EnumKey(base, i))
                i += 1
        except WindowsError:
            pass
    
    return session_names

def read_colors_from_INI(ini_name):
    '''Given the name of an INI file "ini_name", create a list of RGB tuples
    containing the colors found in ini_name.'''
    color_config = configparser.SafeConfigParser()
    color_config.read(ini_name)
    color_dict = color_config[COLOR_INI_SECTION_NAME]
    color_list = []
    
    for color_number, color_name in enumerate(PUTTY_COLOR_ORDER):
        reg_color_name = 'Colour{0}'.format(color_number)
        curr_color = PUTTY_DEFAULT_COLORS[color_number]
        if reg_color_name in color_dict:
            curr_color = unpack_color(color_dict[reg_color_name])
        elif color_name in color_dict:
            curr_color = unpack_color(color_dict[color_name])
        else:
            logging.warning(('No value for {0} ({1}) found in {2} - using the '
                             'default value {3}').format(
                                reg_color_name, color_name, ini_name,
                                curr_color))
        color_list.append(curr_color)
    
    return color_list

def main():
    print(read_colors_from_INI('solarized_dark.ini'))

if __name__ == '__main__':
    main()

