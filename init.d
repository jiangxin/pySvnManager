#! /bin/sh

### BEGIN INIT INFO
# Provides:          <my_app> application instance
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts instance of <my_app> app
# Description:       starts instance of <my app> app using start-stop-daemon
### END INIT INFO

############### EDIT ME ##################
# path to workingenv install if any
#PYTHONPATH=<path to pylons workingenv>/lib/python2.4

# path to app
APP_PATH=/opt/svnadmin

# path to paster bin
DAEMON=/usr/bin/paster

# log file name
LOG_FILE=$APP_PATH/run/paster.log

PID_FILE=$APP_PATH/run/paster.pid

# startup args
DAEMON_OPTS=" serve --monitor-restart --log-file $LOG_FILE production.ini"

# script name
NAME=svnadmin

# app name
DESC=pySvnManager

# pylons user
RUN_AS=www-data

############### END EDIT ME ##################

test -x $DAEMON || exit 0

set -e

case "$1" in
  start)
  	if [ -f "$PID_FILE" ]; then
		if [ -f "/proc/`cat $PID_FILE`/stat" ]; then
			echo "Daemon aleady started? pid: `cat $PID_FILE`"
			exit 1
		fi
	fi
        echo -n "Starting $DESC: "
        start-stop-daemon -c $RUN_AS -d $APP_PATH --start --background --pidfile $PID_FILE  --make-pidfile --exec $DAEMON -- $DAEMON_OPTS
        echo "$NAME."
        ;;
  stop)
        echo -n "Stopping $DESC: "
        start-stop-daemon --stop --pidfile $PID_FILE
        echo "$NAME."
        ;;

  restart|force-reload)
        echo -n "Restarting $DESC: "
        start-stop-daemon --stop --pidfile $PID_FILE
        sleep 1
        start-stop-daemon -d $APP_PATH -c $RUN_AS --start --background --pidfile $PID_FILE  --make-pidfile --exec $DAEMON -- $DAEMON_OPTS
        echo "$NAME."
        ;;
  *)
        N=/etc/init.d/$NAME
        echo "Usage: $N {start|stop|restart|force-reload}" >&2
        exit 1
        ;;
esac

exit 0

