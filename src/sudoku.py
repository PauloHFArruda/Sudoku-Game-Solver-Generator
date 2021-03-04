from typing import Tuple, List, Set, Union, Dict, Optional
import random


Index = Tuple[int, int]
Change = Tuple[Index, int]


class Sudoku:
    def __init__(self, initial_config: List[List[int]]):
        self._values: List[List[int]] = [[0 for _ in range(9)] for _ in range(9)]
        self._possibilities: List[List[Set[int]]] = [[set([i for i in range(1, 10)]) 
                for _ in  range(9)] for _ in range(9)]
        self.locked_indexes: Set[Index] = set()
        self._error_cells: Set[Index] = set()
        self._empty_cells = set([(i, j) for i in range(9) for j in range(9)])
        self._changes_history: List[Change] = []

        self.init(initial_config)

    def init(self, initial_config: List[List[int]]) -> None:
        for i in range(9):
            for j in range(9):
                if initial_config[i][j] > 0:
                    self.change_value((i,j), initial_config[i][j])
                    self.locked_indexes.add((i, j))

        self._changes_history = []

    def reinit(self, initial_config: List[List[int]]) -> None:
        self._values = [[0 for _ in range(9)] for _ in range(9)]
        self._possibilities = [[set([i for i in range(1, 10)]) 
                for _ in  range(9)] for _ in range(9)]
        self.locked_indexes: Set[Index] = set()
        self._error_cells: Set[Index] = set()
        self._empty_cells = set([(i, j) for i in range(9) for j in range(9)])
        self.init(initial_config)

    def lock_nonzero_indexes(self) -> None:
        for i in range(9):
            for j in range(9):
                if self.get_value((i, j)) > 0:
                    self.locked_indexes.add((i, j))

    def clean_unloked_cells(self) -> None:
        for i in range(9):
            for j in range(9):
                if not (i,j) in self.locked_indexes:
                    self.change_value((i, j), 0)

        self._changes_history = []

    def get_value(self, index: Index) -> int:
        """Retorna o valor da celula correspondente ao index"""
        return self._values[index[0]][index[1]]

    def get_possibilities(self, index: Index) -> Set[int]:
        """Retorna os possiveis valores da celula correspondente ao index"""
        return self._possibilities[index[0]][index[1]].copy()

    def add_possibility(self, index: Index, value: int) -> None:
        """Adiciona um valor ao conjunto de possibilidades de um determinado index"""
        self._possibilities[index[0]][index[1]].add(value)

    def discard_possibility(self, index: Index, value: int) -> None:
        """Discarta um valor do conjunto de possibilidades de um determinado index"""
        self._possibilities[index[0]][index[1]].discard(value)

    @property
    def empty_cells(self) -> Set[Index]:
        return self._empty_cells.copy()

    @property
    def error_cells(self) -> Set[Index]:
        return self._error_cells.copy()

    def has_empty_cells(self) -> bool:
        return len(self._empty_cells) != 0

    def has_error_cells(self) -> bool:
        return len(self._error_cells) != 0

    def has_no_possibilities_cell(self):
        for index in self.empty_cells:
            if not self.get_possibilities(index):
                return True
        return False

    def row(self, index: Index) -> List[Index]:
        """Retorna um vetor com as coordenadas da linha referente ao index"""
        return [(index[0], k) for k in range(9)]
    
    def column(self, index: Index) -> List[Index]:
        """Retorna um vetor com as coordenadas da coluna referente ao index"""
        return [(k, index[1]) for k in range(9)]
    
    def box(self, index: Index) -> List[Index]:
        """Retorna um vetor com as coordenadas da caixa referente ao index"""
        i, j = index
        box_start_i, box_start_j = 3*(i//3), 3*(j//3)
        aux = []
        for i in range(box_start_i, box_start_i + 3):
            for j in range(box_start_j, box_start_j + 3):
                aux.append((i,j))
        return aux

    def row_column_box(self, index: Index) -> List[Index]:
        """Retorna um vetor com as coordenadas da linha, coluna e caixa referente ao index"""
        return self.row(index) + self.column(index) + self.box(index)

    def has_value_in(self, value: int, list_to_check: List[Index]) -> bool:
        """Retorna verdadeiro se o valor está na lista"""
        for index in list_to_check:
            if self.get_value(index) == value:
                return True
        return False

    def in_row(self, index: Index, value: int) -> bool:
        """Retorna verdadeiro se o valor está na linha referente ao index"""
        return self.has_value_in(value, self.row(index))
    
    def in_column(self, index: Index, value: int) -> bool:
        """Retorna verdadeiro se o valor está na coluna referente ao index"""
        return self.has_value_in(value, self.column(index))

    def in_box(self, index: Index, value: int) -> bool:
        """Retorna verdadeiro se o valor está na caixa referente ao index"""
        return self.has_value_in(value, self.box(index))

    def in_row_column_box(self, index: Index, value: int) -> bool:
        """Retorna verdadeiro se o valor está na linha, coluna ou caixa referente ao index"""
        return self.has_value_in(value, self.row_column_box(index))
    
    def __clean_value(self, index: Index) -> None:
        """Limpa o valor da celula e ajusta os valores possiveis da celula e das
        celulas da mesma linha, coluna ou caixa"""
        i, j = index
        previous = self.get_value(index)
        self._values[i][j] = 0

        for k in self.row_column_box(index):
            if not self.in_row_column_box(k, previous):
                self.add_possibility(k, previous)
        
        self._empty_cells.add(index)

    def __set_value(self, index: Index, value: int) -> None:
        """Muda o valor da celula para um valor entre 1 e 9 e ajusta os valores possiveis
        das celulas da mesma linha, coluna ou caixa"""
        i,j = index
        if not value in self.get_possibilities(index):
            self._values[i][j] = value
            self._error_cells.update(self.find(value, self.row_column_box(index)))
        else:
            self._values[i][j] = value
        
        for i in self.row_column_box(index):
            self.discard_possibility(i, value)

        self._empty_cells.discard(index)

    def change_value(self, index: Index, value: int):
        """Muda o valor de uma celula para um determinado valor entre 1 e 9 
        ou limpa a celula caso o valor seja 0"""
        if (value >= 0) and (value < 10):
            if  self.get_value(index) != 0:
                self._changes_history.append((index, self.get_value(index)))
                self.__clean_value(index)
                self.verify_errors() #verifica se a mudança concertou algum erro
            else:
                self._changes_history.append((index,0))
            if value > 0:
                self.__set_value(index, value)

    def find(self, value: int, list_to_check: List[Index]) -> Set[Index]:
        """Retorna um conjunto com indices da lista que apresentam determinado valor"""
        return set(filter(lambda index: self.get_value(index) == value, list_to_check))

    def verify_errors(self):
        """Verifica se erros persistem"""
        errors_to_discard = set()
        for index in self._error_cells:
            value = self.get_value(index)
            if value != 0:
                if len(self.find(value, self.row_column_box(index))) == 1:
                    errors_to_discard.add(index)
            else:
                errors_to_discard.add(index)
        self._error_cells.difference_update(errors_to_discard)

    def undo(self):
        """Desfaz a última mudança"""
        if len(self._changes_history) > 0:
            change = self._changes_history.pop()
            self.change_value(*change)
            self._changes_history.pop()

    def copy(self):
        return Sudoku(self._values)

    def print_values(self):
        for line in self._values:
            print('  '.join(map(str, line)))


class SudokuSolver:
    def __init__(self, sudoku: Union[Sudoku, List[List[int]]]):
        self.sudoku: Sudoku
        if isinstance(sudoku, Sudoku):
            self.sudoku = sudoku
        else:
            self.sudoku = Sudoku(sudoku)
        self.attempts: List[Tuple[Index, Set[int]]] = []
        self.changes_to_make: List[Change] = []
        self.possibilities_to_discard: List[Tuple[Index, Set[int]]] = []
        self.double_pairs_indexes: List[Index] = []
        self.discarted_possibilities: List[Tuple[Index, Set[int]]] = []
        self.step = 0

    def reinit(self) -> None:
        self.attempts = []
        self.changes_to_make = []
        self.possibilities_to_discard = []
        self.double_pairs_indexes = []
        self.discarted_possibilities = []
        self.step = 0
        self.sudoku.clean_unloked_cells()

    def check_solved_cells(self) -> List[Change]:
        """Retorna um vetor com os index e valores das celulas resolvidas"""
        aux = []
        for i in range(9):
            for j in range(9):
                index = (i, j)
                if self.sudoku.get_value(index) == 0:
                    cell = self.sudoku.get_possibilities(index)
                    if len(cell) == 1:
                        aux.append((index, cell.pop()))
        return aux

    def is_single(self, list_to_check: List[Index]) -> List[Change]:
        """Retorna um vetor com os index e valores de cada valor entre 1 e 9 que aparece
        uma unica vez na lista de index"""
        aux = [[] for _ in range(9)]
        for index in list_to_check:
            if self.sudoku.get_value(index) == 0:
                for k in self.sudoku.get_possibilities(index):
                    aux[k-1].append(index)
        return [(k[0], i+1) for i,k in enumerate(aux) if len(k) == 1]
    
    def check_singles(self) -> List[Change]:
        """Retorna um vetor com os index e valores de cada valor unico em uma
        linha, coluna ou caixa"""
        aux = []
        for i in range(9):
            aux.extend(self.is_single(self.sudoku.row((i,0))))
            aux.extend(self.is_single(self.sudoku.column((0,i))))
        
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                aux.extend(self.is_single(self.sudoku.box((i,j))))
        
        return aux

    def has_double_pairs(self, list_to_check: List[Index]) -> Tuple[List[Tuple[Index, Set[int]]], Set[Index]]:
        """Retorna as possibilidades para discartar e os indexes dos pares duplicados"""
        pairs_index = []
        double_pairs = []

        for index in list_to_check:
            if self.sudoku.get_value(index) == 0:
                cell = self.sudoku.get_possibilities(index)
                if len(cell) == 2:
                    for pair_index in pairs_index:
                        pair_cell = self.sudoku.get_possibilities(pair_index)
                        if cell == pair_cell:
                            double_pairs.append(((index, pair_index), cell))
                    pairs_index.append(index)

        list_to_discard = []
        for double_pair in double_pairs:
            double_pair_indexes, double_pair_cell = double_pair
            for index in list_to_check:
                if (index != double_pair_indexes[0]) and (index != double_pair_indexes[1]):
                    if self.sudoku.get_value(index) == 0:
                        intersection = self.sudoku.get_possibilities(index).intersection(double_pair_cell)
                        if len(intersection) > 0:
                            list_to_discard.append((index, intersection))

        set_double_pair_indexes = set()
        for double_pair in double_pairs:
            indexes,_ = double_pair
            for index in indexes:
                set_double_pair_indexes.add(index)

        return list_to_discard, set_double_pair_indexes

    def check_double_pairs(self) -> Tuple[List[Tuple[Index, Set[int]]], List[Index]]:
        """Retorna as possibilidades para discartar e os indexes dos pares
        duplicados de todas as linhas, colunas, e caixas"""
        list_to_discard = []
        double_pair_indexes = set()
        for i in range(9):
            aux1, aux2 = self.has_double_pairs(self.sudoku.row((i,0)))
            list_to_discard.extend(aux1)
            double_pair_indexes.update(aux2)
            aux1, aux2 = self.has_double_pairs(self.sudoku.column((0,i)))
            list_to_discard.extend(aux1)
            double_pair_indexes.update(aux2)
        
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                aux1, aux2 = self.has_double_pairs(self.sudoku.box((i,j)))
                list_to_discard.extend(aux1)
                double_pair_indexes.update(aux2)
        
        return list_to_discard, list(double_pair_indexes)
    
    def make_changes(self, list_to_change: List[Change]) -> None:
        """Faz cada uma das mudanças de um vetor de mudanças"""
        for change in list_to_change:
            self.sudoku.change_value(*change)

    def discard_possibilities(self, list_to_discard: List[Tuple[Index, Set[int]]]) -> None:
        for to_discard in list_to_discard:
            index, values_to_discard = to_discard
            for value in values_to_discard:
                self.sudoku.discard_possibility(index, value)

    def fix_possibilities(self, list_to_fix: List[Tuple[Index, Set[int]]]) -> None:
        for index, possibilities in list_to_fix:
            for value in possibilities:
                if not self.sudoku.in_row_column_box(index, value):
                    self.sudoku.add_possibility(index, value)

    def make_attempt(self) -> List[Change]:
        index = min(self.sudoku.empty_cells, key = lambda index: len(self.sudoku.get_possibilities(index)))
        #index = self.sudoku.empty_cells.pop()
        value = self.sudoku.get_possibilities(index).pop()
        self.attempts.append((index, set([value])))
        return [(index, value)]

    def change_attempt(self) -> List[Change]:
               
        while len(self.attempts) > 0:
            last_attempt_index, last_attempt_set = self.attempts[-1]
            
            while self.sudoku.get_value(last_attempt_index) != 0:
                self.sudoku.undo()
            self.fix_possibilities(self.discarted_possibilities)
            self.discarted_possibilities = []
            
            possibilities = self.sudoku.get_possibilities(last_attempt_index).difference(last_attempt_set)
            if len(possibilities) > 0:
                new_value = possibilities.pop()
                self.attempts[-1][1].add(new_value)
                return [(last_attempt_index, new_value)]
            else:
                self.attempts.pop()

        return []

    def step_solve(self) -> None:
        if self.sudoku.has_error_cells() or self.sudoku.has_no_possibilities_cell():
            print('problema')
            self.changes_to_make = self.change_attempt()
            self.possibilities_to_discard = []
            self.step = 0
        elif self.changes_to_make:
            self.make_changes(self.changes_to_make)
            self.changes_to_make = []
            self.step = 0
        elif self.possibilities_to_discard:
            self.discard_possibilities(self.possibilities_to_discard)
            self.possibilities_to_discard = []
            self.double_pairs_indexes = []
            self.step = 0
        else:
            if self.step == 0:
                self.changes_to_make = self.check_solved_cells()
            elif self.step == 1:
                self.changes_to_make = self.check_singles()
            elif self.step == 2:
                self.possibilities_to_discard, self.double_pairs_indexes = self.check_double_pairs()
                if not self.possibilities_to_discard:
                    self.double_pairs_indexes = []
                else:
                    self.discarted_possibilities.extend(self.possibilities_to_discard)
            else:
                self.changes_to_make = self.make_attempt() 
            self.step += 1

    def solve(self) -> Dict[str, int]:
        stats = {
            "clues": len(self.sudoku.locked_indexes),
            "steps": 0,
            "solved-cells": 0,
            "singles": 0,
            "double-pairs": 0,
            "attempts": 0,
            "attempt-change": 0,
        }
        step = 0
        while self.sudoku.has_empty_cells() or self.sudoku.has_error_cells():
            stats['steps'] += 1
            if self.attempts:
                if self.sudoku.has_error_cells() or self.sudoku.has_no_possibilities_cell():
                    self.changes_to_make = self.change_attempt()
                    stats['attempt-change'] += 1
            if self.changes_to_make:
                self.make_changes(self.changes_to_make)
                self.changes_to_make = []
                step = 0
            elif self.possibilities_to_discard:
                self.discard_possibilities(self.possibilities_to_discard)
                self.discarted_possibilities.extend(self.possibilities_to_discard)
                self.possibilities_to_discard = []
                step = 0
            else:
                if step == 0:
                    self.changes_to_make = self.check_solved_cells()
                    stats['solved-cells'] += len(self.changes_to_make)
                elif step == 1:
                    self.changes_to_make = self.check_singles()
                    stats['singles'] += len(self.changes_to_make)
                elif step == 2:
                    self.possibilities_to_discard,_ = self.check_double_pairs()
                    stats['double-pairs'] += len(self.possibilities_to_discard)
                else:
                    self.changes_to_make = self.make_attempt()
                    stats['attempts'] += 1
                step += 1
        
        return stats


def read_sudoku(difficulty: Optional[str] = None, number: Optional[int] = None):
    if difficulty == None:
        difficulty = random.choice(['facil', 'medio', 'dificil', 'expert'])
    if number == None:
        number = random.randint(0,14)
    with open('games/'+difficulty+'.txt', 'r') as f:
        sudoku_games = f.readlines()
    return [list(map(int, line.split())) for line in sudoku_games[number*10:number*10+9]]


if __name__ == '__main__':
    import time
    import pandas as pd
    difficulty = 'facil'
    aux = []
    for i in range(15):
        print(i)
        solver = SudokuSolver(read_sudoku(difficulty, i))
        
        start = time.time_ns()
        try:
            stats = solver.solve()
        except:
            continue
        end = time.time_ns()
        stats['solve-time-ms'] = (end - start)//1_000_000
        aux.append(stats)
        
    df = pd.DataFrame(aux)
    df.to_excel('stats/'+difficulty+'.xlsx')



