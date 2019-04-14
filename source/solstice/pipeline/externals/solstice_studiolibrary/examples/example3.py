# An example for how to lock specific folders using the lockRegExp param

import solstice_studiolibrary


if __name__ == "__main__":

    # Use the solstice_studiolibrary.app context for creating a QApplication instance
    with solstice_studiolibrary.app():

        # Lock all folders that contain the words "icon" & "Pixar" in the path
        lockRegExp = "icon|Pixar"

        solstice_studiolibrary.main(name="Example3", path="data", lockRegExp=lockRegExp)
