import pygame as pg
import src.pages as pages
from src.pygamepages import PageManager

sc_width = 680
sc_height = 470
sc_size = (sc_width, sc_height)

color = {'white': (255,255,255),
    'black': (0,0,0),
    'yellow': (224,227,152),
    'blue': (0,0,255),
    'blue_light': (150,200,240),
    'gray_light': (150,150,150)}

pg.init()
screen = pg.display.set_mode(sc_size)
pg.display.set_caption('Sudoku')
clock = pg.time.Clock()
PageManager.init(screen)
pages.MainMenu()
pages.SelectDifficulty()
pages.GamePage()
pages.SelectSolutionPage()
pages.SolverPage()
pages.GeneratorPage()


example2 = [[0,3,0,0,0,0,0,0,0],
            [0,0,0,0,0,8,0,6,0],
            [7,0,0,0,0,0,8,0,9],
            [8,0,0,0,0,3,0,0,4],
            [0,0,6,0,0,0,0,0,0],
            [3,7,5,0,0,0,6,1,0],
            [0,0,0,0,6,0,0,0,7],
            [4,8,0,0,0,1,5,0,0],
            [0,5,1,3,0,0,0,0,0]]

playing = True
while playing:
    clock.tick(30)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            playing = False
        else:
            PageManager.event_handler(event)
    
    PageManager.loop()

    pg.display.update()

pg.quit()