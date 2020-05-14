import pygame
import pygame.locals
import argparse
import configparser as cp

class World():

    def loadBrickImages(self,filenames, width, height):
        bricks = []
        for file in filenames:
            image = pygame.image.load(file).convert()
            image = pygame.transform.scale(image, (width, height))
            bricks.append(image)
        return bricks

    def extendMap(self,section):
        auxMap=[]
        for row in self.map:
            for j in range(section[1]):
                auxRow=[]
                for brick in row:
                    auxRow.extend([brick+"-"+str(j)+"-"+str(i) for i in range(section[0])])
                auxMap.append(auxRow)
        return auxMap

    def sectionImages(self,images,section):
        cropedImages={}
        for brick,image in images.items():
            width, height = image.get_size()
            width, height = width//section[0], height//section[1]
            for i in range(section[0]):
                for j in range(section[1]):
                    rect = (i*width, j*height, width, height)
                    cropedImages[brick+"-"+str(j)+"-"+str(i)]=image.subsurface(rect)
        return cropedImages

    def loadMap(self, filename):
        self.map = []
        self.brickDesc = {}
        parser = cp.ConfigParser()
        parser.read(filename)
        try:
            self.brickset = parser.get("map", "brickimages").split(",")
            self.bricksize = [int(s) for s in parser.get("map", "bricksize").split(",")]
            self.map = parser.get("map", "map").split("\n")
            self.bricks = self.loadBrickImages(self.brickset, self.bricksize[0], self.bricksize[1])
            bricks={}
            for s in parser.sections():
                if len(s) < 2:
                    brickDescription = dict(parser.items(s))
                    self.brickDesc[s] = brickDescription
                    bricks[s]=self.bricks[int(brickDescription["brick"])]
            self.bricks = bricks
            try:
                section = [int(s) for s in parser.get("map", "section").split(",")]
                self.map = self.extendMap(section)
                self.bricks = self.sectionImages(self.bricks,section)
                self.bricksize = (self.bricksize[0]//section[0],self.bricksize[1]//section[1])
            except cp.NoOptionError as e:
                pass
            self.width = len(self.map[0])
            self.height = len(self.map)
            self.windowSize = (self.width*self.bricksize[0],self.height*self.bricksize[1])
        except Exception as e:
            print(e)
            exit("Failed to load: "+filename)

    def generate(self):
        print(self.map)
        image = pygame.Surface((self.width*self.bricksize[0], self.height*self.bricksize[1]))
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                brick_image = self.bricks[self.map[y][x]]
                image.blit(brick_image,(x*self.bricksize[0], y*self.bricksize[1]))
        return image

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--map', type=str, help='File to load map', default='sim.txt')
    args = parser.parse_args()

    pygame.display.set_mode((1,1))
    World = World()
    World.loadMap(args.map)

    window = pygame.display.set_mode((World.windowSize[0], World.windowSize[1]))
    map = World.generate()
    window.blit(map, (0, 0))
    pygame.display.flip()

    terminate=True
    while terminate:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                terminate=False
