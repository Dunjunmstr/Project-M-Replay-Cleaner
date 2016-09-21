# Project-M-Replay-Cleaner
Removes audiovisual lag from replays of Project M

Status: Project dropped due to Moore's Law making it obsolete.

To do:
1. Move the audio processing and the video processing to separate files
2. Create a proper user interface
3. Fix the stencils to be more robust, and make more stencils. As it stands the stencils only work for the timestamps provided.
4. Confirm why the final FFMpeg call fails.
5. Cut down on the preprocessing time and memory spent (Nearly 8 GB and 35 minutes spent for 4 minutes of video)
6. Figure out why ffmpeg won't make the video lossless and set up the video codecs for this.
7. Make proper variable names.


Time spent: 7-2-15 to 7-9-15 (Most of this time was spent wrangling with ffmpeg)
Dependencies: PIL, Pydub

Note: This project was never intended for the eyes of the general public. 90% of the code has not been edited for viewability (only a few questionable lines of comments and dead code were removed); please tread at your own risk.

Copyright by J**** C***, 2015 Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
