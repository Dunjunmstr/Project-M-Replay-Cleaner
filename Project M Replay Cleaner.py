import os
import shutil
import subprocess
import time
from PIL import Image
from pydub import AudioSegment
from pydub.utils import audioop, ratio_to_db

DEBUG = 1

def analyzeStencil(baseDirectory, stencil):
    blackPixels = []
    whitePixels = []
    modifiers = ["Black", "White"]
    for color in modifiers:
        if color == "Black":
            pixelList = blackPixels
        else:
            pixelList = whitePixels
        stencilName = baseDirectory + color+ " " + stencil +".png" 
        imageFile = Image.open(stencilName)
        pixels = imageFile.load()
        (width, height) = imageFile.size
        for i in range (0, width):
            for j in range (0, height):
                if pixels[i,j][0] < 128: #might as well because potential blurriness
                    pixelList.append((i,j))
    return (blackPixels, whitePixels, width, height) 

def cacheStencil(stencilDirectory):
    baseDirectory = stencilDirectory
    stencils = {"Stencil 0":0, "Stencil 1":0, "Stencil 3":0, "Stencil 5":0, "Stencil 6":0, "Stencil 8":0}
    for stencil in stencils:
        stencils[stencil] = analyzeStencil(baseDirectory, stencil)
    return stencils

def compareStencil(blackStencilPixels, whiteStencilPixels, pictureDirectory):
    imageFile = Image.open(pictureDirectory)
    pixels = imageFile.load()
    for stencilPixel in blackStencilPixels:
        if pixels[stencilPixel[0], stencilPixel[1]][1] > 128:
            return False #All pixels in this need to have a black interior
    for stencilPixel in whiteStencilPixels:
        if pixels[stencilPixel[0], stencilPixel[1]][1] < 64:
            return False #All pixels in this need to have a white interior
    return True

def initBoundingBox():
    return [(429, 42), (444, 61)] #Basically coordinates detecting change

def makeMonochrome(picture):
    imageFile = Image.open(picture)
    pixels = imageFile.load()
    img = Image.new( 'RGB', imageFile.size, "black") # create a new black image
    newpixels = img.load() # create the pixel map
    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            imageTuple = pixels[i,j]
            if ((imageTuple[0] +imageTuple[1]+imageTuple[2])/3 > 128):
                newpixels[i,j] = (255, 255, 255) # set the colour accordingly
            else:
                newpixels[i,j] = (0, 0, 0) # set the colour accordingly
    img.save("Stencils/" + picture)

def compareBoxes(corners, initial, other): #Returns true if bounding boxes are the same in content
    initialPicture = Image.open(initial)
    initialPixels = initialPicture.load()
    otherPicture = Image.open(other)
    otherPixels = otherPicture.load()
    threshold = 25
    for i in range (corners[0][0], corners[1][0]):
        for j in range (corners[0][1], corners[1][1]):
            for k in range (0, len(initialPixels[i,j])):
                if abs(initialPixels[i,j][k] - otherPixels[i,j][k]) > threshold:
                    return False
    return True

def mushVideo(framesDirectory, matchName, startFrame, endFrame, ffmpegDirectory):
    corners = initBoundingBox()
    stencilDirectory = ffmpegDirectory + "Stencils\\"
    stencils = cacheStencil(stencilDirectory)
    uniqueImages = []
    imageDurations = []
    stencilNames = ["Stencil 0", "Stencil 1", "Stencil 3", "Stencil 5", "Stencil 6", "Stencil 8"]
    currentStencilIndex = 0
    previousStencilIndex = 0
    previousImage = ""
    previousNotFound = False
    for i in range (startFrame, endFrame):
        if i%300 == 0:
            print "We're now on image", i, "and our imageDuration has a sum of", sum(imageDurations), "while we have", len(uniqueImages), "unique images."
        previousStencilIndex = currentStencilIndex
        imageName = framesDirectory + matchName + ("0" * (6 - len(str(i))))+ str(i) + ".png"
        if (i == startFrame) or not compareBoxes(corners, previousImage, imageName):
            uniqueImages.append(i)
            foundMatch = False
            for numberOfFrames in range (0, 6): #Find the first stencil that matches
                currentStencilIndex = (currentStencilIndex-1)%6 #Switch stencil because this is not the first one
                blackStencil = stencils[stencilNames[currentStencilIndex]][0]
                whiteStencil = stencils[stencilNames[currentStencilIndex]][1]
                match = compareStencil(blackStencil, whiteStencil, imageName)
                # print "Stencil", currentStencilIndex, "has a match of", match, "with image", str(i)
                if match:
                    foundMatch = True
                    break
            if foundMatch == True:
                if (i != startFrame):
                    advanceFrames = (previousStencilIndex -currentStencilIndex - 1)%6 +1#Index 1 through 6 frames
                    if previousNotFound:
                        imageDurations[len(imageDurations)-1] += advanceFrames/2
                        advanceFrames = advanceFrames - advanceFrames/2
                        previousNotFound = False
                    if advanceFrames == 6:
                        print "Image", i, "supposedly takes 6 frames to transition to. Our hypothesis is that it's blurriness."
                        previousNotFound = True
                        currentStencilIndex = (currentStencilIndex - 1) % 6 #To be on the safe side, I guess. Usually 6 has trouble with detection, but best not to risk it.
                        imageDurations.append(1)
                    else:
                        imageDurations.append(advanceFrames) 
                # print currentStencilIndex, previousStencilIndex
            else:
                if (i != startFrame):
                    previousNotFound = True
                    currentStencilIndex = (currentStencilIndex - 1) % 6 #To be on the safe side, I guess. Usually 6 has trouble with detection, but best not to risk it.
                    imageDurations.append(1)
        else:
            print "We found a duplicate image: Image number ", i
        previousImage = imageName
    imageDurations.append(1) #For the last one, which has an undefined duration. Might as well give it 1 frame
    print "Done!"
    return (uniqueImages, imageDurations)

def setupVisual(matchName, startFrame, endFrame, framesDirectory, ffmpegDirectory):
    # framesDirectory = "C:\\Users\\***** ****\\Desktop\\Image project\\FFmpeg\\bin\\frames\\"
    # startFrame = 125
    # endFrame = 6601
    (uniqueImages, imageDurations) = mushVideo(framesDirectory, matchName, startFrame, endFrame, ffmpegDirectory)
    # return sum(imageDurations)
    if DEBUG:
        print uniqueImages
        print imageDurations
        time.sleep(1) #If there's an error, print out the list anyways
    frameNumber = 1
    for i in range (0, len(uniqueImages)):
        imageName = framesDirectory + matchName + ("0" * (6 - len(str(uniqueImages[i]))))+ str(uniqueImages[i]) + ".png"
        for j in range (0, imageDurations[i]):
            orderedImage= framesDirectory + matchName + ("0" * (6 - len(str(frameNumber))))+ str(frameNumber) + "c.png"
            shutil.copyfile(imageName, orderedImage)
            frameNumber += 1
    #All of the files are now in the frame directory. Return the number of frames to mush together.
    return frameNumber

def getLeftAudioSample(audioIndex):
    result = audioop.getsample(audioIndex._data, audioIndex.sample_width, 0)
    return result

def getRightAudioSample(audioIndex):
    result = audioop.getsample(audioIndex._data, audioIndex.sample_width, 1)
    return result



def msPassCheck(slop, millisecond, openedFile): #Check if a given millisecond has passed the 0 mark
    #It seems that for stereo files, left noise and right noise have different parities.
    #The odds of both passing the 0 line in a millisecond is relatively high.
    checkedMS = openedFile[millisecond]
    leftPosExist = False
    leftNegExist = False
    rightPosExist = False
    rightNegExist = False
    for i in range (1, openedFile.frame_rate/1000, slop): #In other words, checking each frame in MS
        if getLeftAudioSample(checkedMS.get_sample_slice(i, i+1)) > 0:
            leftPosExist = True
        elif getLeftAudioSample(checkedMS.get_sample_slice(i, i+1)) < 0:
            leftNegExist = True
        if getRightAudioSample(checkedMS.get_sample_slice(i, i+1)) > 0:
            rightPosExist = True
        elif getRightAudioSample(checkedMS.get_sample_slice(i, i+1)) < 0:
            rightNegExist = True
        if leftPosExist and leftNegExist and rightPosExist and rightNegExist:
            break
    return leftPosExist and leftNegExist and rightPosExist and rightNegExist

def getSegment(ourFile, startMS, endMS):
    start = int((ourFile.frame_rate * startMS)/1000)
    end = int((ourFile.frame_rate * endMS)/1000)
    return ourFile.get_sample_slice(start, end)
    

def deleteStutter(wavFile, actualLength, ffmpegDirectory, slop = 1, actualSlop = 1): #Match start and end are in ms
#NOTE: Slop < 1000 by necessity, actualSlop skips miliseconds
    #This will work as follows: First we take a segment of audio, and go through each sample. We find the longest
    #run of positives/negatives. For each such run, append only the first and last millisecond.
    AudioSegment.converter = ffmpegDirectory + "ffmpeg.exe"
    openedFile = AudioSegment.from_file(wavFile, format="wav")
    finalCombine = openedFile[0:0]
    currentTime = 0 # ms
    duration = len(openedFile)
    currentRun = 0
    exciseList = [] #This will take in all segments longer than 15 ms for assembly and excision afterwards.
    excisionSum = 0
    while currentTime < duration:
        if msPassCheck(slop, currentTime, openedFile):
            if currentRun > 15: #15 miliseconds
                exciseList.append((currentTime-currentRun, currentTime)) #Inclusive first, exclusive second
                excisionSum += currentRun
            currentRun =  0
        currentRun += actualSlop
        currentTime += actualSlop
        if (currentTime%1000 == 0) and (currentTime%slop == 0):
            print "We're on second", currentTime/1000
    #Now we assemble everything.
    toExcise = duration - actualLength
    leftovers = max(excisionSum - toExcise, 0)
    caps = float(leftovers)/(2*len(exciseList)) #How long each excision cap should be
    #Now we restart.
    currentTime = 0
    print "The amount of trash discovered is", excisionSum, ", the length of our excise list is", str(len(exciseList)),", the original total time was", duration, ", the actual length is", actualLength, "and the length per cap is", caps
    print exciseList
    for i in range(0, len(exciseList)):
        finalCombine = finalCombine + openedFile[currentTime: exciseList[i][0]] #First add the distance between the current time and the thing to be excised
        finalCombine = finalCombine + getSegment(openedFile, exciseList[i][0], exciseList[i][0] + caps) #Add the first cap
        finalCombine = finalCombine + getSegment(openedFile, exciseList[i][1] - caps, exciseList[i][1]) #Add the backwards cap
        currentTime = exciseList[i][1] #Onto the next segment
    #At this point we should be done with all excisions, and we just need to append the rest of the match on
    finalCombine = finalCombine + openedFile[currentTime:duration]
    return finalCombine

def makeWAV(matchName, matchFile, segmentStart, segmentEnd, matchStart, matchEnd, ffmpegDirectory, workFolder):
    if not os.path.isdir(workFolder):
        os.mkdir(workFolder)
        #This actually shouldn't happen

    # command = [ ffmpegDirectory +"\\ffmpeg.exe",
    #         '-i', matchFile,
    #         '-ss', matchEnd,
    #         '-to', segmentEnd,
    #         '-y', workFolder + matchName+'tail.wav']
    # subprocess.call(command)


    # command = [ ffmpegDirectory +"\\ffmpeg.exe",
    #         '-i', matchFile,
    #         '-ss', segmentStart,
    #         '-to', matchStart,
    #         '-y', workFolder + matchName+'head.wav']
    # subprocess.call(command)

    command = [ ffmpegDirectory +"\\ffmpeg.exe",
            '-i', matchFile,
            '-ss', matchStart,
            '-to', matchEnd,
            '-y', workFolder + matchName+'middle.wav']
    subprocess.call(command)

    #FFMpeg why

    # command = [ ffmpegDirectory +"\\ffmpeg.exe",
    #         '-i', matchFile,
    #         '-y', workFolder + matchName+'total.wav']
    # subprocess.call(command)

def getLength(filename):
    result = subprocess.Popen(["ffprobe", filename],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    durationString = [x for x in result.stdout.readlines() if "Duration" in x][0]
    startIndex = 0
    j = 0
    for i in range (0, len(durationString) - len("Duration: ")):#Scanning for duration
        if durationString[i:i + len("Duration: ")] == "Duration: ":
            startIndex = i + len("Duration: ")
            j = startIndex
            while durationString[j] != ",":
                j+= 1
    return durationString[startIndex:j]


def makeFrames(matchName, matchFile, segmentStart, segmentEnd, matchStart, matchEnd, ffmpegDirectory, workFolder):
    if not os.path.isdir(workFolder):
        os.mkdir(workFolder)
    command = [ ffmpegDirectory +"\\ffmpeg.exe",
            '-i', matchFile,
            '-ss', matchStart,
            '-to', matchEnd,
            '-y', workFolder + matchName + "%6d.png"]
    subprocess.call(command)


def combineFrames(matchName, ffmpegDirectory, workFolder):
    if not os.path.isdir(workFolder):
        os.mkdir(workFolder)
    #Here we run into a problem: We could convert both the pngs and wav simultaneously,
    #but most computers don't have that much memory, I think. There seems to be a problem
    #regarding adding audio losslessly into mp4s, and attempting to add it to a .ts file 
    #glitches things up. So we're going to add audio lossily to an mp4, then convert to .ts
    #with the .ts able to do lossless concatenation.
    command = [ ffmpegDirectory +"\\ffmpeg.exe",
            '-thread_queue_size', '102400',
            '-framerate', '60',
            '-start_number', '1',
            '-i', workFolder + matchName + "%6dc.png", #
            # '-i', workFolder + matchName + "middleAudio.wav",
            # '-acodec', 'copy',
            '-preset', 'slow', 
            '-y', workFolder + matchName + 'middle' + '.mp4']
    subprocess.call(command)

    #The above turns pngs into mp4.
    
    command = [ ffmpegDirectory +"\\ffmpeg.exe",
            '-thread_queue_size', '1024',
            '-i', workFolder + matchName + 'middle' + '.mp4',
            '-i', workFolder + matchName + "audio.wav",
            # '-c', 'copy', 
            # '-acodec', 'copy', #I have no idea how to make this work
            # '-preset', 'slow', 
            '-y', workFolder + matchName + 'middlesound' + '.mp4']
    subprocess.call(command)

    # #The above then turns mp4s into mp4s with sound

    # command = [ ffmpegDirectory +"\\ffmpeg.exe",
    #         '-thread_queue_size', '1024',
    #         '-i', workFolder + matchName + 'middlesound' + '.mpg',
    #         # '-i', workFolder + matchName + "middleAudio.wav",
    #         '-c', 'copy',
    #         "-bsf:v", "h264_mp4toannexb",
    #         '-f', 'mpegts',
    #         '-y', workFolder + matchName + 'middle' + '.ts']

    # subprocess.call(command)

    #And finally we get a .ts file.


    command = [ffmpegDirectory +"\\ffmpeg.exe",
        '-i', 'concat:' + workFolder + matchName + 'head' + '.mp4|' + workFolder + matchName + 'middlesound' + '.mp4|'  + workFolder + matchName + 'tail' + '.mp4',
        '-c', 'copy', '-y', workFolder + matchName + '.mp4']
    subprocess.call(command)

    #This should be it.

    # command = [ ffmpegDirectory +"\\ffmpeg.exe",
    #         '-thread_queue_size', '1024',
    #         '-i', workFolder + matchName + 'middle' + '.ts',
    #         '-i', workFolder + matchName + "middleAudio.wav",
    #         # "-map 0:0", "-map 1:0",
    #         '-vcodec', 'copy',
    #         '-acodec', 'copy',
    #         "-shortest",
    #         '-y', workFolder + matchName + 'middle2' + '.ts']

    # subprocess.call(command)

    #The above was an attempt to add the sound while converting to a .ts.
    #It failed.

    #Ignore the above. We have chosen to turn everything into a png file, merge them, then apply audio.
    # totalNumber = 1
    # matchNumber = 1
    # notFound = True
    # while notFound:
    #     fileName = workFolder + matchName + ("0" * (6 - len(str(matchNumber))))+ str(matchNumber) + "head.png"
    #     if os.path.isfile(fileName):
    #         newFileName = workFolder + matchName + ("0" * (6 - len(str(totalNumber))))+ str(totalNumber) + "final.png"
    #         os.rename(fileName, newFileName)
    #         totalNumber += 1
    #         matchNumber += 1
    #     else:
    #         notFound = False

    # matchNumber = 1
    # notFound = True
    # while notFound:
    #     fileName = workFolder + matchName + ("0" * (6 - len(str(matchNumber))))+ str(matchNumber) + "c.png"
    #     if os.path.isfile(fileName):
    #         newFileName = workFolder + matchName + ("0" * (6 - len(str(totalNumber))))+ str(totalNumber) + "final.png"
    #         os.rename(fileName, newFileName)
    #         totalNumber += 1
    #         matchNumber += 1
    #     else:
    #         notFound = False

    # matchNumber = 1
    # notFound = True
    # while notFound:
    #     fileName = workFolder + matchName + ("0" * (6 - len(str(matchNumber))))+ str(matchNumber) + "tail.png"
    #     if os.path.isfile(fileName):
    #         newFileName = workFolder + matchName + ("0" * (6 - len(str(totalNumber))))+ str(totalNumber) + "final.png"
    #         os.rename(fileName, newFileName)
    #         totalNumber += 1
    #         matchNumber += 1
    #     else:
    #         notFound = False

    # command = [ ffmpegDirectory +"\\ffmpeg.exe",
    #         '-thread_queue_size', '102400',
    #         '-framerate', '60',
    #         '-start_number', '1',
    #         '-i', workFolder + matchName + '%6dfinal.png',
    #         # '-i', workFolder + matchName + "%5d.png", #+ "c"
    #         # '-i', workFolder + matchName + "middleAudio.wav",
    #         # '-acodec', 'copy',
    #         '-vcodec', 'libx264', 
    #         '-preset', 'slow', 
    #         '-y', workFolder + matchName + 'audioless' + '.mp4']
    # # subprocess.call(command)

    # command = [ ffmpegDirectory +"\\ffmpeg.exe",
    #         '-thread_queue_size', '1024',
    #         '-i', workFolder + matchName + 'audioless' + '.mp4',
    #         '-i', workFolder + matchName + "audio.wav",
    #         '-c', 'copy', 
    #         # '-acodec', 'copy', #I have no idea how to make this work
    #         # '-preset', 'slow', 
    #         '-y', workFolder + matchName + '.mp4']
    # subprocess.call(command)

    #And now we have a working file; we're done. Huzzah.
    



def makeEnds(matchName, matchFile, segmentStart, segmentEnd, matchStart, matchEnd, ffmpegDirectory, workFolder):
    if not os.path.isdir(workFolder):
        os.mkdir(workFolder)
        #This actually shouldn't happen
    command = [ ffmpegDirectory +"\\ffmpeg.exe",
            '-thread_queue_size', '1024',
            '-i', matchFile,
            '-ss', matchEnd,
            '-to', segmentEnd,
            '-y',
            workFolder+ matchName + 'tail' +'.mp4']
    subprocess.call(command)
    command = [ ffmpegDirectory +"\\ffmpeg.exe",
            '-thread_queue_size', '1024',
            '-i', matchFile,
            '-ss', segmentStart,
            '-to', matchStart,
            '-y',
            workFolder + matchName + 'head' +'.mp4']
    subprocess.call(command)


def findLastFrame(matchName, workFolder):
    #Doing this just in case because apparently some files have variable framerate.
    i = 1
    while True:
        if not os.path.isfile(workFolder + matchName + ("0" * (6 - len(str(i))))+ str(i) + ".png"):
            return i-1
        i+= 1

def main(matchName, matchFile, segmentStart, segmentEnd, matchStart, matchEnd, ffmpegDirectory, slop = 1, actualSlop = 1):
    matchStart = str(matchStart)
    matchEnd = str(matchEnd)
    segmentStart = str(segmentStart)
    segmentEnd = str(segmentEnd)
    workFolder = ffmpegDirectory + 'WorkFolder\\' #Delete this at the end
    makeFrames(matchName, matchFile, segmentStart, segmentEnd, matchStart, matchEnd, ffmpegDirectory, workFolder)
    makeWAV(matchName, matchFile, segmentStart, segmentEnd, matchStart, matchEnd, ffmpegDirectory, workFolder)
    totalLength = getLength(matchFile)
    makeEnds(matchName, matchFile, segmentStart, segmentEnd, matchStart, matchEnd, ffmpegDirectory, workFolder)
    lastFrame = findLastFrame(matchName, workFolder)
    #We now have the header and tail of the match as well as the middle's frames and wav.
    #This is what we'll do: First we doctor frames until we get an audioless video.
    #Then we'll use the length of the video to make an appropriate-length wav file.
    actualLength = setupVisual(matchName, 1, lastFrame, workFolder, ffmpegDirectory)
    actualLength = (actualLength*1000)/60 #We're working in milliseconds now
    wavFile = workFolder + matchName+'middle.wav'
    stutterlessAudio = deleteStutter(wavFile, actualLength, ffmpegDirectory, slop, actualSlop)
    stutterlessAudio.export(workFolder + matchName + "audio.wav", format="wav");
    #Make video from matchStart to matchEnd into PNGs, keep a counter
    #Make video of 0 to matchStart and totalLength to matchEnd
    # matchVideo = mushVideo(frames)
    #add 1st video to matchVideo to end video
    #Slap the wav file onto the mp4, export it

    #Now we just have to combine the head, middle, and tail, and we're done.
    combineFrames(matchName, ffmpegDirectory, workFolder)
    print "Done!"
    return 0




matchFile = "FFmpeg\\bin\\2015-07-02-1429-19.flv"
workFolder = "FFmpeg\\bin\\test\\"
ffmpegDirectory = "FFmpeg\\bin\\"
workFolder = "FFmpeg\\bin\\WorkFolder\\"
# command = [ffmpegDirectory +"\\ffmpeg.exe",
#         '-i', 'concat:' + workFolder + "Testingourstuff" + 'head' + '.ts|' + workFolder + "Testingourstuff" + 'tail' + '.ts',
#         '-c', 'copy', '-bsf:a', 'aac_adtstoasc', '-y', workFolder + "Testingourstuff" + '.mp4']

# subprocess.call(command)

# main("Testingourstuff", matchFile, 606, 876, 612, 872, ffmpegDirectory)

matchName = "Testingourstuff"
command = [ffmpegDirectory +"\\ffmpeg.exe",
    '-i', 'concat:' + workFolder + matchName + 'head' + '.mp4|' + workFolder + matchName + 'middlesound' + '.mp4|'  + workFolder + matchName + 'tail' + '.mp4',
    '-c', 'copy', '-y', workFolder + matchName + '.mp4']
subprocess.call(command)
