from manim import *

class CircleScene(Scene):
    def construct(self):
        circle = Circle()           # Create a circle
        circle.set_fill(BLUE, opacity=0.5)  # Set the color and transparency
        self.play(Create(circle))   # Show the circle on screen
        self.wait(1)                # Pause for a second
