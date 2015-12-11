title: 'Microsoft’s Natural Ergonomic Keyboard 4000 and its Zoom Slider'
published: 2015-12-11
tags: [linux, gentoo, keyboard]
refs:
    - '[Make the zoom slider of Microsoft Natural Ergonomic Keyboard 4000 and
      7000 scroll up and down, in 14.04
      (Trusty)](http://askubuntu.com/a/473823) (Ask Ubuntu)'

{% include 'gentoo-disclaimer.md' %}

If you are using Microsoft’s excellent [Natural Ergonomic Keyboard 4000][1]—at
least *one* product that Microsoft got right—under Linux, chances are that the
zoom slider in the middle of the keyboard does not work out of the box.  The
problem is that the zoom slider uses keycodes greater than 255, which the
evdev driver cannot handle.

[1]: https://www.microsoft.com/accessories/en-us/products/keyboards/natural-ergonomic-keyboard-4000/b2m-00012

Fortunately, you can use udev to remap the keys.  The default keyboard
mappings are contained in `/lib/udev/hwdb.d/60-keyboard.hwdb`, where you will
also find detailed documentation comments on the file format in the header,
including:

    # To update this file, create a new file
    #   /etc/udev/hwdb.d/70-keyboard.hwdb
    # and add your rules there. To load the new rules execute (as root):
    #   udevadm hwdb --update
    #   udevadm trigger /dev/input/eventXX
    # where /dev/input/eventXX is the keyboard in question. If in
    # doubt, simply use /dev/input/event* to reload all input rules.

You might even already find a section for the Natural Ergonomic Keyboard 4000
in this file.  If that is the case, copy its definition and use it as a
starting point for the new `/etc/udev/hwdb.d/70-keyboard.hwdb`.  If you want
the zoom slider keys to be mapped as “Page Up” and “Page Down” keys, use the
following:

    keyboard:usb:v045Ep00DB*
     KEYBOARD_KEY_c022d=pageup
     KEYBOARD_KEY_c022e=pagedown

Of course, you can map it to anything you like.  For example, to emulate a
mouse wheel scroll, you could define your custom mapping as:

    keyboard:usb:v045Ep00DB*
     KEYBOARD_KEY_c022d=scrollup
     KEYBOARD_KEY_c022e=scrolldown

This should result in Xorg receiving the zoom slider keys as `XF86ScrollUp`
and `XF86ScrollDown`.  Finally, make things work with [xdotool][2][^b151211a]
by binding those keys within your window manager to run `xdotool click 4`
(scroll up) and `xdotool click 5` (scroll down).

[2]: http://www.semicomplete.com/projects/xdotool/
[^b151211a]: Gentoo package [x11-misc/xdotool](https://packages.gentoo.org/packages/x11-misc/xdotool)
