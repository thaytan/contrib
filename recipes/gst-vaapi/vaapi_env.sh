if lspci -v | grep -i vga | grep -i intel ; then
    export LIBVA_DRIVER_NAME=iHD
    rm -rf ~/.cache/gstreamer-1.0/ 

    if glxinfo | grep "OpenGL vendor string" | cut -f2 -d":" | xargs | grep -i X.Org ; then
        export LIBVA_DRIVER_NAME=radeonsi
        rm -rf ~/.cache/gstreamer-1.0/
    else 
        export LIBVA_DRIVER_NAME=fglrx
        rm -rf ~/.cache/gstreamer-1.0/
    fi
fi