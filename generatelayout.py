#WHAT YOU NEED TO DO TO RUN THIS
#Fill in the file path to point to the folder with the script in it (see line 16 of the script, must be done in the script file)
#Put all the layout txt AND xml files in the "layout txts" folder 
#Put all the ship image files in the "layout images" folder
#Have the autoBlueprints.xml.append file
#Make sure the base door and room files (comes in the script folder) exist and have the right folder path ("rooms" folder)
#Make sure the base system files (comes in the script folder) exist and have the right folder path ("icons" folder)
#All of these files/folder should be in the same location as the script

#Created by Basic Person
import os
import re
from PIL import Image

#TODO PUT PATH HERE
os.chdir("NEED FILE PATH")

class Room:
    def __init__(self, id, x, y, l, h):
        self.id = id
        self.x = x
        self.y = y
        self.l = l
        self.h = h

class Door:
    def __init__(self, x, y, room1, room2, rotate):
        self.x = x
        self.y = y
        self.room1 = room1
        self.room2 = room2
        self.rotate = rotate

class System:
    def __init__(self, name, room, start):
        temproom = re.findall(r'\d+', room)
        if "true" in start:
            self.start = True
        if "false" in start:
            self.start = False
        self.name = name.lstrip("<")
        self.room = int(temproom[0])

class Ship:
    def __init__(self, name, layout, img):
        self.layout = layout[8:-1]
        self.img = "layout images/" + img[5:-2] + "_base.png"
        self.name = name[6:-1]


autoList = []
autoPath = "autoBlueprints.xml.append"

#read auto file
with open(autoPath, 'r', encoding="utf-8") as f:
    for x in f:
        x = x.rstrip('\n')
        x = x.lstrip()
        autoList.append(x)

#go through auto file and remove comments
goodAutoList = []
comment = False

for line in autoList:
    while True:
        if comment == False:
            start = line.find("<!--")
            if start == -1:
                goodAutoList.append(line)
                break
            else:
                end = line.find("-->", start + 4)
                if end == -1:
                    line = line[:start]
                    comment = True
                    break
                else:
                    line = line[:start] + line[end + 3:]
        else:
            end = line.find("-->")
            if end == -1:
                line = ""
                break
            else:
                line = line[end + 3:]
                comment = False
autoList = goodAutoList

#read through the autofile for info
for line in autoList:
    #first line need info
    if "<shipBlueprint" in line:
        counter = 0
        roomList = []
        doorList = []
        tileList = []
        xmlList = []
        systemClassList = []
        skip = False
        for line2 in autoList[autoList.index(line):]:
            counter += 1
            if "</shipBlueprint>" in line2:
                shipList = autoList[autoList.index(line):autoList.index(line) + counter]

        shipInfo = shipList[0].split()
        ship = Ship(shipInfo[1], shipInfo[2], shipInfo[3])
        print(ship.name)

        #read layout file
        filePath = "layout txts/" + ship.layout + ".txt"
        with open(filePath, 'r') as f:
            for x in f:
                x = x.rstrip('\n')
                tileList.append(x)


        #create room classes
        for num, line in enumerate(tileList):
            if line == "ROOM":
                r = tileList[num+1:num+6]
                r = list(map(int, r))
                room = Room(r[0], r[1], r[2], r[3], r[4])
                roomList.append(room)
            if line == "DOOR":
                d = tileList[num+1:num+6]
                d = list(map(int, d))
                door = Door(d[0], d[1], d[2], d[3], d[4])
                doorList.append(door)
        

        #find the dimensions
        #tile size 35x35
        xmax = 0
        ymax = 0
        for room in roomList:
            xam = room.x + room.l
            yam = room.y + room.h
            if xam > xmax:
                xmax = xam
            if yam > ymax:
                ymax = yam

        canvas = Image.new('RGBA', (xmax * 35, ymax * 35))


        #generate the ship layout
        for room in roomList:
            realy = room.y * 35
            realx = room.x * 35
            file = str(room.l) + "x" + str(room.h) + ".png"
            image = Image.open("rooms/" + file).convert('RGBA')
            canvas.paste(image, (realx, realy), mask=image)


        #generate the doors
        for door in doorList:
            if door.rotate == 0:
                file = "rooms/horidoor.png"
                rx = -2
                ry = 3
            if door.rotate == 1:
                file = "rooms/vertidoor.png"
                rx = 3
                ry = -2
            realy = door.y * 35 - ry
            realx = door.x * 35 - rx
            image = Image.open(file).convert('RGBA')
            canvas.paste(image, (realx, realy), mask=image)


        #add systems
        for line2 in shipList:
            if "<systemList>" in line2:
                sys1 = shipList.index(line2)
            if "</systemList>" in line2:
                sys2 = shipList.index(line2)
        systemList = shipList[sys1 + 1:sys2]

        for line2 in systemList:
            #still breaks when there is a space for some reason
            if "</systemList>" in line2:
                continue
            if len(line2) == 0:
                continue
            sl = line2.split()
            print(sl)
            if len(sl) == 4:
                sl.append("true")
            system = System(sl[0], sl[3], sl[4])
            systemClassList.append(system)


        for i in roomList:
            for system in systemClassList:
                file = "icons/" + system.name + ".png"
                image = Image.open(file).convert('RGBA')

                if system.start == False:
                    rc, gc, bc, ac = image.split()
                    rc = rc.point(lambda p: int(p*20))
                    image = Image.merge('RGBA', (rc, gc, bc, ac))

                if i.id == system.room:

                    #for if medical and clonebay in the same room
                    if system.name == "clonebay":
                        for m in systemClassList:
                            if m.name == "medbay" and m.room == system.room:
                                #if the room is less than 2 width
                                if i.l == 1:
                                    xcord = round(i.x * 35 + ((35 * i.l)/2)) - 16
                                    ycord = round(i.y * 35 + ((35 * i.h/2))) - 4
                                else:
                                    xcord = round(i.x * 35 + ((35 * i.l)/2)) - 4
                                    ycord = round(i.y * 35 + ((35 * i.h/2))) - 16
                                break
                            else:
                                xcord = round(i.x * 35 + ((35 * i.l)/2)) - 16
                                ycord = round(i.y * 35 + ((35 * i.h/2))) - 16
                    elif system.name == "medbay":
                        for m in systemClassList:
                            if m.name == "clonebay" and m.room == system.room:
                                if i.l == 1:
                                    xcord = round(i.x * 35 + ((35 * i.l)/2)) - 16
                                    ycord = round(i.y * 35 + ((35 * i.h/2))) - 28
                                else:
                                    xcord = round(i.x * 35 + ((35 * i.l)/2)) - 28
                                    ycord = round(i.y * 35 + ((35 * i.h/2))) - 16
                                break
                            else:
                                xcord = round(i.x * 35 + ((35 * i.l)/2)) - 16
                                ycord = round(i.y * 35 + ((35 * i.h/2))) - 16
                    
                    #otherwise      
                    else:
                        xcord = round(i.x * 35 + ((35 * i.l)/2)) - 16
                        ycord = round(i.y * 35 + ((35 * i.h/2))) - 16
                    canvas.paste(image, (xcord, ycord), mask=image)
        
        #open xml for image info
        with open("layout txts/" + ship.layout + '.xml', 'r', encoding='utf-8') as t:
            for x in t:
                x = x.rstrip('\n')
                xmlList.append(x)
        
        #find image line
        for line2 in xmlList:
            if "<img" in line2:
                imageStats = line2.split()

                imgx = int(''.join(re.findall(r'-?\d+', imageStats[1])))
                imgy = int(''.join(re.findall(r'-?\d+', imageStats[2])))
                imgl = int(''.join(re.findall(r'\d+', imageStats[3])))
                imgh = int(''.join(re.findall(r'\d+', imageStats[4])))

                shipImage = Image.new('RGBA', (imgl, imgh))
                image = Image.open(ship.img).convert('RGBA')
                shipImage.paste(image, (0, 0), mask=image)
                shipImage.paste(canvas, (-imgx, -imgy), mask=canvas)

                shipImage.save("output/" + ship.name + " layout.png")
                continue