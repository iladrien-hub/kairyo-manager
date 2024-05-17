from PyQt5 import QtCore, QtGui


class Viewport(QtCore.QRect):

    def __init__(self):
        super().__init__()

        self.__scale = 1.0
        self.__pixmapSize = QtCore.QSize()

    def pixmapSize(self):
        return self.__pixmapSize

    def setPixmapSize(self, size: QtCore.QSize):
        self.__pixmapSize = size

    def scale(self):
        return self.__scale

    def setScale(self, new_scale: float, anchor: QtCore.QPoint = None):
        # update current scale and save the old one
        old_scale, self.__scale = self.__scale, new_scale
        # ensure scale in range [10%, 300%]
        self.__scale = max(min(self.__scale, 5.0), 0.1)

        # return if scale was not changed
        if old_scale == self.__scale:
            return

        # save the old center of the viewport and update its dimensions based on the scale and image size
        old_center = self.center()
        self.setSize(self.__pixmapSize * self.__scale)

        # Now for the tricky part...
        if anchor is not None:
            # When scaling, all distances in the image change their size.
            # Therefore, in order to fix a point on the image relative to the cursor position, you need to shift
            # the center of the image by the amount of scale.
            #
            # Find the vector between the point under the cursor and the OLD center of the viewport.
            # It's important to save this center before resizing, because it will change afterwards.
            vector = old_center - anchor

            # Next, we multiply this vector by the amount of scale change, which is expressed as the ratio of the new
            # value to the old one
            #
            # After that, we return this vector to the global coordinate system by adding it to the cursor position.
            # Voilà, the new center of the viewport.
            new_pos = anchor + vector * self.__scale / old_scale

            self.moveCenter(new_pos)
