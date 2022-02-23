# Dead simple vsftpd server for single user

This image contains vsftpd server configured with only one user whose name is
set during build (defaults to `deepcore`) time using the docker build arg 
`USER_NAME` with a corresponding volume `/home/USER_NAME`. Password is set from the
`USER_PASS` env variable or left empty if not provided.

Example usage:

    $ docker run -it --rm  -v ${PWD}/Tools:/home/deepcore \
    -e FTP_USER_NAME="aivero" -e USER_PASS="somepass" -v FTP_USER_HOME=/deepcore -p 2121:21 -p 10090-10100:10090-10100 \
    ghcr.io/aivero/docker-alpine-vsftpd:3.8-run

    $ docker run -it --rm  -v ${PWD}/Tools:/home/deepcore \
    -p 2121:21 -p 10090-10100:10090-10100 \
    ghcr.io/aivero/docker-alpine-vsftpd:3.8-run
