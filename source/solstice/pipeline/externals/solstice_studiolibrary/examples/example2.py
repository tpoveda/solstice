# An example for creating a custom settings action

import solstice_studiolibrary


class CustomLibraryWidget(solstice_studiolibrary.LibraryWidget):

    def createSettingsMenu(self):
        """Reimplementing this method to add a custom action."""
        menu = super(CustomLibraryWidget, self).createSettingsMenu()

        menu.addSeparator()

        action = menu.addAction("Custom Action")
        action.triggered.connect(self.customActionClicked)

        return menu

    def customActionClicked(self):
        """Triggered when the custom action has been clicked."""
        print "Hello World"


if __name__ == "__main__":

    # Use the solstice_studiolibrary.app context for creating a QApplication instance
    with solstice_studiolibrary.app():

        w = CustomLibraryWidget.instance(name="Example2", path="data")
