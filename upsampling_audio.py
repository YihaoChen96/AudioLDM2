import os, shutil
import subprocess
from pydub import AudioSegment
from pydub.playback import play
from tempfile import NamedTemporaryFile


def find_wav_files(directory):
    wav_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".wav"):
                wav_files.append(os.path.join(root, file))
    return wav_files

# This is not working now because audioSR creates folders that prevents the script to get the actual file.
def chunk_and_process_audio(input_path, output_path, chunk_length_ms=5120):
    # Load the audio file
    audio = AudioSegment.from_file(input_path)

    # Calculate the number of chunks
    num_chunks = len(audio) // chunk_length_ms

    # Temporary files list
    temp_files = []

    # Process each chunk
    for i in range(num_chunks):
        chunk = audio[i * chunk_length_ms:(i + 1) * chunk_length_ms]

        # Create a temporary file for this chunk
        temp_chunk = NamedTemporaryFile(delete=False, suffix='.wav')
        temp_chunk_name = temp_chunk.name
        temp_files.append(temp_chunk_name)
        chunk.export(temp_chunk_name, format="wav")

        # Run the audiosr command
        processed_chunk_name = temp_chunk_name + "_processed"
        command = f"audiosr -i {temp_chunk_name} -s {processed_chunk_name}"
        subprocess.run(command, shell=True)

        # Replace the original chunk file with the processed one
        temp_files.append(processed_chunk_name)
        break

    # Combine the processed chunks
    combined = AudioSegment.empty()
    for fname in temp_files:
        if "_processed" in fname:
            wav_files = find_wav_files(fname) # Find the single output WAV file under the directory
            processed_chunk = AudioSegment.from_wav(wav_files[0])
            combined += processed_chunk

    # Export the combined audio
    combined.export(output_path, format="wav")

    # Clean up temporary files
    for fname in temp_files:
        if os.path.isdir(fname):
            shutil.rmtree(fname)
        elif os.path.isfile(fname):
            os.remove(fname)

if __name__ == '__main__':

    # Example usage
    input_wav_path = '/home/yihao/AudioLDM2/test16k.wav'  # Replace with your input WAV file path
    output_wav_path = '/home/yihao/AudioLDM2/test48k_chunked.wav'  # Replace with your desired output WAV file path

    chunk_and_process_audio(input_wav_path, output_wav_path)