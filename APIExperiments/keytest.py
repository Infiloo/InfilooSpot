import LCD1602
from pynput import keyboard

cmd = ""

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    # print('{0} released'.format(key))
    global cmd
    if key == keyboard.Key.enter:
        # Stop listener so we can handle the collect cmd
        return False
    else:
    	if hasattr(key, 'char') == True:
    		cmd = cmd + str(key.char)

# Collect events until released
with keyboard.Listener(
        # on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

print("Result: " + cmd)
