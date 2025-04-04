class ColorPalette:
    def __init__(self, mode="light"):
        self.set_mode(mode)

    def set_mode(self, mode):
        """Sets the colors for light or dark mode."""
        if mode == "light":
            self.background = "#FEFEFE"  # White
            self.primary = "#3567DB"  # Blue
            self.text = "#030710"  # Black (cool-toned)

        elif mode == "dark":
            self.background = "#181818"  # Black
            self.primary = "#2353C5"  # Blue
            self.text = "#F0F4FC"  # White (cool-toned)


    def get_color(self, color_name):
        """Returns the color code based on the color name."""
        color_dict = {
            "primary": self.primary,
            "background": self.background,
            "text": self.text,

        }
        return color_dict.get(color_name, None)  # Return None if color is not found
