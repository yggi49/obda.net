title: Install Windows 10 on a Linux Laptop
published: 2020-04-04
tags: [windows, installation, dual-boot]

Believe it or not, recently I was tasked with turning a Linux laptop into a
dual-boot machine with Windows 10.  How hard can it be?  Download the
ISO image, put it on a bootable USB flash drive, install it, and fix the boot
loader afterwards.  You would think.

Turns out, one of the first things that Windows setup will tell you after
booting from the USB drive is <q>A media driver your computer needs is
missing.</q>  A search on the Internet quickly reveals that other people
[experienced][1] [this problem][2] [as well][3], and it seems that it is
something that exists at least [since Windows 7][4].

The only working solutions seemed to include either an external DVD drive, or
unplugging and re-inserting the USB drive into a different port.  In my case,
neither was successful; the ISO image was too large to be burnt to a DVD, and
switching USB ports apparently only works with USB 2 ports, which my laptop
was not equipped with.  After a lot of trial-and-error, cursing, as well as a
few more hours of research, I finally succeeded.

[1]: https://answers.microsoft.com/en-us/windows/forum/all/windows-10-clean-install-a-media-driver-is-missing/16982d42-bd5c-4545-8e84-618b80cb8431
[2]: https://answers.microsoft.com/en-us/windows/forum/windows_10-windows_install/windows-10-clean-install-a-media-driver-your/3068a127-f088-44a2-af36-ba90a1604855
[3]: https://www.tenforums.com/installation-upgrade/73386-windows-10-clean-install-missing-media-driver.html
[4]: https://superuser.com/questions/279359/windows-7-fresh-install-missing-cd-dvd-media-drivers


### Prerequisites

You will need *two* empty USB flash drives, with at least 8 GiB capacity each.
I will also assume that you have already downloaded a Windows 10 disc image
from [Microsoft’s Software Download Windows 10 page][5] and stored it in your
home directory as `win10.iso`.  Finally, I will assume that you have some
unallocated space on your hard drive to install Windows into.  If you don’t,
use a tool such as *gparted*.

[5]: https://www.microsoft.com/software-download/windows10


### Prepare the USB Flash Drives

The first step is the most obvious one: put the ISO image on one of the
USB drives as you normally would using *dd*.  For example, if your USB drive
is located at `/dev/sdb`, execute:

    :::console
    user@host:~$ dd if=win10.iso of=/dev/sdb bs=4M

For the second USB drive (I will assume that it is located at `/dev/sdc`),
copy the *contents* of the ISO image onto it.  To do this, start off by using
*fdisk* to create an NTFS partiton on the drive.

    :::console
    user@host:~$ sudo fdisk /dev/sdc

    Welcome to fdisk (util-linux 2.31.1).
    Changes will remain in memory only, until you decide to write them.
    Be careful before using the write command.


    Command (m for help):

First, enter <kbd>o</kbd> and press <kbd>Enter ↩</kbd> to create a new DOS
partition table:

    Command (m for help): o
    Created a new DOS disklabel with disk identifier 0xdeadbeef.

Next, create a new primary partition with <kbd>n</kbd>.  Go with the proposed
defaults; when asked for the size, enter `+8G` for an 8 GiB partition:

    Command (m for help): n
    Partition type
       p   primary (0 primary, 0 extended, 4 free)
       e   extended (container for logical partitions)
    Select (default p):

    Using default response p.
    Partition number (1-4, default 1):
    First sector (2048-95737, default 2048):
    Last sector, +sectors or +size{K,M,G,T,P} (2048-95737, default 95737): +8G

    Created a new partition 1 of type 'Linux' and of size 8 GiB.

Then, change the new partition’s type to NTFS; enter <kbd>t</kbd> and choose
hex code `7`:

    Command (m for help): t
    Selected partition 1
    Hex code (type L to list all codes): 7
    Changed type of partition 'Linux' to 'HPFS/NTFS/exFAT'.

Finally, enter <kbd>w</kbd> to write all changes to the USB drive and quit
fdisk:

    Command (m for help): w
    The partition table has been altered.
    Calling ioctl() to re-read partition table.
    Syncing disks.

Next, format the newly created partition:

    :::console
    user@host:~$ sudo mkfs.ntfs /dev/sdc1
    Cluster size has been automatically set to 4096 bytes.
    Initializing device with zeroes: 100% - Done.
    Creating NTFS volume structures.
    mkntfs completed successfully. Have a nice day.

Now mount the USB drive as well as the ISO image, and copy everything from the
image onto the drive:

    :::console
    user@host:~$ sudo mkdir /mnt/{usb,iso}
    user@host:~$ sudo mount /dev/sdc1 /mnt/usb
    user@host:~$ sudo mount -o loop ~/win10.iso /mnt/iso
    user@host:~$ sudo cp -r /mnt/iso/* /mnt/usb
    user@host:~$ sudo umount /mnt/{usb,iso}

Once the *umount* command has finished, you can safely unplug the second
USB drive.


### Boot From the First USB Flash Drive

Now it is time to reboot from the *first* USB drive (the one that was created
with *dd*).  Unfortunately, this might not be as straightforward as it sounds,
either.  If your system refuses to boot from the USB drive and always loads
the GRUB boot menu, you can drop into a GRUB command line by pressing
<kbd>c</kbd> and trigger booting from the USB drive manually.

First, ask GRUB to list all partitions on all drives:

    grub> ls
    (hd0) (hd1) (hd1,gpt3) (hd1,gpt2) (hd1,gpt1)

Typically, your USB drive is the one without a separate partition; in this
case, the device would be `(hd0)`.  Next, you need to find out the partition’s
UUID.  Run `ls` again, but add the device as an argument this time:

    grub> ls (hd0)
    Device hd0: Filesystem type udf [...] UUID 1234567890abcdef [...]

Jot down the UUID, you will need it in a few moments.  Now, you must load some
additional GRUB modules before you can continue:

    grub> insmod part_gpt
    grub> insmod ntfs
    grub> insmod search_fs_uuid
    grub> insmod chain

Afterwards, you can set the root file system using the UUID determined above
and select the EFI file to boot from:

    grub> search --fs-uuid --set=root 1234567890abcdef
    grub> chainloader /efi/boot/bootx64.efi
    /EndEntire
    file path: [...]/File(\efi\boot)/File(bootx64.efi)/EndEntire

At long last, you can now boot from the drive:

    grub> boot

This will boot the USB drive, and you should be greeted by the Windows setup
welcome screen after a few moments.


### Install Windows

Now the *second* USB flash drive you created comes into play.  After you have
selected your region and language, plug the drive into a free USB port and
click the *“Install now”* button.  Windows setup should now be able to access
the second USB drive for the “missing drivers” it used to complain about, and
you can proceed with installing Windows into the unallocated space on your
hard drive.


### Re-Enable GRUB

After the Windows installation has finished, you will find out that you are no
longer able to boot into Linux.  To end up with our target dual-boot system,
you first need to restore GRUB as your boot loader, and finally reconfigure it
from Linux to add a Windows entry.

From the Windows menu, search for the *Command Prompt* terminal application,
and right-click it to run it as administrator.  In the terminal, enter the
following command:

    :::console
    C:\WINDOWS\system32>bcdedit /set {bootmgr} path \EFI\manjaro\grubx64.efi

If you are using a Linux distribution other than Manjaro, e.g., Ubuntu, edit
the path accordingly.  If in doubt, just look up the correct path in Windows
Explorer; it is located at the root of a hard disk drive other than *C:*.—Be
careful to get this right!

Afterwards, reboot your system.  You should see the GRUB menu again and be
able to boot into your Linux system.


### Reconfigure GRUB

Finally, you need to reconfigure GRUB, so that Windows shows up in its boot
menu.  This last step is by far the easiest:

    :::console
    user@host:~$ sudo update-grub

If you did not modify GRUB’s configuration previously, this should
automatically detect the new Windows installation as an additional system, and
there is nothing else to do.

That’s it—reboot the laptop to make sure that everything works as intended,
and then open a beverage of your choice to celebrate!
