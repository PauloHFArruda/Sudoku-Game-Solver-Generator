from .pygamepages import*
from functools import partial
from .sudoku import Sudoku, SudokuSolver, read_sudoku
import pygame


colors = {'white': (255,255,255),
    'black': (0,0,0),
    'yellow': (224,227,152),
    'red': (240,0,0),
    'red_light': (250,110,110),
    'red_secondary': (255,32,32),
    'blue': (0,0,255),
    'blue_light': (180,215,255),
    'text_primary': (52, 72, 97),
    'text_secondary': (92, 102, 115),
    'gray': (150,150,150),
    'gray_dark': (40,40,40),
    'gray_light': (220,220,220),
    'pink_light': (250,180,205)}


example2 = [[0,3,0,0,0,0,0,0,0],
            [0,0,0,0,0,8,0,6,0],
            [7,0,0,0,0,0,8,0,9],
            [8,0,0,0,0,3,0,0,4],
            [0,0,6,0,0,0,0,0,0],
            [3,7,5,0,0,0,6,1,0],
            [0,0,0,0,6,0,0,0,7],
            [4,8,0,0,0,1,5,0,0],
            [0,5,1,3,0,0,0,0,0]]


class Text(Element):
    def __init__(self, parent, pos, text, font=('Arial', 24), color=(0,0,0), bold=False):
        super().__init__(parent, pos, (1,1))
        self._font = pygame.font.SysFont(*font)
        self._color = color
        self.surfs = []
        self.line_height = 1
        self.set_text(text)

    def draw(self):
        for i, surf in enumerate(self.surfs):
            self.blit(surf, (0, i*self.line_height))

    def set_text(self, new_text: str) -> None:
        lines = new_text.split('\n')
        self.surfs = [self._font.render(line, True, self._color) for line in lines]
        self.line_height = self.surfs[0].get_size()[1]
        

class MyButton(TextButton):
    def __init__(self, parent, pos, text, func, **kw):
        super().__init__(parent, pos, text, func, font_size=24, size=(190,35), 
                centralized=True, background_color=(30,30,30))
        self.config(**kw)
    
    def update(self):
        if self.on_mouse_focus():
            self.background_color = (155,155,155)
        else:
            self.background_color = (170,170,170)


class MainMenu(Page):
    def __init__(self):
        super().__init__('MainMenu')

        self.background = pygame.Surface(self.size)
        self.background.fill(colors['white'])

        Label(self, (self.width/2, 0.2*self.height), 'Sudoku', font_size=42, centralized=True)

        MyButton(self, (self.width/2, 0.55*self.height), 'Jogar/Resolver', 
                partial(PageManager.change_page, 'SelectDifficulty'))
        #MyButton(self, (self.width/2, 0.60*self.height), 'Resolver', 
        #        partial(PageManager.change_page, 'SolverPage', [[0 for _ in range(9)] for _ in range(9)]))
        MyButton(self, (self.width/2, 0.7*self.height), 'Gerar', 
                partial(PageManager.change_page, 'GeneratorPage'))

    def draw(self):
        self.blit(self.background)


class SelectDifficulty(Page):
    def __init__(self):
        super().__init__('SelectDifficulty')

        self.background = pygame.Surface(self.size)
        self.background.fill(colors['white'])

        #Label(self, (self.width/2, self.height*0.18), 'Dificuldade', centralized=True)
        self.frame = Frame(self, self.center, 0.6*self.size, centralized=True)
        MyButton(self.frame, (self.frame.width/2, 1/6*self.frame.height), 'Em Branco', 
                partial(self.select, 'branco'))
        MyButton(self.frame, (self.frame.width/2, 2/6*self.frame.height), 'Fácil', 
                partial(self.select, 'facil'))
        MyButton(self.frame, (self.frame.width/2, 3/6*self.frame.height), 'Médio', 
                partial(self.select, 'medio'))
        MyButton(self.frame, (self.frame.width/2, 4/6*self.frame.height), 'Difícil', 
                partial(self.select, 'dificil'))
        MyButton(self.frame, (self.frame.width/2, 5/6*self.frame.height), 'Expert', 
                partial(self.select, 'expert'))

    def select(self, difficulty):
        if difficulty == 'branco':
            PageManager.change_page('GamePage', [[0 for _ in range(9)] for _ in range(9)])
        PageManager.change_page('GamePage', read_sudoku(difficulty))

    def draw(self):
        self.blit(self.background)


class SudokuTable(Element):
    def __init__(self, source, pos, size, sudoku):
        super().__init__(source, pos, size)
        self.step = self.size[0]/9
        self.surf = pygame.Surface(self.size)
        font_size = int(self.size[0]/9)
        self.font = pygame.font.SysFont('arial', font_size)
        self.font_secondary = pygame.font.SysFont('arial', int(font_size*0.35))
        text = self.font.render('1', True, colors['black'])
        txt_size = text.get_size()
        self.centralized_pos = ((self.step*1.05 - txt_size[0])/2, 
            (self.step*1.05 - txt_size[1])/2)
        
        self.selected_cell = None
        
        self.sudoku = sudoku
        self.cells_to_detach = []
        self.numbers_to_detach = []
        self.auto_notes = True
        self.note = False
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.bind(pygame.MOUSEBUTTONDOWN, self.on_click)
    
    def detach_cell(self, index, color):
        step = self.step
        pos = (index[1]*step, index[0]*step)
        rect = pygame.Rect(*pos, step, step)
        pygame.draw.rect(self.surf, color, rect)
    
    def detach_row(self, index, color):
        step = self.step
        pos = (index[1]*step, 0)
        rect = pygame.Rect(*pos, step, self.size[0])
        pygame.draw.rect(self.surf, color, rect)
    
    def detach_column(self, index, color):
        step = self.step
        pos = (0, index[0]*step)
        rect = pygame.Rect(*pos, self.size[0], step)
        pygame.draw.rect(self.surf, color, rect)

    def detach_box(self, index, color):
        step = self.step
        pos = (step * 3*(index[1]//3), step * 3*(index[0]//3))
        rect = pygame.Rect(*pos, 3*step, 3*step)
        pygame.draw.rect(self.surf, color, rect)

    def detach_number(self, index, number, color):
        value = self.sudoku.get_value(index)
        if value != 0:
            self.draw_number(index, number, color, False)
        else:
            self.draw_number(index, number, color, True)

    def draw_cells(self):
        if self.selected_cell:
            self.detach_row(self.selected_cell, colors['gray_light'])
            self.detach_column(self.selected_cell, colors['gray_light'])
            self.detach_box(self.selected_cell, colors['gray_light'])
            self.detach_cell(self.selected_cell, colors['blue_light'])
        
        for indexes, color in self.cells_to_detach:
            for index in indexes:
                self.detach_cell(index, color)

    def draw_number(self, index, number, color, note):
        step = self.step
        surf = self.surf
        i, j = index
        if note:
            text = self.font_secondary.render(str(number), True, color)
            pos_x = (j+0.12)*step + ((number-1)%3)*step*0.3
            pos_y = (i+0.035)*step + ((number-1)//3)*step*0.3
            surf.blit(text, (pos_x, pos_y))
        else:
            centralized_pos = self.centralized_pos
            text = self.font.render(str(number), True, color)
            pos = (centralized_pos[0] + j*step, centralized_pos[1] + i*step)
            surf.blit(text, pos)

    def draw_numbers(self):
        for i in range(9):
            for j in range(9):
                value = self.sudoku.get_value((i,j))
                if value != 0:
                    if (i, j) in self.sudoku.locked_indexes:
                        self.draw_number((i,j), value, colors['black'], False)
                    else:
                        self.draw_number((i,j), value, colors['text_primary'], False)
                else:
                    if self.auto_notes:
                        cell = self.sudoku.get_possibilities((i, j))
                    else:
                        cell = self.notes[i][j]
                    for k in cell:
                        self.draw_number((i,j), k, colors['text_secondary'], True)
        
        for index in self.sudoku.error_cells:
            self.detach_number(index, self.sudoku.get_value(index), colors['red'])

        for cells, color in self.numbers_to_detach:
            for index, k in cells:
                if isinstance(k, int):
                    self.detach_number(index, k, color)
                else:
                    for value in k:
                        self.detach_number(index, value, color)
  
    def draw_lines(self):
        step = self.step
        surf = self.surf
        for i in range(10):
            start_pos = (int(i*step), 0)
            end_pos = (start_pos[0], self.size[0])

            if (i%3 == 0):
                pygame.draw.line(surf, colors['black'], start_pos, end_pos, 3)
            else:
                pygame.draw.line(surf, colors['black'], start_pos, end_pos, 1)

        
        for i in range(10):
            start_pos = (0, i*step)
            end_pos = (self.size[0], start_pos[1])

            if (i%3 == 0):
                pygame.draw.line(surf, colors['black'], start_pos, end_pos, 3)
            else:
                pygame.draw.line(surf, colors['black'], start_pos, end_pos, 1)

    def draw(self):
        self.surf.fill(colors['white'])
        self.draw_cells()
        self.draw_numbers()
        self.draw_lines()
        self.blit(self.surf)

    def on_click(self, event):
        if self.on_mouse_focus():
            pos = self.mouse_pos()
            self.selected_cell = (int(pos[1]//self.step), int(pos[0]//self.step))

    def make_note(self, index, value):
        notes = self.notes[index[0]][index[1]]
        if self.sudoku.get_value(index) != 0:
            self.sudoku.change_value(index, 0)
        if value in notes:
            notes.discard(value)
        elif value > 0:
            notes.add(value)


class SudokuPage(Page):
    def __init__(self, tag):
        super().__init__(tag)
        self.background = pygame.Surface(self.size)
        self.background.fill(colors['white'])
        pygame.draw.rect(self.background, colors['black'], pygame.Rect(5, 5, 456, 456))

        self.sudoku = Sudoku(read_sudoku())
        self.table = SudokuTable(self, (8,8), (450, 450), self.sudoku)
        MyButton(self, (565, 35), 'Menu', partial(PageManager.change_page, 'MainMenu'))

        self.bind(pygame.KEYDOWN, self.key_down)
    
    def on_open(self, *args, **kw):
        if args:
            if isinstance(args[0], Sudoku):
                self.sudoku.reinit(args[0]._values)
            else:
                self.sudoku.reinit(args[0])
            self.table.sudoku = self.sudoku
            self.table.notes = [[set() for _ in range(9)] for _ in range(9)]

    def draw(self):
        self.blit(self.background)

    def numeric_key_down(self, value):
        selected_cell = self.table.selected_cell
        if selected_cell:
            if not selected_cell in self.sudoku.locked_indexes:
                if self.table.note and not self.table.auto_notes:
                    self.table.make_note(selected_cell, value)
                else:
                    self.sudoku.change_value(selected_cell, value)

    def arrows_key_down(self, event):
        cell = self.table.selected_cell
        if cell is None:
            cell = (0,0)
        if event.key == pygame.K_UP:
            self.table.selected_cell = (max(0, cell[0] - 1), cell[1])
        elif event.key == pygame.K_DOWN:
            self.table.selected_cell = (min(8, cell[0] + 1), cell[1])
        if event.key == pygame.K_LEFT:
            self.table.selected_cell = (cell[0], max(0, cell[1] - 1))
        if event.key == pygame.K_RIGHT:
            self.table.selected_cell = (cell[0], min(8, cell[1] + 1))

    def key_down(self, event):
        if event.unicode.isnumeric():
            self.numeric_key_down(int(event.unicode))    
        else: 
            self.arrows_key_down(event)


class GamePage(SudokuPage):
    def __init__(self):
        super().__init__('GamePage')
        self.table.auto_notes = False

        
        self.frame = Frame(self, (470, 0.48*self.height), (200,250))
        def func(label, but, event):
            if label.active and label.on_mouse_focus():
                but.value = not but.value
                but.func()
        self.auto_note_label = Label(self.frame, (0.36*self.frame.width, 0.20*self.frame.height), 'Auto Notas:', 
                centralized=True, font_size=25)
        self.auto_note_but = ButtonOnOff(self.frame, (0.85*self.frame.width, 0.20*self.frame.height), 
            scale=2, centralized=True, func=self.auto_note_change)
        self.bind(pygame.MOUSEBUTTONDOWN, partial(func, self.auto_note_label, self.auto_note_but))
        self.note_label = Label(self.frame, (0.37*self.frame.width, 0.40*self.frame.height), 'Anotar:', 
                centralized=True, font_size=25)
        self.note_but = ButtonOnOff(self.frame, (0.73*self.frame.width, 0.40*self.frame.height), 
            scale=2, centralized=True, func=self.note_change)
        self.bind(pygame.MOUSEBUTTONDOWN, partial(func, self.note_label, self.note_but))
        MyButton(self.frame, (self.frame.width/2, 0.60*self.frame.height), 'Desfazer', self.sudoku.undo)
        MyButton(self.frame, (self.frame.width/2, 0.80*self.frame.height), 'Resolver', self.solve)

    def solve(self):
        PageManager.change_page('SelectSolutionPage', self.sudoku)

    def auto_note_change(self):
        self.table.auto_notes = not self.table.auto_notes

    def note_change(self):
        self.table.note = not self.table.note

    def key_down(self, event):
        if event.key in (pygame.K_LALT, pygame.K_RALT):
            self.table.auto_notes = not self.table.auto_notes
            self.auto_note_but.value = self.table.note
        elif event.key in (pygame.K_RSHIFT, pygame.K_LSHIFT):
            self.table.note = not self.table.note
            self.note_but.value = self.table.note
        else: 
            super().key_down(event)


class SelectSolutionFrame(Frame):
    def __init__(self, parent, pos, size, **kw):
        super().__init__(parent, pos, size, **kw)
        self.centralized = True
        self.background = pygame.Surface(self.size)
        pygame.draw.rect(self.background, (255,255,255), pygame.Rect(3,3, self.width-6,self.height-6))
        pygame.draw.rect(self.background, (0,0,0), pygame.Rect(5,5, self.width-10,self.height-10))
        pygame.draw.rect(self.background, (255,255,255), pygame.Rect(7,7, self.width-14,self.height-14))
    
    def draw(self):
        self.blit(self.background)


class SelectSolutionPage(Page):
    def __init__(self):
        super().__init__('SelectSolutionPage')
        self.sudoku = None

        self.background = pygame.Surface(self.size)
        self.background.convert_alpha()
        self.background.set_alpha(150)
        self.background.fill((0,0,0))

        self.frame = SelectSolutionFrame(self, self.center, self.size/2)
        self.label = Label(self.frame, (self.frame.width/2, 0.15*self.frame.height), 'Resolver', centralized=True)
        self.step_by_step_but = MyButton(self.frame, (self.frame.width/2, 0.45*self.frame.height), 
                'Passo a Passo', partial(self.select, 'step_by_step'))
        self.quick_solve_but = MyButton(self.frame, (self.frame.width/2, 0.65*self.frame.height), 
                'Direto', partial(self.select, 'quick_solve'))
        self.cancel_but = MyButton(self.frame, (self.frame.width/2, 0.85*self.frame.height), 
                'Cancelar', partial(PageManager.change_page, 'GamePage'))

    def on_open(self, *args, **kw):
        self.sudoku = args[0]
        self.blit(self.background)

    def select(self, solution):
        PageManager.change_page('SolverPage', self.sudoku, solution)


class SolverPage(SudokuPage):
    def __init__(self):
        super().__init__('SolverPage')
        self.solver = SudokuSolver(self.sudoku)

        self.solving_frame = Frame(self, (470, 50), (190, 410), active=True, visible=True)
        self.step_text = Text(self.solving_frame, (0, 30), '', font=('Arial', 20, True))
        self.step_info_text = Text(self.solving_frame, (0, 60), '', font=('Arial', 14))
        self.found_text = Label(self.solving_frame, (self.solving_frame.width/2, 180), 
            '', centralized=True)
        self.next_step_but = MyButton(self.solving_frame, (self.solving_frame.width/2, 370), 
                'Próximo Passo', self.next_step)

        self.solved_label = Label(self, (565, 235), 'Resolvido', centralized=True, visible=False)

    def on_open(self, *args, **kw):
        super().on_open(*args, **kw)
        if self.sudoku.locked_indexes:
            self.sudoku.clean_unloked_cells()
        else:
            self.sudoku.lock_nonzero_indexes()
        self.solver.reinit()
        if args[1] == 'step_by_step':
            self.next_step()
        else:
            self.solver.solve()
            self.solving_frame.visible = False
            self.solved_label.visible = True
        self.update_numbers_to_detach()

    def draw(self):
        self.blit(self.background)

    def update_numbers_to_detach(self):
        self.table.numbers_to_detach = []
        self.table.numbers_to_detach.append((self.solver.changes_to_make, colors['red_light']))
        self.table.numbers_to_detach.append((self.solver.possibilities_to_discard, colors['red_light']))
        self.table.numbers_to_detach.append(
                ([(index, self.solver.sudoku.get_value(index)) 
                for index,_ in self.solver.attempts if self.solver.sudoku.get_value(index) != 0], 
                colors['blue']))

    def update_cells_to_detach(self):
        self.table.cells_to_detach = []
        self.table.cells_to_detach.append(
                ([index for index,_ in self.solver.changes_to_make], colors['yellow']))
        self.table.cells_to_detach.append((self.solver.double_pairs_indexes, colors['yellow']))
        #self.table.cells_to_detach.append(
        #    ([index for index,_ in self.solver.attempts], colors['pink_light']))

    def update_step_info(self):
        if self.solver.step == 1:
            self.step_text.set_text('Células Resolvidas')
            self.step_info_text.set_text('Células com apenas uma\npossibilidade')
            self.found_text.text = 'Encontradas: %d'%len(set(self.solver.changes_to_make))
        elif self.solver.step == 2:
            self.step_text.set_text('Possibilidade Única')
            self.step_info_text.set_text('Possibilidade que aparece \numa única vez em uma \nlinha, coluna ou caixa')
            self.found_text.text = 'Encontradas: %d'%len(set(self.solver.changes_to_make))
        elif self.solver.step == 3:
            self.step_text.set_text('Pares Duplicados')
            self.step_info_text.set_text('Um par de células com as \nmesmas duas possibilidades em \numa mesma linha, coluna ou \ncaixa. Permite discartar \npossibilidades')
            self.found_text.text = 'Encontradas: %d'%(len(set(self.solver.double_pairs_indexes))/2)
        elif self.solver.step == 4:
            self.step_text.set_text('Tentativa')
            self.step_info_text.set_text('Faz uma tentativa, caso \nchegue em um erro a tentativa\né trocada')
            self.found_text.text = 'Encontradas: 1'
        else:
            if self.solver.sudoku.has_error_cells():
                self.step_text.set_text('Erros')
                self.step_info_text.set_text('Erro implica tentativa errada, \ntroca-se a última tentiva \ndesfazendo as mudanças \nfeitas depois dela')
                self.found_text.text = ('Encontradas: %d'%(len(set(self.solver.sudoku.error_cells))))
            elif not self.solver.sudoku.has_empty_cells():
                self.solving_frame.visible = False
                self.solved_label.visible = True

    def next_step(self):
        self.solver.step_solve()
        self.update_cells_to_detach()
        self.update_numbers_to_detach()
        self.update_step_info()

    def key_down(self, event):
        super().key_down(event)
        if event.key == pygame.K_SPACE:
            self.next_step()


class GeneratorPage(Page):
    def __init__(self):
        super().__init__('GeneratorPage')
        self.background = pygame.Surface(self.size)
        self.background.fill((255,255,255))
        Label(self, (self.width/2, 0.25*self.height), 'Fazendo', centralized=True)
        MyButton(self, self.center, 'Menu', partial(PageManager.change_page, 'MainMenu'))

    def draw(self):
        self.blit(self.background)
