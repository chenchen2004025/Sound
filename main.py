import WaveProcess
import matplotlib.pyplot as plt

def main():
    wave_data, time = WaveProcess.read_wave_data("..\\soundProgram\\20161121TwoSilent.wav")
    WaveProcess.pre_process(wave_data, time)
    # draw the wave
    plt.subplot(211)
    plt.plot(time, wave_data[0])
    plt.subplot(212)
    plt.plot(time, wave_data[1], c="g")
    plt.show()


if __name__ == "__main__":
    main()