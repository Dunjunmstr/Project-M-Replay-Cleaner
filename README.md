# Project-M-Replay-Cleaner
Removes audiovisual lag from replays of Project M

A brief synopsis of this project: In the Fall 2014 - Spring 2015 semesters, I made the mistake of overloading on courses and failed to set up my summer properly with an internship. I decided to take a break and prep for the GREs at my leisure, but slacked off for a bit and played a videogame (Project M, a mod of Super Smash Brothers Brawl) with a friend for a good part of the first half. I'm a terrible hoarder so I kept videos of our matches, but due to mediocre laptop specs all of the matches were laggy regardless of quality. To remedy this, this program, which I dub to be the "Project M Replay Cleaner", was created in an effort to make the replays viewable.

There are a few caveats to this, however:
1. This was never intended for the eyes of the general public, and is only being uploaded for purposes of a code sample. 
2. Although this is my most recent non-trivial non-commercial project with a substantial amount of code written, it was still written in the first half of Summer 2015, which was before I picked up any actual Software Engineering internships. As such, many of the coding practices featured here are no longer/were never endorsed by me (in particular mushing everything into one file, not raising errors, and having arbitrary variable names), and I can assure the reader that my coding abilities have improved significantly.
3. This project was put on hiatus after I got my first internship, and subsequently dropped after Moore's Law proved to more powerful than I expected and I got a new laptop.

90% of the code has not been edited for viewability (only a few questionable lines of comments and code as well as a significant amount of dead code were removed); please tread at your own risk.

Comments:
1. Obviously there's no UI yet. I was in the middle of doing this when I received a phone call indicating that I had received an internship offer.
2. The preprocessing time and memory used is absolutely horrendous (Nearly 8 GB and 35 minutes spent for 4 minutes, and roughly an hour for processing). Furthermore there is no cleanup (since it was still in a testing state).
3. This has several dependencies, in particular PIL, SciPy, and Pydub. It also relies heavily on ffmpeg.
4. The code only works for the timestamps already in here. This can be attributed to the lack of stencils made.
5. The results of this project can be viewed on my resume.
6. This project took roughly a week judging by the modify times (7-2-15 to 7-9-15), most of which was spent wrangling with ffmpeg.
7. Optimally the result would be high quality but there were some issues setting up video codecs.
8. I'm not too sure why, but for some reason the final ffmpeg call fails. This isn't too big of an issue though, since "Testingourstuffmiddlesound.mp4" contains the bulk of the video if run with the current parameters.
9. I don't think this project can be extended to much else, but for completeness:

Copyright by J**** C***, 2015 Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php