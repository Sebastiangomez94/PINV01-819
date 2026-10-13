
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++YOU MUST ADD OR OVERWRITE THE "etc" FOLDER ON THE PIXHAWK SD ROOT+++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

There are two scripts here for specific tasks:

-etc/logging/logger_topics.txt : Here are the defined topics for logging and its rates

-etc/extras.txt: Here is the customized mavlink request to increase the ATTITUDE_TARGET topic sending rate to TELEM2 port for usage on AIA control though a Rasperry Pi or any device capable of MAVLINK messaging


READ THESE LINKS IF YOU NEED TO ADD OR MODIFIY ANY FILE RELATED TO PX4 BOOT CUSTOMIZATION, MAVLINK MESSAGING RATE CUSTOMIZATION OR PX4 LOGGING CUSTOMIZATION:


Pixhawk Cube dev/tty ports:

https://docs.px4.io/main/en/flight_controller/cubepilot_cube_orange.html


Pixhawk Cube dev/tty ports:

https://docs.px4.io/main/en/flight_controller/cubepilot_cube_orange.html

https://www.mathworks.com/help/uav/px4/ref/serial-port-names-labels-px4.html

Stablish the logged topics on the sdcard and logging rates:

https://docs.px4.io/v1.12/en/dev_log/logging.html

Increase the speed of mavlink stream of a specific mavlink topic:

https://github.com/mavlink/mavros/issues/305




