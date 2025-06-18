from guardin_mind.manager import ConfigRead

class HelloWorld:
    def __init__(self):
        # Load configs
        ConfigRead(self) # Required code

    def func(self) -> str: # Function example
        print(self.name)
        print(self.version)
        print(self.description)
        print(self.authors)

        return "Hello World"