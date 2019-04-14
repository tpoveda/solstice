# Copyright 2017 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import solstice_studiolibrary


def main(*args, **kwargs):
    """
    Convenience method for creating/showing a MayaLibraryWidget instance.

    return solstice_studiolibrarymaya.MayaLibraryWidget.instance(
        name="",
        path="",
        show=True,
        lock=False,
        superusers=None,
        lockRegExp=None,
        unlockRegExp=None
    )

    :rtype: solstice_studiolibrarymaya.MayaLibraryWidget
    """
    import solstice_studiolibrarymaya

    solstice_studiolibrarymaya.registerItems()
    solstice_studiolibrarymaya.enableMayaClosedEvent()

    if solstice_studiolibrary.isMaya():
        import solstice_studiolibrarymaya.mayalibrarywidget
        cls = solstice_studiolibrarymaya.mayalibrarywidget.MayaLibraryWidget
    else:
        cls = solstice_studiolibrary.LibraryWidget

    libraryWidget = cls.instance(*args, **kwargs)

    return libraryWidget


if __name__ == "__main__":

    # Run the Studio Library in a QApplication instance
    with solstice_studiolibrary.app():
        main()
