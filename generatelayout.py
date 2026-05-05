#WHAT YOU NEED TO DO TO RUN THIS
#Have Pillow installed (done through pip install pillow)
#Put all the layout txts AND xml files in the "layout info files" folder 
#Put all the ship image files in the "layout images" folder
#Have the autoBlueprints.xml.append file in the same folder as the script
#Make sure the base door and room files (comes in the script folder) exist and have the right folder path ("rooms" folder)
#Make sure the base system files (comes in the script folder) exist and have the right folder path ("icons" folder)
#All of these files/folder should be in the same location as the script

#Created by Basic Person
import os
import sys
import re
from PIL import Image
import xml.etree.ElementTree as ET

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#checks if file was dropped
#try:
#    droppedFile = sys.argv[1]
#except IndexError:
#    print("No file was dropped")

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
        if "true" in start:
            self.start = True
        if "false" in start:
            self.start = False
        self.name = name
        self.room = int(room)

class Ship:
    def __init__(self, name, layout, img):
        self.layout = layout
        self.img = "layout images/" + img + "_base.png"
        self.name = name

with open("autoBlueprints.xml.append", "r", encoding="utf-8") as f:
    content = f.read()

root=ET.fromstring(content)

#read through the autofile for info
for child in root:
    if child.tag == "shipBlueprint":
        name = child.attrib["name"]
        counter = 0
        roomList = []
        doorList = []
        tileList = []
        xmlList = []
        systemClassList = []
        skip = False
        shipInfo = [name, child.attrib["layout"], child.attrib["img"]]
        ship = Ship(shipInfo[0], shipInfo[1], shipInfo[2])
        print(ship.name)

        #read layout file
        filePath = "layout info files/" + ship.layout + ".txt"
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
        for subchild in child:
            if subchild.tag == "systemList":
                for system in subchild:
                    try:
                        [system.attrib["start"]]
                    except:
                        system.attrib.update({"start": "true"})
                    systemClassList.append(System(system.tag, system.attrib["room"], system.attrib["start"]))

        for i in roomList:
            for system in systemClassList:
                file = "icons/" + system.name + ".png"
                image = Image.open(file).convert('RGBA')

                if system.start == False:
                    rc, gc, bc, ac = image.split()
                    rc = rc.point(lambda p: int(p+200))
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
        with open("layout info files/" + ship.layout + '.xml', 'r', encoding='utf-8') as t:
            content = t.read()

        content = re.sub(r"<\?xml.*?\?>", "", content).strip()
        wrapped = f"<root>\n{content}\n</root>"
        imageRoot=ET.fromstring(wrapped)

        for imageChild in imageRoot:
            if imageChild.tag == "img":
                imageStats = [imageChild.attrib["x"], imageChild.attrib["y"], imageChild.attrib["w"], imageChild.attrib["h"]]

                imgx = int(''.join(re.findall(r'-?\d+', imageStats[0])))
                imgy = int(''.join(re.findall(r'-?\d+', imageStats[1])))
                imgl = int(''.join(re.findall(r'\d+', imageStats[2])))
                imgh = int(''.join(re.findall(r'\d+', imageStats[3])))

                shipImage = Image.new('RGBA', (imgl, imgh))
                image = Image.open(ship.img).convert('RGBA')
                shipImage.paste(image, (0, 0), mask=image)
                shipImage.paste(canvas, (-imgx, -imgy), mask=canvas)

                shipImage.save("output/" + ship.name + " layout.png")

                continue
