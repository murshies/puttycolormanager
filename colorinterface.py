
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
# Used in Windows Registry API calls, where the calls have reserved
# parameters that are always set to zero.
WINDOWS_RESERVED = 0
# The INI section name for color themes read from an INI file.
COLOR_INI_SECTION_NAME = 'Colors'

def unpack_color(color_val):
    """
    Get a RGB color tuple from a value packed as a string. The format is
    the format used by PuTTY in the Windows registry. Whitspace is
    allowed between integers.
    
    Parameters
    ----------
    reg_values : string
        This is the value read from the registry. It is a string in the
        format red,green,blue.
    
    Returns
    -------
    tuple
        a tuple containing the RGB values as integers
    
    Raises
    ------
    ValueError
        when the input string a malformed
    """
    return tuple([int(x.strip()) for x in color_val.split(',')])

def pack_registry_colors(color_list):
    """
    Converts RGB integer values into the format used by PuTTY to store
    colors in the Windows registry.
    
    Parameters
    ----------
    color_list : list or tuple
        the collection of three integers that make up the RGB values for
        a color
    
    Returns
    -------
    string
        color_list as a string in the format red,green,blue
    """
    return ','.join([str(x) for x in color_list])

def read_session_colors(session_name):
    """
    Read all of the color values for the PuTTY session.
    
    Parameters
    ----------
    session_name : string
        the name of the PuTTY session
    
    Returns
    -------
    list
        a list of tuples. Each tuple is a collection of three integers,
        which are the RGB values for that color. The colors are ordered
        as they are in PuTTY (i.e. PUTTY_COLOR_ORDER).
    """
    full_session_name = BASE_PUTTY_PATH + session_name
    colors_list = []
    
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        full_session_name) as session:
        for color_number in range(len(PUTTY_COLOR_ORDER)):
            reg_color_name = 'Colour{0}'.format(color_number)
            reg_value = winreg.QueryValueEx(session, reg_color_name)
            color_from_reg = reg_value[0]
            colors = unpack_color(color_from_reg)
            colors_list.append(colors)
    
    return colors_list

def write_session_colors(session_name, color_list):
    """
    Write a color list to the Windows registry for a single PuTTY
    session.
    
    Parameters
    ----------
    session_name : string
        The name of the PuTTY session as it appears in the Windows
        registry.
    color_list : list
        a list of RGB integer tuples
    
    See Also
    --------
    read_session_colors for more information on the color list format
    """

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
    """
    Get the name of all PuTTY sessions.
    
    Returns
    -------
    list
        a list of PuTTY session names, each in the form of a string
    """
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
    """
    Read PuTTY session colors from an INI file.
    
    The INI file needs to contain at least one section, called Colors
    (defined as COLOR_INI_SECTION_NAME). Each color defined by PuTTY
    needs to be represented in this INI section. The key for a
    particular color can be their registry names (e.g. Colour0,
    Colour1) or their names as shown in the PuTTY dialog (e.g.
    default foreground, default background).
    
    Parameters
    ----------
    ini_name : string
        the name of the INI file to read
    
    Returns
    -------
    list
        a list of RGB integer tuples
    
    Raises
    ------
    ValueError
        when a color isn't represented the INI section
    KeyError
        when the color INI section name isn't present in the INI file
    
    See Also
    --------
    read_session_colors for more information on the color list format
    """
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
            raise ValueError(('No value for {0} ({1}) found in {2} - using '
                              'the default value {3}').format(
                                  reg_color_name, color_name, ini_name,
                                  curr_color))
        color_list.append(curr_color)
    
    return color_list

def write_colors_to_INI(ini_name, colors_list, color_names=False):
    """
    Write a color list to a file.
    
    Parameters
    ----------
    ini_name : string
        the name of the file to which the color list will be written
    
    colors_list : list
        the list of integer tuples to write to file
    
    color_names : boolean, optional
        If set to True, the name given to the the color by PuTTY (i.e.
        the names in PUTTY_COLOR_ORDER will be used; otherwise, their
        registry names (e.g. Colour0, Colour1) will be used.
    
    Raises
    ------
    IOError
        when the file is not writable
    IndexError
        when there are more integer tuples in the color list than
        necessary
    
    See Also
    --------
    read_session_colors for more information on the color list format
    """
    color_config = configparser.SafeConfigParser()
    color_config.add_section(COLOR_INI_SECTION_NAME)
    
    for pos, color_val in enumerate(colors_list):
        ini_key = (PUTTY_COLOR_ORDER[pos] if color_names
                   else 'Colour{0}'.format(pos))
        color_str = pack_registry_colors(color_val)
        color_config[COLOR_INI_SECTION_NAME][ini_key] = color_str
        
    with open(ini_name, 'w') as config_file:
        color_config.write(config_file)

def main():
    print(read_colors_from_INI('solarized_dark.ini'))

if __name__ == '__main__':
    main()

