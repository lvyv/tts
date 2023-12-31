import pyrubberband
import librosa
import soundfile as sf
import wave
import array
import math
import numpy as np
import os


def concatenate_wav_files(directory, output_path):
    # 获取目录中所有 WAV 文件的文件名
    wav_files = [f for f in os.listdir(directory) if f.endswith(".st.wav")]
    wav_files.sort()  # 按文件名顺序排序

    # 初始化总音频数据
    total_data = np.array([], dtype=np.int16)

    # 逐个拼接 WAV 文件
    for wav_file in wav_files:
        wav_path = os.path.join(directory, wav_file)
        with wave.open(wav_path, 'rb') as wav:
            params = wav.getparams()
            data = np.frombuffer(wav.readframes(params.nframes), dtype=np.int16)
            total_data = np.concatenate((total_data, data))

    # 创建输出 WAV 文件
    with wave.open(output_path, 'wb') as wav_out:
        # 设置输出 WAV 文件参数
        wav_out.setparams(params)
        # 写入拼接后的音频数据到输出 WAV 文件
        wav_out.writeframes(total_data.tobytes())


def merge_wav(input_path1, input_path2, output_path):
    # 打开第一个 WAV 文件
    with wave.open(input_path1, 'rb') as wav1:
        # 读取第一个 WAV 文件的参数
        params1 = wav1.getparams()
        # 读取第一个 WAV 文件的音频数据
        data1 = np.frombuffer(wav1.readframes(params1.nframes), dtype=np.int16)

    # 打开第二个 WAV 文件
    with wave.open(input_path2, 'rb') as wav2:
        # 读取第二个 WAV 文件的参数
        params2 = wav2.getparams()
        # 读取第二个 WAV 文件的音频数据
        data2 = np.frombuffer(wav2.readframes(params2.nframes), dtype=np.int16)

    # 确保两个文件的采样频率、通道数等参数一致
    assert params1.nchannels == params2.nchannels, "输入文件通道不同"
    assert params1.framerate == params2.framerate, "输入文件采样率不同"

    # 合并音频数据
    concatenated_data = np.concatenate((data1, data2))
    # 创建输出 WAV 文件
    with wave.open(output_path, 'wb') as wav_out:
        # 设置输出 WAV 文件参数
        wav_out.setparams(params1)
        # 写入合并后的音频数据到输出 WAV 文件
        wav_out.writeframes(concatenated_data.tobytes())
    return output_path


def generate_white_noise(output, dur, sample_rate=24000, amplitude=0.001):
    # 生成白噪音
    white_noise = amplitude * 32767.0 * np.random.uniform(-1.0, 1.0, int(sample_rate * dur))

    # 打开 WAV 文件
    with wave.open(output, 'w') as wav_file:
        # 设置 WAV 文件参数
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16 位采样
        wav_file.setframerate(sample_rate)
        wav_file.setnframes(int(sample_rate * dur))

        # 写入白噪音数据到 WAV 文件
        wav_file.writeframes(white_noise.astype(np.int16).tobytes())


def generate_sine_wav(output, dur, sample_rate=24000, frequency=440.0, amplitude=0.5):
    # 打开 WAV 文件
    with wave.open(output, 'w') as wav_file:
        # 设置 WAV 文件参数
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16 位采样
        wav_file.setframerate(sample_rate)
        wav_file.setnframes(int(sample_rate * dur))

        # 生成音频数据
        data = array.array('h',
                           [int(amplitude * 32767.0 * math.sin(2.0 * math.pi * frequency * t / sample_rate))
                            for t in range(int(sample_rate * dur))])

        # 写入音频数据到 WAV 文件
        wav_file.writeframes(data.tobytes())


def get_wav_duration(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        # 获取采样频率
        framerate = wav_file.getframerate()
        # 获取总帧数
        frames = wav_file.getnframes()
        # 计算时长（以秒为单位）
        dur = frames / float(framerate)
        return dur


def strech_wav(input_path, target_duration, target_path):
    origin = get_wav_duration(input_path)
    # 读取输入音频
    wav, arr = librosa.load(input_path, sr=None)
    factor = origin / target_duration
    stretched_wav = pyrubberband.time_stretch(wav, arr, factor)
    sf.write(target_path, stretched_wav, int(arr))
    return target_path


if __name__ == '__main__':
    # 输入音频文件路径
    input_file_path = 'tmp/0000.wav'
    # 读取输入音频
    # audio, sr = librosa.load(input_file_path, sr=None)
    # # 设定拉伸倍率（小于1表示压缩，大于1表示拉伸）
    # stretch_factor = 1.5
    # # 使用 pyrubberband 进行时间拉伸
    # stretched_audio = pyrubberband.time_stretch(audio, sr, stretch_factor)
    # # 保存输出音频文件
    # output_file_path = 'stretched_audio.wav'
    # sf.write(output_file_path, stretched_audio, sr)
    # print(f"Audio stretched by a factor of {stretch_factor}. Saved to {output_file_path}")

    # 示例用法
    output_file_path = 'output.wav'
    duration = 5.0  # 音频时长（秒）
    generate_sine_wav(output_file_path, duration)
    print(f"已生成 {output_file_path}，时长为 {duration} 秒")

    output_file_path = 'output2.wav'
    duration = 5.0  # 音频时长（秒）
    generate_white_noise(output_file_path, duration, amplitude=0.01)
    print(f"已生成 {output_file_path}，时长为 {duration} 秒")
