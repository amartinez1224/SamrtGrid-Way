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
        image = pygame.Surface((self.width*self.bricksize[0], self.height*self.bricksize[1]))
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                brick_image = self.bricks[self.map[y][x]]
                image.blit(brick_image,(x*self.bricksize[0], y*self.bricksize[1]))
        return image

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super(Sprite, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.pos = pos

    def _get_pos(self):
        return self.rect.topleft[0], self.rect.topleft[1]

    def _set_pos(self, pos):
        self.rect.topleft = pos[0], pos[1]

    def update(self):
        self.rect.move_ip(self.pos[0], self.pos[1])

    position = property(_get_pos, _set_pos)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--map', type=str, help='File to load map', default='sim.txt')
    args = parser.parse_args()

    pygame.display.set_mode((1,1))
    world = World()
    world.loadMap(args.map)

    window = pygame.display.set_mode((world.windowSize[0], world.windowSize[1]))
    map = world.generate()
    window.blit(map, (0, 0))
    pygame.display.flip()

    sprites = pygame.sprite.RenderUpdates()
    sprite = Sprite((100,200), world.loadBrickImages(["car.png"], 25,25)[0])
    sprites.add(sprite)

    sprites.update()
    print(sprite.position)
    sprite._set_pos((50,50))
    print(sprite.position)
    sprites.update()

    terminate=True
    while terminate:
        sprites.clear(window,map)
        dirty = sprites.draw(window)
        pygame.display.update(dirty)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                terminate=False
