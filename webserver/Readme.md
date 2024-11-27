Webserver Example
=================

This program runs a webserver. Requesting the main page triggers
a number of parallel requests (up to 5) with a total of 9 requests.

Main idea of this program is to test the implementation of
parallel requests handling and to gain insights into throughput
in this scenario.

After startup, the program prints an URL. You should copy this URL
into a browser with activated development tools, and deactivate
the browser cache.

Note: this program needs the module `ehttpserver`. Install it using

    circup install ehttpserver

Throughputs with various systems:

  - Pico-W (8.0.5 and 9.2.1): about 11s
  - Pico Plus2 W: about 11s
  - Adafruit Feather ESP32-S3 (4MB/2MB): about 1s
