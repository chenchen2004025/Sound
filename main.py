import WaveProcess
import matplotlib.pyplot as plt
import numpy as np
import web
from handle import Handle

urls = (
    '/wx', 'Handle',
)


def main():
    WaveProcess.pitch_valid_main("..\\soundProgram\\")

if __name__ == "__main__":
    #main()
    app = web.application(urls, globals())
    app.run()