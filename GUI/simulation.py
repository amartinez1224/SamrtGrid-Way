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

    def loadMap(self, filename):
        self.map = []
        self.brickDesc = {}
        parser = cp.ConfigParser()
        parser.read(filename)
        try:
            self.brickset = parser.get("map", "brickimages").split(",")
            self.bricksize = [int(s) for s in parser.get("map", "bricksize").split(",")]
            self.map = parser.get("map", "map").split("\n")
            self.width = len(self.map[0])
            self.height = len(self.map)
            self.windowSize = [int(s) for s in parser.get("map", "windowsize").split(",")]
            self.mapArray = self.loadBrickImages(self.brickset, self.bricksize[0], self.bricksize[1])
            for s in parser.sections():
                if len(s) < 2:
                    brickDescription = dict(parser.items(s))
                    self.brickDesc[s] = brickDescription
        except Exception as e:
            print(e)
            exit("Failed to load: "+filename)

    def generate(self):
        bricks = self.mapArray
        image = pygame.Surface((self.width*self.bricksize[0], self.height*self.bricksize[1]))
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                brick = int(self.brickDesc[self.map[x][y]]['brick'])
                brick_image = bricks[brick]
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
