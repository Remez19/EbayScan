import kivy
from kivy.app import App
from kivy.uix.label import Label


class NarkisApp(App):

    def build(self):
        # return a Button() as a root widget
        return Label(text='NARKIS', font_size=12)


if __name__ == '__main__':
    NarkisApp().run()