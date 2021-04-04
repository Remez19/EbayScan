from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.colorpicker import ColorPicker

Builder.load_file('kivyViews/Narkis.kv')


class Narkis(Widget):
    pass


class NarkisApp(App):
    def build(self):
        # return a Button() as a root widget
        return Narkis()


if __name__ == '__main__':
    NarkisApp().run()
