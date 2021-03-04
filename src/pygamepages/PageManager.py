import pygame
from pygame import Surface, Vector2
from typing import NewType, List, Callable, Any


class Page:
    _event_funcs: List[List[Callable]]
    tag: str

    def on_open(self): pass

    def on_close(self): pass

    def _draw(self): pass

    def _update(self): pass    


EventType = NewType('EventType', int)
_screen: Surface
_current_page: Page
_pages: List[Page] = []
NUMBER_EVENT_TYPES = 7

def init(surf) -> None:
    global _screen
    _screen = surf

def __find_page(tag) -> int:
    for i, page in enumerate(_pages):
        if page.tag == tag:
            return i
    raise Exception('Page not found')

def _add_page(page: Page) -> None:
    _pages.append(page)
    if len(_pages) == 1:
        __set_start_page(page.tag)

def __set_start_page(tag: str, *args, **kw) -> None:
    global _current_page
    _current_page = _pages[__find_page(tag)]
    _current_page.on_open(*args, **kw)

def change_page(tag: str, *args, **kw) -> None:
    global _current_page
    _current_page.on_close()
    _current_page = _pages[__find_page(tag)]
    _current_page.on_open(*args, **kw)

def loop() -> None:
    _current_page._update()
    _current_page._draw()

def bind(event_type: EventType, func: Callable[[Any], None], page_tag: str) -> None:
    _pages[__find_page(page_tag)]._event_funcs[event_type].append(func)

def event_handler(event) -> None:
    if event.type < NUMBER_EVENT_TYPES:
        for func in _current_page._event_funcs[event.type]:
            func(event)