import json
import os
import torch
import math
import logging
from TTS.api import TTS
import backend as bke

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s  - %(filename)s:%(lineno)d', datefmt='%y-%m-%d '
                                                                                                           '%I:%M:%S '
                                                                                                           '%p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def format_duration(seconds):
    if math.isnan(seconds):
        return '00:00:00,000'
    duration_str = ''
    try:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        duration_str = "{:02}:{:02}:{:02},{:03}".format(int(hours), int(minutes), int(seconds), int(milliseconds))
    except Exception as err:
        logger.error(f'The format_duration is not finished, f{err}.')
    finally:
        return duration_str


def convert_json_to_srt(fjson):
    jso = load_json(fjson)
    fsrt = f'{fjson}.srt'
    with open(fsrt, 'w', encoding='utf-8') as file:
        for idx, trans in enumerate(jso):
            lines = [str(idx + 1), '\n']
            # 1. no
            # 2. time
            start = format_duration(trans.get('start'))
            end = format_duration(trans.get('end'))
            time_str = f'{start} --> {end}'
            lines.append(time_str)
            lines.append('\n')
            # 3. text
            text = trans.get('text')
            lines.append(text)
            lines.append('\n')
            lines.append('\n')
            # 4. line break
            file.writelines(lines)


def load_json(fpath):
    # 读取 JSON 文件
    with open(fpath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # 现在变量 data 包含了 JSON 文件中的数据
    return data


def generate_wav(tts, fjson, wav_dir, speaker, lan='zh-cn'):
    jso = load_json(fjson)
    os.makedirs(wav_dir, exist_ok=True)
    pre_start = 0
    for idx, trans in enumerate(jso):
        out_wav = f'{wav_dir}/{idx:04}.wav'
        tts.tts_to_file(text=trans.get('text'),
                        file_path=out_wav,
                        speaker_wav=speaker,
                        language=lan)
        duration = trans.get('duration')
        streched_wav = f'{wav_dir}/{idx:04}.st.wav'
        bke.strech_wav(out_wav, duration, streched_wav)

        interval = trans.get('start') - pre_start
        white_noise = f'{wav_dir}/noise.wav'
        bke.generate_white_noise(white_noise, interval)

        bke.merge_wav(white_noise, streched_wav, streched_wav)

        pre_start = trans.get('end')


if __name__ == '__main__':
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts_eng = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    #
    in_file = 'input/Intro2LLM-cn.json'
    out = 'output'
    sp_wav = "input/lzl.wav"
    generate_wav(tts_eng, in_file, out, sp_wav)

    bke.concatenate_wav_files(out, 'output/output.wav')

    # json字幕转srt
    convert_json_to_srt(in_file)
