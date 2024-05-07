import colorsys
import os
from typing import Union

from .styling import Style, make_stylesheet


class DarkTheme(object):

    def __init__(
            self,
            *,
            accent_200: str,
            surface_100: str,
            surface_200: str,
            surface_300: str,
            surface_400: str,
            surface_500: str,
            surface_600: str,
            text_100: str,
            text_200: str,
    ):
        self.accent_200 = accent_200
        self.surface_100 = surface_100
        self.surface_200 = surface_200
        self.surface_300 = surface_300
        self.surface_400 = surface_400
        self.surface_500 = surface_500
        self.surface_600 = surface_600
        self.text_100 = text_100
        self.text_200 = text_200

        self.stylesheet = [
            Style('*', {
                'background-color': self.surface_300
            }),
            Style('QMenu', {
                'background-color': self.surface_300,
                'border': f'1px solid {self.surface_500}'
            }),
            Style('QMenu::item', {
                'color': self.text_200,
            }),
            Style('QMenu::item:selected', {
                'background-color': self.accent_200,
            }),
            Style('QMenuBar::item', {
                'color': self.text_200
            }),
            Style('QMenuBar::item:selected, QMenuBar::item:pressed', {
                'background-color': self.accent_200
            }),
            Style("QPushButton#tabButton", {
                'color': self.text_200,
                'background-color': self.surface_300,
                'border': 'none',
                'border-radius': '0',
                'padding': '4px 10px',
            }),
            Style("QPushButton:checked#tabButton", {
                'background-color': self.surface_200,
                'border': 'none',
            }),
            Style("QPushButton:hover#tabButton", {
                'background-color': self.surface_200,
                'border': 'none',
            }),
            Style('QWidget#tabPaneNorth', {
                'border-bottom': f'1px solid {self.surface_100}'
            }),
            Style('QWidget#tabPaneSouth', {
                'border-top': f'1px solid {self.surface_100}'
            }),
            Style('QWidget#tabPaneEast', {
                'border-left': f'1px solid {self.surface_100}'
            }),
            Style('QWidget#tabPaneWest', {
                'border-right': f'1px solid {self.surface_100}'
            }),
            Style('QPushButton#titleBarMinimize, QPushButton#titleBarResize, QPushButton#titleBarClose', {
                'background-color': 'transparent',
                'border': 'none'
            }),
            Style('QPushButton:hover#titleBarMinimize, QPushButton:hover#titleBarResize', {
                'background-color': self.surface_400,
            }),
            Style('QPushButton:pressed#titleBarMinimize, QPushButton:pressed#titleBarResize', {
                'background-color': self.surface_600,
            }),
            Style('QPushButton:hover#titleBarClose', {
                'background-color': '#e81123',
            }),
            Style('QPushButton:pressed#titleBarClose', {
                'background-color': '#f1707a',
            }),
            Style('QFrame#titlebar', {
                'border-bottom': f'1px solid {self.surface_600}',
                'padding-bottom': '1px',
            }),
            Style('QLabel#appIcon', {
                'padding-left': '12px',
                'padding-right': '12px'
            }),
            Style('QLabel#appTitle', {
                'padding-left': '18px',
                'font-size': '11px',
                'color': self.text_100
            }),
            Style('QLabel:disabled#appTitle', {
                'color': self.darker_hex(self.text_100, 2)
            })
        ]

    def make_stylesheet(self):
        return make_stylesheet(self.stylesheet, do_ident_closing_brace=False)

    @classmethod
    def from_palette(cls, shade: str, text: str, accent: str):
        res = {}

        # surfaces
        hsv = cls.hex2hsv(shade)

        res['surface_100'] = cls.rgb2hex(cls.hsv2rgb(cls.darker(hsv, 1.2)))
        res['surface_200'] = shade
        res['surface_300'] = cls.rgb2hex(cls.hsv2rgb(cls.lighter(hsv, 1.2)))
        res['surface_400'] = cls.rgb2hex(cls.hsv2rgb(cls.lighter(hsv, 1.7)))
        res['surface_500'] = cls.rgb2hex(cls.hsv2rgb(cls.lighter(hsv, 2.0)))
        res['surface_600'] = cls.rgb2hex(cls.hsv2rgb(cls.lighter(hsv, 2.7)))

        # text
        hsv = cls.hex2hsv(text)
        res['text_100'] = cls.rgb2hex(cls.hsv2rgb(cls.darker(hsv, 1.5)))
        res['text_200'] = text

        # accent
        res['accent_200'] = accent

        return cls(**res)

    @classmethod
    def from_xml(cls, fn: Union[str, os.PathLike]):
        import xml.etree.ElementTree as Et

        root = Et.parse(fn).getroot()

        colors = {}

        for item in root:
            colors[item.tag] = item.text

        return cls.from_palette(**colors)

    @classmethod
    def hex2rgb(cls, hex_value):
        h = hex_value.strip("#")
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        return rgb

    @classmethod
    def rgb2hsv(cls, rgb):
        return colorsys.rgb_to_hsv(*(i / 255 for i in rgb))

    @classmethod
    def hsv2rgb(cls, hsv):
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(*hsv))

    @classmethod
    def hex2hsv(cls, hex_value):
        return cls.rgb2hsv(cls.hex2rgb(hex_value))

    @classmethod
    def darker(cls, hsv, f):
        return hsv[0], hsv[1], hsv[2] / f

    @classmethod
    def darker_hex(cls, hex_value, f):
        hsv = cls.hex2hsv(hex_value)
        return cls.rgb2hex(cls.hsv2rgb(cls.darker(hsv, f)))

    @classmethod
    def lighter(cls, hsv, f):
        return hsv[0], hsv[1], hsv[2] * f

    @classmethod
    def lighter_hex(cls, hex_value, f):
        hsv = cls.hex2hsv(hex_value)
        return cls.rgb2hex(cls.hsv2rgb(cls.lighter(hsv, f)))

    @classmethod
    def rgb2str(cls, rgb):
        return "rgb({}, {}, {})".format(*rgb)

    @classmethod
    def rgb2hex(cls, rgb):
        return '#%02x%02x%02x' % rgb
