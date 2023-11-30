from diffusers import AudioLDM2Pipeline
import torch


model_id = "cvssp/audioldm2"
pipe = AudioLDM2Pipeline.from_pretrained(model_id, torch_dtype=torch.float16)

pipe.to("cuda")
generator = torch.Generator("cuda").manual_seed(0)

pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)

prompt = "The sound of Brazilian samba drums with waves gently crashing in the background"

audio = pipe(prompt, audio_length_in_s=10.24, generator=generator).audios[0]