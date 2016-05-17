import logging
import os.path


# Dict will be a directive i.e {"http":"{'server':["line"]}"}
# Start of a line will be preceded by on

class NginxConfUtils:
    def __index__(self, confloc):
        self.logging.getLogger("EnginXLink")
        self.target = open(name=confloc, mode='w')

    def write_directives_to_file(self, directives,tabs):
        self.target.write(directives)

    def write_block_to_file(self,block_dict,tabs):
        target = self.target

