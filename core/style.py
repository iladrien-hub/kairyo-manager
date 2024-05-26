from PyQt5.QtWidgets import QProxyStyle, QStyle


class KairyoStyle(QProxyStyle):

    def styleHint(self, hint, option=..., widget=..., returnData=...) -> int:
        if hint == QStyle.SH_MenuBar_AltKeyNavigation:
            return 0
        return super().styleHint(hint, option, widget, returnData)
