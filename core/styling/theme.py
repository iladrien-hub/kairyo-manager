import colorsys
import os
from typing import Union

from .styling import Style, make_stylesheet


class DarkTheme(object):

    def __init__(
            self,
            *,
            accent_200: str,
            surface_50: str,
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
        self.surface_50 = surface_50
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
                'padding': '4px 8px',
                'min-width': '269px',
                'height': '13px'
            }),
            Style('QMenu::icon', {
                'padding-left': '12px'
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
                'border-bottom': f'1px solid {self.surface_50}'
            }),
            Style('QWidget#tabPaneSouth', {
                'border-top': f'1px solid {self.surface_50}'
            }),
            Style('QWidget#tabPaneEast', {
                'border-left': f'1px solid {self.surface_50}'
            }),
            Style('QWidget#tabPaneWest', {
                'border-right': f'1px solid {self.surface_50}'
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
                'padding-left': '0px',
                'font-size': '11px',
                'color': self.text_100
            }),
            Style('QLabel:disabled#appTitle', {
                'color': self.darker_hex(self.text_100, 2)
            }),
            Style('QScrollBar:vertical', {
                'background': self.surface_200,
                'width': '8px',
                'border': 'none',
                'border-radius': '0px'
            }),
            Style('QScrollBar::handle:vertical', {
                'background': self.hex2rgba(self.surface_500, 140),
                'width': '8px',
                'border': 'none'
            }),
            Style('QScrollBar::handle:vertical:hover', {
                'background': self.surface_500,
            }),
            Style('QScrollBar::handle:vertical:pressed', {
                'background': self.surface_500,
            }),
            Style('QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical', {
                'background': 'transparent',
                'border': 'none'
            }),
            Style('QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical', {
                'background': 'transparent',
                'border': 'none'
            }),
            Style('QToolButton', {
                'background': 'transparent',
                'border': 'none',
                'border-radius': '2px',
                'padding': '4px',
            }),
            Style('QToolButton:hover', {
                'background': self.hex2rgba(self.surface_500, 127),
            }),
            Style('QToolButton:pressed', {
                'background': self.hex2rgba(self.surface_500, 175),
            }),
            Style('QToolButton::menu-indicator', {
                'image': 'none',
            }),
            Style('QToolTip', {
                'color': self.text_200,
                'background-color': self.surface_400,
                'border': f'1px solid {self.surface_500}',
            }),
            # region ProjectManager
            Style('QListWidget#projectImageList', {
                'border': 'none',
                'border-right': f'1px solid {self.surface_50}',
                'background': self.surface_200,
                'color': self.text_200
            }),
            Style('QFrame#imageListToolbar', {
                'border': 'none',
                'border-right': f'1px solid {self.surface_50}',
                'border-bottom': f'1px solid {self.surface_50}',
                'background': self.surface_300,
                'color': self.text_200
            }),
            Style('QFrame#imageHistoryView', {
                'border-left': f'1px solid {self.surface_50}',
                'border-top': f'1px solid {self.surface_50}',
            }),
            Style('QListWidget#commitsList', {
                'border': 'none',
                'background': self.surface_200,
                'color': self.text_200
            }),
            Style('SnapshotItemWidget > QLabel', {
                'color': self.text_200,
                'padding': '0px 4px',
                'background': '#464a4d',
                'font-family': 'Consolas',
            }),
            Style('SnapshotItemWidget > QLabel:hover', {
                'background': self.lighter_hex('#464a4d', 1.3)
            }),
            Style('SnapshotItemWidget[selected="true"] > QLabel', {
                'background': self.accent_200
            }),
            Style('PreviewGraphicsWidget', {
                'border': 'none',
                'border-left': f'1px solid {self.surface_50}',
                'background': self.surface_100
            }),
            Style('HistoryInfoBox', {
                'border': 'none',
                'border-right': f'1px solid {self.surface_50}',
                'background': self.surface_200,
                'font-size': '14px'
            }),
            # endregion
        ]

    def make_stylesheet(self):
        return make_stylesheet(self.stylesheet, do_ident_closing_brace=False)

    @classmethod
    def from_palette(cls, shade: str, text: str, accent: str):
        res = {}

        # surfaces
        hsv = cls.hex2hsv(shade)

        res['surface_100'] = cls.rgb2hex(cls.hsv2rgb(cls.darker(hsv, 1.2)))
        res['surface_50'] = cls.darker_hex(res['surface_100'], 1.1)
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

    @classmethod
    def hex2rgba(cls, hex_value, alpha):
        return "rgb({}, {}, {}, {})".format(*cls.hex2rgb(hex_value), alpha)
