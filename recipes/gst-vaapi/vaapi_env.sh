if lspci -v | grep -i vga | grep -i intel ; then
    if cat /proc/cpuinfo | grep -m 1 "cpu family" | grep -E '[1-9][0-9]+$' ; then
        export LIBVA_DRIVER_NAME=iHD
        rm -rf ~/.cache/gstreamer-1.0/ 
    else
        export LIBVA_DRIVER_NAME=i965
        rm -rf ~/.cache/gstreamer-1.0/
    fi
else
    if glxinfo | grep "OpenGL vendor string" | cut -f2 -d":" | xargs | grep -i X.Org ; then
        export LIBVA_DRIVER_NAME=radeonsi
        rm -rf ~/.cache/gstreamer-1.0/
    else 
        export LIBVA_DRIVER_NAME=fglrx
        rm -rf ~/.cache/gstreamer-1.0/
    fi
fi