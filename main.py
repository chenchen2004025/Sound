import WaveProcess
import matplotlib.pyplot as plt
import numpy as np

def main():
    wave_data, time, frame_rate = WaveProcess.read_wave_data("..\\soundProgram\\20161121OneNorouxian.wav")
    wave_data = WaveProcess.pre_process(wave_data, time)
    wave_data2, frame_time= WaveProcess.enframe(wave_data[1,:], 1600, 400, time)
    frame_number = wave_data2.shape[0]
    voice_segment, SF, Ef = WaveProcess.pitch_valid(wave_data2, frame_number, 0.05)
    b = WaveProcess.np.array([0.012280, -0.039508, 0.042177, 0.000000, -0.042177, 0.039508, -0.012280])
    a = WaveProcess.np.array([1.000000, -5.527146, 12.854342 - 16.110307, 11.479789, -4.410179, 0.713507])
    xx = WaveProcess.my_filter(b, a, wave_data[1,:])
    yy = WaveProcess.enframe(wave_data[1,:], 1600, 400, time)
    frame_number = yy[0].shape[0]
    energy = []
    for i in range(0,frame_number):
        temp = np.abs(yy[0][i,:])
        energy.append(10 * np.sum(np.log10(temp ** 2)))
    # draw the wave
    pitch_min_cycle = np.fix(frame_rate/500)
    pitch_max_cycle = np.fix(frame_rate/60)
    period = np.zeros([1, frame_number])
    plt.subplot(111)
    #plt.plot(time, wave_data[0])
    plt.plot(energy)
    plt.show()
    plt.subplot(212)
    plt.plot(time, wave_data[1], c="g")
    plt.show()


if __name__ == "__main__":
    main()