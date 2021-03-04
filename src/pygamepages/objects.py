import pygame
from pygame import Vector2, Surface
from . import PageManager
from .PageManager import EventType
from typing import Union, Tuple, List, Callable, Optional, Any

Color = Union[Tuple[int, int, int], Tuple[int, int, int, int]]
Coordinate = Union[Vector2, Tuple[float, float]]



def vec2int(vec: Vector2) -> Tuple[int, int]:
    return (int(vec.x), int(vec.y))

def rect_fit(vec: Coordinate, rect_size: Coordinate) -> bool:
    if ((vec[0] > 0) and (vec[1] > 0) 
            and (vec[0] < rect_size[0]) and (vec[1] < rect_size[1])):
        return True
    return False


class BaseElement:
    _page_tag: str
    _pos: Vector2
    _parent_pos: Vector2
    _actual_pos: Vector2
    _size: Vector2
    _centralized: bool
    _active: bool
    visible: bool

    def config(self, **kw):
        for key, val in kw.items():
            if key[0] == '_':
                raise KeyError(f"'{key}' is not public")

            try:
                self.__setattr__(key, val)
            except:
                raise Exception(f"Invalid key:'{key}' or value:'{val}'")

    def _update_actual_pos(self):
        if self.centralized:
            self._actual_pos = self._parent_pos + self.pos - self.size/2
        else:
            self._actual_pos = self._parent_pos + self.pos

    @property
    def active(self) -> bool:
        return self._active
    
    @active.setter
    def active(self, new_value: bool) -> None:
        self._active = new_value

    @property
    def pos(self) -> Vector2: 
        return self._pos

    @pos.setter
    def pos(self, new_pos):
        self._pos = Vector2(new_pos)
        self._update_actual_pos()
    
    @property
    def size(self) -> Vector2: 
        return self._size

    @size.setter
    def size(self, new_size):
        size = Vector2(new_size)
        if (size[0] > 0) and (size[1] > 0):
            self._size = size
        else:
            raise Exception('Invalid size, expected positive values')
        self._update_actual_pos()
    
    @property
    def centralized(self) -> bool: 
        return self._centralized

    @centralized.setter
    def centralized(self, value: bool):
        if isinstance(value, bool):
            self._centralized = value
        else:
            raise ValueError
        self._update_actual_pos()

    @property
    def width(self) -> float:
        return self._size.x

    @width.setter
    def width(self, new_width: float):
        self._size.x = new_width

    @property
    def height(self) -> float:
        return self._size.y

    @height.setter
    def height(self, new_height: float):
        self._size.y = new_height

    @property
    def center(self) -> Vector2:
        return Vector2(self._size/2)

    def bind(self, event_type: EventType, func: Callable[[Any], None]):
        PageManager.bind(event_type, func, self._page_tag)

    def blit(self, surf: Surface, pos: Coordinate = Vector2(0, 0), centralized: bool = False):
        if centralized:
            PageManager._screen.blit(surf, self._actual_pos + pos + self.center - Vector2(surf.get_size())/2)
        else:
            PageManager._screen.blit(surf, self._actual_pos + pos)

    def _update(self):
        pass

    def _draw(self):
        pass

    def mouse_pos(self) -> Vector2:
        return Vector2(pygame.mouse.get_pos()) - self._actual_pos

    def on_mouse_focus(self) -> bool:
        return rect_fit(self.mouse_pos(), self._size)


class BaseFrame(BaseElement):
    _elements: List[BaseElement]

    @property
    def active(self) -> bool:
        return self._active
    
    @active.setter
    def active(self, new_value: bool) -> None:
        self._active = new_value
        for elt in self._elements:
            elt._active = new_value

    def _update_actual_pos(self):
        super()._update_actual_pos()
        for elt in self._elements:
            elt._parent_pos = self._actual_pos
            elt._update_actual_pos()

    def _update(self):
        if self.active:
            self.update()
            for elt in self._elements:
                if elt.active:
                    elt._update()

    def update(self):
        pass

    def _draw(self):
        if self.visible:
            self.draw()
            for elt in self._elements:
                if elt.visible:
                    elt._draw()

    def draw(self):
        pass


class Element(BaseElement):
    def __init__(self, parent: BaseFrame, pos: Coordinate, size: Coordinate, **kw):
        self._pos: Vector2
        self._size: Vector2
        self._actual_pos: Vector2
        self._active: bool = True
        self._centralized: bool = False
        self._parent_pos: Vector2 = parent._actual_pos
        self._page_tag: str = parent._page_tag

        self.visible: bool = True
        
        self.pos = pos
        self.size = size

        self.config(**kw)

        parent._elements.append(self)

    def _update(self):
        if self.active:
            self.update()

    def update(self):
        pass

    def _draw(self):
        if self.visible:
            self.draw()

    def draw(self):
        print('draw method not implemented')


class Frame(BaseFrame, Element):
    def __init__(self, parent: BaseFrame, pos: Coordinate, size: Coordinate, **kw):
        self._elements: List[Element] = []
        super().__init__(parent, pos, size, **kw)
    
    def _update_actual_pos(self):
        Element._update_actual_pos(self)
        for elt in self._elements:
            elt._parent_pos = self._actual_pos
            elt._update_actual_pos()
        

class Page(BaseFrame):
    def __init__(self, tag: str):
        self._tag: str = tag
        self._page_tag = tag
        self._actual_pos = Vector2(0, 0)
        self._size = Vector2(PageManager._screen.get_size())
        self._active = True
        self.visible = True

        PageManager._add_page(self)

        self._elements: List[Element] = []
        self._event_funcs: List[List[Callable[[], None]]] = [[] 
                for _ in range(PageManager.NUMBER_EVENT_TYPES)]
    
    @property
    def tag(self) -> str:
        return self._tag

    def blit(self, surf: pygame.Surface, pos: Coordinate = Vector2(0,0)):
        PageManager._screen.blit(surf, pos)

    def on_open(self, *args, **kw):
        pass

    def on_close(self, *args, **kw):
        pass


class Widget(Element):
    def __init__(self, parent: BaseFrame, pos: Coordinate, size: Coordinate, **kw):
        self._background_color: Optional[Color] = None
        self._background_image: Optional[Surface] = None
        self._background_surf: Optional[Surface] = None

        super().__init__(parent, pos, size)

        self.config(**kw)

    @property
    def background(self) -> Optional[Surface]:
        return self._background_surf

    @property
    def background_color(self) -> Optional[Color]:
        return self._background_color
    
    @background_color.setter
    def background_color(self, new_color: Color):
        self._background_color = new_color
        if not self._background_image: 
            if not new_color is None:
                self._background_surf = Surface(vec2int(self.size))
                self._background_surf.fill(new_color[:3])
                if len(new_color) == 4:
                    self._background_surf.set_alpha(new_color[3])
    
    @property
    def background_image(self) -> Optional[Surface]:
        return self._background_image
    
    @background_image.setter
    def background_image(self, new_image: Surface):
        self._background_image = new_image
        self._background_surf = new_image
        if not rect_fit(new_image.get_size(), self.size):
            self.size = new_image.get_size()

    @property
    def size(self) -> Vector2: 
        return self._size

    @size.setter
    def size(self, new_size):
        self._size = Vector2(new_size)
        self._update_actual_pos()
        if not self._background_image and self._background_surf:
            pygame.transform.scale(self._background_surf, vec2int(new_size))
    
    def draw_background(self):
        if self._background_surf:
            self.blit(self._background_surf)
    

class Label(Widget):
    def __init__(self, parent: BaseFrame, pos: Coordinate, text: str, **kw):
        self._font: str = 'Arial'
        self._font_size: int = 28
        self._sys_font: pygame.font.Font = pygame.font.SysFont(self._font, self._font_size)
        self._text_color: Color = (0,0,0)
        self._text: str
        self._text_surf: Surface

        super().__init__(parent, pos, (1,1))

        self.text = text
        self.config(**kw)
    
    def _update_font(self):
        try:
            self._sys_font = pygame.font.SysFont(self._font, self._font_size)
        except:
            raise Exception('Invalid font')
        
        self._update_text_surf()
            
    def _update_text_surf(self):
        try:
            self._text_surf = self._sys_font.render(self._text, True, self._text_color)
            txt_size = self._text_surf.get_size()
            if not rect_fit(txt_size, self._size):
                self.size = txt_size
        except:
            raise Exception('Invalid text')

    @property
    def font(self) -> str:
        return self._font
    
    @font.setter
    def font(self, new_font):
        self._font = new_font
        self._update_font()
    
    @property
    def font_size(self) -> int:
        return self._font_size
    
    @font_size.setter
    def font_size(self, new_font_size: int):
        self._font_size = new_font_size
        self._update_font()
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, new_text: str) -> None:
        self._text = new_text
        self._update_text_surf()
    
    @property
    def text_color(self) -> Color:
        return self._text_color
    
    @text_color.setter
    def text_color(self, new_text_color):
        self._text_color = new_text_color
        self._update_text_surf()
    
    def draw(self):
        self.draw_background()
        self.blit(self._text_surf, centralized=True)


class Button(Element):
    def __init__(self, parent: BaseFrame, pos: Coordinate, size: Coordinate, 
            func: Callable[[], None], **kw):
        self._func = func
        super().__init__(parent, pos, size, **kw)

        self.bind(pygame.MOUSEBUTTONDOWN, self.on_click)
    
    def on_click(self, event):
        if self.active and self.on_mouse_focus():
            self._func()


class TextButton(Label):
    def __init__(self, parent: BaseFrame, pos: Coordinate, text: str, 
            func: Callable[[], None], **kw):
        self._func = func
        self._mouse_focus = False
        super().__init__(parent, pos, text)
        
        self.bind(pygame.MOUSEBUTTONDOWN, self.on_click)
        self.config(**kw)
    
    def on_click(self, event):
        if self.active and self.on_mouse_focus():
            self._func()


class Slider(Widget):
    def __init__(self, parent: BaseFrame, pos: Coordinate, **kw):
        self._value: int = 0
        self._scale = 1
        self._bar_width = 100
        self._sliding = False
        self._bar: Surface
        self._slider: Surface
        super().__init__(parent, pos, (100,25))

        self.bind(pygame.MOUSEBUTTONDOWN, self.on_click)
        self.bind(pygame.MOUSEBUTTONUP, self.on_button_up)
        self._update_surfs()
        self.config(**kw)

    def _update_surfs(self):
        self._bar = Surface((self._bar_width, int(5*self.scale)))
        self._slider = Surface(vec2int(Vector2(15,25)*self.scale))

    @property
    def value(self) -> float:
        return (self._bar_width - 15*self.scale)/self._value
    
    @value.setter
    def value(self, new_value: float) -> None:
        if new_value > 1 or new_value < 0:
            raise ValueError('Expected value between 0 and 1')
        self._value = int((self._bar_width - 15*self.scale)*new_value)

    @property
    def scale(self) -> float:
        return self._scale
    
    @scale.setter
    def scale(self, new_scale: float) -> None:
        self._scale = new_scale
        self._update_surfs() 
    
    @property
    def bar_width(self) -> int:
        return self._bar_width
    
    @bar_width.setter
    def bar_width(self, new_value: int) -> None:
        self._bar_width = new_value
        self._update_surfs()

    def on_click(self, event):
        if self.active and self.on_mouse_focus():
            self._sliding = True
            print('clickou')

    def on_button_up(self, event):
        self._sliding = False
        print('soltou')

    def update(self):
        if self._sliding:
            mouse_pos = self.mouse_pos()
            self._value = max(0, min(self._bar_width - 15*self.scale, mouse_pos[0] - int(7.5*self.scale)))

    def draw(self):
        self.blit(self._bar, (0, 10*self.scale))
        self.blit(self._slider, (self._value ,0))


class ButtonOnOff(Widget):
    def __init__(self, parent: BaseFrame, pos: Coordinate, **kw):
        self._scale: float = 1
        self._value: bool = False
        def func(): pass
        self._func = func

        super().__init__(parent, pos, (24,12), background_color=(240,0,0))
        
        self.bind(pygame.MOUSEBUTTONDOWN, self.on_click)
        self.config(**kw)

    @property
    def func(self) -> Callable:
        return self._func    

    @func.setter
    def func(self, new_func: Callable) -> None:
        self._func = new_func

    @property
    def value(self) -> bool:
        return self._value
    
    @value.setter
    def value(self, new_value: bool) -> None:
        self._value = new_value

    @property
    def scale(self) -> float:
        return self._scale
    
    @scale.setter
    def scale(self, new_scale: float) -> None:
        self._scale = new_scale
        self.size = Vector2(24,12)*self._scale

    def draw(self):
        if self._value:
            self.background_color = (0,240,0)
            rect = pygame.Rect(*(i*self._scale for i in (12, 1, 10, 10)))
        else:
            self.background_color = (240,0,0)
            rect = pygame.Rect(*(i*self._scale for i in (2, 1, 10, 10)))
        pygame.draw.rect(self._background_surf, (255,255,255), rect)
        self.draw_background()
        
    def on_click(self, event):
        if self.active and self.on_mouse_focus():
            self._value = not self._value
            self._func()

