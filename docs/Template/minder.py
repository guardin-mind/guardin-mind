from guardin_mind.manager import ConfigRead

class Template:
    def __init__(self):
        # Load configs from minder_config.toml
        ConfigRead(self) # Required code

    def foo(self) -> str: # Function example
        print(self.name)
        print(self.version)
        print(self.description)
        print(self.authors)

        return "This is minder template"