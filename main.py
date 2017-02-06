import WaveProcess
import matplotlib.pyplot as plt

def main():
    wave_data, time = WaveProcess.read_wave_data("..\\soundProgram\\20161121OneNorouxian.wav")
    wave_data = WaveProcess.pre_process(wave_data, time)
    wave_data2, frame_time= WaveProcess.enframe(wave_data[1,:], 1600, 400, time)
    frame_number = wave_data2.shape[0]
    voice_segment, SF, Ef = WaveProcess.pitch_valid(wave_data2, frame_number, 0.05)
    b = WaveProcess.np.array([0.012280, -0.039508, 0.042177, 0.000000, -0.042177, 0.039508, -0.012280])
    a = WaveProcess.np.array([1.000000, -5.527146, 12.854342 - 16.110307, 11.479789, -4.410179, 0.713507])
    xx = WaveProcess.my_filter(b, a, wave_data[1,:])
    yy = WaveProcess.enframe(xx, 1600, 400, time)
    frame_number = yy.shape[0]
    for i in range(0,frame_number):
        energy = WaveProcess.np.sum(10 * WaveProcess.np.log10(yy[i,:]*2))
    # draw the wave
    plt.subplot(211)
    plt.plot(time, wave_data[0])
    plt.subplot(212)
    plt.plot(time, wave_data[1], c="g")
    plt.show()


if __name__ == "__main__":
    main()