/etc/console... keymap control = ...

? what is the default loadkeys

/etc/default/keyboard
setupcon --save -v
loadkeys




## regenerate locales

$ sudo locale-gen
$ sudo dpkg-reconfigure locales
