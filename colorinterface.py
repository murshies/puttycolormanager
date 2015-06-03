
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

def unpackRegistryColor(regValue):
    '''Given the value of a color read from the registry, return a list of
    integers of the RGB values. "regValue" will be a tuple of 2 items,
    containing the value of the registry item (a string in our case), and an
    integer representing the item type (1 in our case). The colors in the
    registry are comma-separated (e.g. 255,255,255).'''
    return unpackColor(regValue[0])

def unpackColor(colorVal):
    '''Given a color in the form of a comma-separated RGB string, return a
    tuple of integers. Whitspace is allowed between integers.'''
    return tuple([int(x.strip()) for x in colorVal.split(',')])

def packRegistryColors(colorList):
    '''Converts a color in the form of an RGB list of integers into the format
    expected by PuTTY (a comma-separated list of integers in the form of a
    string).'''
    return ','.join([str(x) for x in colorList])

def readSessionColors(sessionName):
    '''Read all of the color values for the PuTTY session with name
    "sessionName".'''
    fullSessionName = BASE_PUTTY_PATH + sessionName
    colorsList = []
    
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         fullSessionName) as session:
        for colorNumber in range(len(PUTTY_COLOR_ORDER)):
            regColorName = 'Colour{0}'.format(colorNumber)
            regValue = winreg.QueryValueEx(session, regColorName)
            colors = unpackRegistryColor(regValue)
            colorsList.append(colors)
    
    return colorsList

def writeSessionColors(sessionName, colorList):
    '''Given the name of a session "sessionName" and a list of RGB integer
    lists, set colorList as the colors for sessionName.'''
    fullSessionName = BASE_PUTTY_PATH + sessionName
    
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, fullSessionName,
                         WINDOWS_RESERVED, winreg.KEY_WRITE) as session:
        for colorNumber, colorVal in enumerate(colorList):
            regColorName = 'Colour{0}'.format(colorNumber)
            packedColor = packRegistryColors(colorVal)
            winreg.SetValueEx(session, regColorName, WINDOWS_RESERVED,
                               PUTTY_REG_COLOR_TYPE, packedColor)

def getAllSessionNames():
    '''Get the name of all PuTTY sessions.'''
    sessionNames = []
    
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, BASE_PUTTY_PATH) as base:
        try:
            i = 0
            while True:
                sessionNames.append(winreg.EnumKey(base, i))
                i += 1
        except WindowsError:
            pass
    
    return sessionNames

def readColorsFromINI(iniName):
    '''Given the name of an INI file "iniName", create a list of RGB tuples
    containing the colors found in iniName.'''
    colorConfig = configparser.SafeConfigParser()
    colorConfig.read(iniName)
    colorDict = colorConfig[COLOR_INI_SECTION_NAME]
    colorList = []
    
    for colorNumber, colorName in enumerate(PUTTY_COLOR_ORDER):
        regColorName = 'Colour{0}'.format(colorNumber)
        currColor = PUTTY_DEFAULT_COLORS[colorNumber]
        if regColorName in colorDict:
            currColor = unpackColor(colorDict[regColorName])
        elif colorName in colorDict:
            currColor = unpackColor(colorDict[colorName])
        else:
            logging.warning(('No value for {0} ({1}) found in {2} - using the '
                            'default value {3}').format(
                                regColorName, colorName, iniName, currColor))
        colorList.append(currColor)
    
    return colorList

def main():
    print(readColorsFromINI('solarized_dark.ini'))

if __name__ == '__main__':
    main()

