import colorsys
import os
from typing import Union

from .styling import Style, make_stylesheet


class DarkTheme(object):

    def __init__(
            self,
            *,
            accent_200: str,
            danger_200: str,
            success_200: str,
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
        self.danger_200 = danger_200
        self.success_200 = success_200
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
                'background-color': self.surface_300,
                'outline': 'none'
            }),
            Style('QLabel', {
                'color': self.text_200,
            }),
            Style('QLabel:disabled', {
                'color': self.text_100,
            }),
            Style('LabeledDivider > QFrame[frameShape="4"]', {
                'color': self.text_100,
            }),
            Style('QPushButton', {
                'background': f'qlineargradient(x1:0, y1:0, x2:0, y2:1, '
                              f'stop:0 {self.lighter_hex(self.surface_200, 2.5)}, '
                              f'stop:1 {self.surface_500})',
                'border': f'1px solid {self.surface_200}',
                'border-radius': '2px',
                'padding': '4px 15px',
                'color': self.text_200,
                'font-size': '11px',
            }),
            Style('QPushButton[accent="true"]', {
                'background': f'qlineargradient(x1:0, y1:0, x2:0, y2:1, '
                              f'stop:0 #3486e5, '
                              f'stop:1 #235b9b)',
                'font-weight': 'bold'
            }),
            Style('QPushButton:focus', {
                'border': f'1px solid {self.accent_200}',
            }),
            Style('QPushButton:disabled', {
                'border': f'1px solid {self.darker_hex(self.text_100, 1.7)}',
                'background': 'transparent',
                'color': self.darker_hex(self.text_100, 1.7)
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
            Style("TabButton", {
                'color': self.text_200,
                'background-color': self.surface_300,
                'border': 'none',
                'border-radius': '0',
                'padding': '4px 10px',
            }),
            Style("TabButton:checked", {
                'background-color': self.surface_200,
                'border': 'none',
            }),
            Style("TabButton:hover", {
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
            Style('QProgressBar ', {
                'border': 'none',
                'max-height': '4px',
                'background-color': self.surface_200
            }),
            Style('QProgressBar::chunk', {
                'background-color': self.accent_200
            }),
            Style('QLineEdit', {
                'background-color': self.surface_200,
                'border': f'1px solid {self.surface_50}',
                'padding': '4px'
            }),
            Style('QLineEdit:disabled', {
                'background-color': self.surface_300,
                'border': f'1px solid {self.surface_100}',
                'color': self.text_100
            }),
            Style('QLineEdit, QTextEdit', {
                'background-color': self.surface_200,
                'border': f'1px solid {self.surface_50}',
                'padding': '4px',
                'color': self.text_200
            }),
            Style('QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QComboBox:on', {
                'border': f'1px solid {self.accent_200}',
            }),
            Style('QSlider::groove', {
                'border': 'none',
                'background': self.surface_100
            }),
            Style('QSlider::groove:horizontal', {
                'height': '4px'
            }),
            Style('QSlider::groove:vertical', {
                'width': '4px'
            }),
            Style('QSlider::handle', {
                'background': self.accent_200,
                'height': '14px',
                'width': '14px',
                'border': f'2px solid {self.surface_300}',
                'border-radius': '9px'
            }),
            Style('QSlider::handle:disabled', {
                'background': self.surface_400,
            }),
            Style('QSlider::handle:horizontal', {
                'margin': '-7px 0px'
            }),
            Style('QSlider::handle:vertical', {
                'margin': '0px -7px'
            }),
            Style('FancySlider > QLabel', {
                'color': self.text_200
            }),
            Style('QComboBox', {
                'color': self.text_200,
                'padding': '4px 6px',
                'border': f'1px solid {self.surface_50}',
                'background': self.surface_200,
            }),
            Style('QComboBox:disabled', {
                'color': self.text_100,
                'border': f'1px solid {self.surface_100}',
                'background': self.surface_300,
            }),
            Style('QComboBox QAbstractItemView', {
                'color': self.text_200,
                'background': self.surface_200,
                'border': f'1px solid {self.surface_50}',
                'outline': 'none'
            }),
            Style('QComboBox QAbstractItemView::item', {
                'padding': '4px',
                'border': 'none'
            }),
            Style('QComboBox QAbstractItemView::item:hover', {
                'padding': '4px',
                'background-color': self.surface_400,
            }),
            Style('QComboBox::item', {
                'color': self.text_200,
            }),
            Style('QComboBox::drop-down', {
                'subcontrol-origin': 'padding',
                'subcontrol-position': 'center right',
                'width': '14px',
                'height': '14px',
                'background': 'transparent'
            }),
            Style('QComboBox::down-arrow', {
                'image': 'url(:/mainwindow/sort-down.svg)',
                'margin-right': '6px',
                'width': '8px',
                'height': '8px',
            }),
            Style('QCheckBox', {
                'color': self.text_200
            }),
            Style('QCheckBox::indicator', {
                'border': f'1px solid {self.surface_50}',
                'border-radius': '2px',
                'width': '12px',
                'height': '12px',
                'padding': '2px'
            }),
            Style('QCheckBox::indicator:focus', {
                'border': f'1px solid {self.accent_200}',
            }),
            Style('QCheckBox::indicator:checked', {
                'image': 'url(:/mainwindow/check.svg)',
            }),
            Style('QTreeView', {
                'border': 'none',
                'color': self.text_200,
                'font-weight': 'bold',
            }),
            Style('QTreeView::item', {
                'padding': '4px 0px',
                'color': self.text_200,
            }),
            Style('QTreeView::item:hover', {
                'background': 'transparent',
            }),
            Style('QTreeView::item:selected', {
                'background': self.surface_400,
            }),
            Style('QTreeView::branch:selected', {
                'background': self.surface_400,
            }),
            Style(
                'QTreeView::branch:has-children:!has-siblings:closed, '
                'QTreeView::branch:closed:has-children:has-siblings', {
                    'padding': '7px',
                    'border-image': 'none',
                    'image': 'url(:/mainwindow/chevron-right.svg)',
                }
            ),
            Style(
                'QTreeView::branch:open:has-children:!has-siblings, '
                'QTreeView::branch:open:has-children:has-siblings ', {
                    'padding': '5px',
                    'border-image': 'none',
                    'image': 'url(:/mainwindow/chevron-down.svg)',
                }
            ),
            Style('FileInput', {
                'qproperty-iconColor': self.text_100,
            }),
            # region: ProjectManager
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
            # region: progress-ext
            Style('QueueListWidget', {
                'border': 'none',
                'border-left': f'1px solid {self.surface_50}',
            }),
            Style('QueueItemWidget', {
                'border': 'none',
                'background': self.surface_300,
            }),
            Style('QueueItemWidget > QLabel#queueItemName', {
                'color': text_200,
            }),
            Style('QueueItemWidget > QLabel#queueItemDescription', {
                'color': text_100,
            }),
            Style('QueueListWidget > QListWidget', {
                'border': 'none',
                'background': self.surface_200
            }),
            Style('QueueListWidget > ToolBar', {
                'border': 'none',
                'border-bottom': f'1px solid {self.surface_50}',
            }),
            # endregion
            # region: Settings
            Style('SettingsWidget > QLabel', {
                'color': self.text_200,
                'font-weight': 'bold',
                # 'background': 'red'
            }),
            Style('SettingsFooter', {
                'border-top': f'1px solid {self.surface_50}',
            }),
            # endregion
        ]

    def make_stylesheet(self):
        return make_stylesheet(self.stylesheet, do_ident_closing_brace=False)

    @classmethod
    def from_palette(cls, shade: str, text: str, accent: str, danger: str, success: str):
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

        # danger
        res['danger_200'] = danger

        # success
        res['success_200'] = success

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
