# Speaker notes

Beyond the Dropdown: Audio Codecs for Game Audio

## 1. Beyond the Dropdown

~30 sec. Introduce yourself. The promise: by the end, the codec dropdown in your middleware stops being a black box, and you leave with a framework you can apply on Monday.

## 2. About me

~30 sec. Keep it quick: game audio programming from Gas Powered Games to Call of Duty at High Moon to Riot today, with a detour through pro-audio plugins at Output. The point for this audience: you've worked with codecs from both the game runtime side and the music-software side.

## 3. Why this talk

~1 min. Why you're giving this talk. Having worked in both proprietary engines and commercial ones (Unreal, Wwise), you've seen the same gap in both: people pick a codec from a dropdown without knowing what it does. Then the framing: audio is a rendering problem, just like graphics. Every row on the right has a graphics twin: texture formats and codecs, frame budget and buffer deadline, VRAM and audio memory, mips/LOD and bitrate tiers, GPU-decoded textures and hardware audio decoders. Graphics programmers argue about BC7 vs ASTC in detail; audio should get the same rigor. [Optional: a specific moment where you saw this gap, e.g. a question a teammate asked or a bug that came from a default setting.]

## 4. What a codec setting affects

~1.5 min. Walk the five consequences quickly. Ask the room: who has changed codec settings per asset rather than per project? Usually few hands. That's the gap this talk fills.

## 5. The basics

Transition. About 8 minutes for this section: the render loop, the path of a voice, what uncompressed audio costs, the kinds of codec, how a perceptual codec works, and the vocabulary.

## 6. The audio render loop

~1 min. Get everyone on the same page: the audio engine doesn't produce one sample at a time. It renders a block (buffer) of samples, hands it to the device, and has to have the next one ready on time. 1,024 samples at 48 kHz is about 21.3 ms. Buffer sizes vary by platform and settings (roughly 256 to 2,048 samples), so say "typical." The graphics parallel from the motivation slide: a late video frame is a stutter; a late audio buffer is an audible glitch, which is why audio budgets are strict. Decode time comes out of this same window.

## 7. The path of one voice

~1.5 min. Top row: the path of one voice through the engine each buffer. A voice is one playing sound. The codec lives in the Decode step, turning compressed bytes back into PCM before anything else can touch it; resampling, effects, spatialization and mixing all work on PCM. Bottom row: the three places a source can live, which is the other half of the codec decision. Decoded in memory = pay RAM, no CPU. Compressed in memory = decode while playing, cost scales with voice count. Streamed = smallest footprint, but adds disk I/O and start-up latency. Engines name these differently (Wwise: in-memory vs. streamed; Unreal: loading behavior on the sound wave), but the tradeoff is the same. This sets up the decision framework later.

## 8. The cost of uncompressed audio

~2 min. Quick primer: sample rate is how often we measure, bit depth is how precisely, channels multiply it. 48 kHz × 16-bit × stereo = 1,536 kbps, about 11.5 MB a minute. Then multiply by variations, localized VO and platforms. That pressure is why codecs exist.

## 9. Three kinds of codec

~2 min. The mental model for the rest of the talk: every codec trades bits for something. Waveform coders spend quality, perceptual coders spend CPU and latency, lossless coders spend compression ratio. Keep that triangle in mind.

## 10. Inside a perceptual codec

~1.5 min. How Vorbis, Opus, AAC, XMA and ATRAC9 all work at heart. 1) Frame: chop the signal into overlapping blocks. 2) Transform: MDCT turns each block into frequency coefficients. 3) Quantize: a psychoacoustic model decides how coarsely each frequency band can be stored; this is the only step that throws information away. 4) Pack: entropy coding (Huffman or range coding) squeezes the numbers losslessly into the bitstream. Masking is why step 3 works: a loud tone hides quieter sounds near it in frequency, and briefly before and after it in time. Encoding is asymmetric by design: the encoder does the hard thinking offline, the decoder just reverses the steps (unpack, rescale, inverse transform, overlap-add), which ties back to the voice path slide. ADPCM skips all of this: it predicts each sample and stores the error in 4 bits.

## 11. Terms on the settings panel

~1.5 min. The vocabulary people will see in Wwise conversion settings or Unreal's sound wave compression panel. Bitrate: 1,536 kbps for stereo PCM vs. roughly 64 to 160 kbps for a perceptual codec. CBR/VBR: many tools expose a "quality" slider instead, which is VBR under the hood. Compression ratio: 1,536 kbps down to 128 kbps is 12:1. Frame size: bigger frames compress better but add latency and coarser seeking; Opus frames run 2.5 to 60 ms. Encoder delay (also called priming or pre-skip): the reason MP3 and AAC loops gap unless the tool trims it. Seek table: needed for starting mid-file, random-start ambiences and interactive music; it costs a little memory. These terms come back in the toolbox table and the checklist.

## 12. The problems codecs solve

Transition. About 7 minutes: why games needed codecs in the first place (samples, memory, voice chat, streaming, hardware), then a short history.

## 13. Sample-based audio

~1.5 min. The first problem. Early consoles made sound by synthesis: square waves, noise, FM. When hardware could play back recorded samples, audio suddenly needed memory, and there was almost none. The SNES had 64 KB of audio RAM for everything, so its samples were stored as BRR, an ADPCM-style format that packs 16 samples into 9 bytes (about 3.5:1). The PlayStation's sound chip had 512 KB and decoded 4-bit ADPCM on 24 voices; longer music and speech streamed from the CD as XA-ADPCM. The PS2 kept the same idea with 2 MB and 48 voices. By the Xbox 360, a perceptual codec (XMA) was decoded by the console's audio hardware. Hardware figures are from general knowledge; verify before presenting.

## 14. Memory and disk

~1 min. The second problem, and it never went away. All numbers here are computed: 100 MB holds 8.7 minutes of 48 kHz 16-bit stereo PCM (192 KB per second), about 35 minutes as 4:1 ADPCM, and about 104 minutes at 128 kbps. Dialogue: 10 hours of 48 kHz mono PCM is 3.46 GB; at 48 kbps Opus it is 216 MB, 16 times smaller. The 48 kbps figure is an example bitrate, not a recommendation. [Add: your own project's audio memory budget or VO hours, if you can share them.]

## 15. Voice chat

~1 min. The third problem. Voice chat became standard on console with Xbox Live in 2002. The codec has three jobs: low bitrate, because upstream bandwidth is shared with the game's own network traffic; low delay, with frames of 20 ms or less; and surviving packet loss, with concealment and forward error correction. Mono PCM at 48 kHz is 768 kbps; Opus speech at around 24 kbps is 32 times smaller (24 kbps is an example; apps vary). Lineage: Speex (2003) was the open speech codec of the 2000s; Skype's SILK and Xiph's CELT were merged into Opus in 2012, which is why Opus handles both speech and music.

## 16. Codecs in streaming

~1.5 min. Codecs matter well outside the game build. Contrast first: in a game, 'streaming' means reading a file from disk at a bitrate you chose at build time. Over a network, the codec has to cope with a connection that changes. Music services: Spotify's web player is AAC at 128 or 256 kbps and its lossless tier is FLAC (per Spotify's support page); its apps have long used Ogg Vorbis; Apple Music is AAC with ALAC for lossless; YouTube serves Opus and AAC. Video on demand: adaptive bitrate over HLS or DASH means the same audio is encoded at several bitrates and the player switches per segment; Netflix adopted xHE-AAC on mobile for exactly this, plus loudness management. Live streams: AAC is the usual ingest format, encoded in real time by OBS or the console. Voice: Opus, built for low delay and packet loss; WebRTC requires it. Cloud gaming: usually Opus, with audio sharing a tight delay budget with video and input. The cloud gaming row and the Vorbis and YouTube details are from general knowledge; confirm before presenting. The point for this audience: three codecs they will meet again in the toolbox section run most of the internet's audio.

## 17. Hardware

~1 min. The last problem: hardware limits. Dedicated decoders: from the PlayStation's sound chip to the Xbox 360's XMA hardware to AAC decoders in phones, moving decode off the CPU frees it for the game and saves power. Storage: optical discs seek slowly, so music and VO stream as compressed data, and cartridge and download sizes cap the total. Output links: optical S/PDIF only carries stereo PCM, so 5.1 over optical needs a live Dolby Digital or DTS encode (the original Xbox did this in real time); Bluetooth is narrower still. From general knowledge; verify specifics before presenting. [Add: a hardware constraint you've hit yourself.]

## 18. A short history

~1.5 min. Don't linger on dates. The arc: waveform coding (ADPCM) → perceptual coding (MP3, AAC) → royalty-free perceptual (Vorbis) → platform-native hardware codecs (XMA, ATRAC9) → a single flexible open codec (Opus). Dates: ADPCM research at Bell Labs early 1970s; MPEG-1 Layer III 1993; AAC 1997; Vorbis 1.0 2002; XMA with Xbox 360 2005; ATRAC9 with PS Vita 2011; Opus as RFC 6716 in 2012.

## 19. ADPCM and MP3

~1.5 min. ADPCM is 4 bits per sample, so a fixed 4:1, with trivial decode and exact random access. That's why it's still the default for footsteps, impacts, UI. MP3's frame-based encoder adds delay and padding, so loops click or gap unless your tools trim it; plus licensing until patents lapsed around 2017. Lesson carries forward: the ratio is only one column of the scorecard.

## 20. The modern toolbox

Transition. About 13 minutes for this section.

## 21. Codecs in use today

~2.5 min. This is the slide people photograph. Walk row by row but keep it brisk; the next slides go deeper on Opus vs Vorbis and the platform codecs. Unreal's sound asset options are Bink Audio, RAD Audio, ADPCM, PCM, Opus, Platform Specific and Project Defined; Vorbis is no longer a first-class choice there. Platform Specific maps to each console's native format and doesn't support seeking. Wwise column is from experience; double-check Opus/AAC/XMA/ATRAC9 availability against the Wwise version and platforms you ship on.

## 22. Vorbis and Opus

~2.5 min. Opus was built for real-time comms, which is why it's so strong on speech and at low bitrates; CELT handles music, SILK handles speech, and hybrid mode blends them. Vorbis is still perfectly good at higher bitrates and is everywhere. The honest framing: Opus is the better default for new work, but switching a shipped pipeline isn't free. [Add: your own listening-test results or bitrates if you have them.]

## 23. Platform codecs

~2 min. The pattern: platform codecs win on decode cost because hardware or a tuned native decoder does the work, and lose on portability. On console, that freed CPU can mean more simultaneous voices. [Check and state current-gen specifics for your platforms here; these vary by console generation and SDK, and some details are under NDA.]

## 24. Codecs you didn't choose

~1 min. Your mix is rarely the last encode. Bluetooth headsets re-encode the final mix (SBC, AAC, aptX, LDAC; LE Audio standardizes on LC3) and add latency. TVs and soundbars: when a console is set to bitstream output, it encodes the mix live as Dolby Digital or DTS. Capture, livestreams and cloud gaming encode it again as AAC or Opus. Each lossy generation compounds artifacts (tandem coding), so a mix that's already squeezed hard in-engine can fall apart downstream. [Optional: a personal example, e.g. hearing your mix through a Bluetooth headset or on a stream.]

## 25. Choose a codec per asset class, not per project.

~30 sec. Pause here. This is the one sentence you want people to repeat. Footsteps, music, VO and ambience have different needs; one global setting serves none of them well.

## 26. A decision order

~3 min. The framework attendees take home. Walk an example asset through each question: a footstep stops at 1; a VO line stops at 2; a music stem stops at 3; and on a CPU-starved console, 4 can override 3. Emphasize the final step: numbers get you close, ears decide. [Optional: show a real before/after from your project here.]

## 27. What to measure

~2 min. A checklist version of the framework, for people who want to audit an existing project. Don't read every card; pick the two that bite most often (decode CPU at peak voices, and loop points).

## 28. The frontier

Transition. About 8 minutes for this section. Set expectations: we're separating what's useful now from what's research.

## 29. Apple's APAC

~2.5 min. APAC quietly appeared in iOS 13 / macOS Catalina and was formally defined with iOS 18 (iPhone 16 spatial capture). At WWDC25 Apple introduced ASAF, delivered as APAC, and made APAC required for Apple Immersive Video on Vision Pro. Apple's spec covers scene-based (Ambisonics) and channel layouts, HLS segmentation, and embedded loudness/DRC metadata. The 768 kbps ceiling is from press coverage, not Apple's spec; say "reported". Honest take: a delivery codec for pre-rendered spatial content, not a replacement for your runtime codec. Sources: Apple's APAC developer PDF; WWDC25 coverage.

## 30. Neural codecs

~2.5 min. Instead of hand-designed transforms and psychoacoustic models, an encoder network learns a compact representation; residual vector quantization turns it into discrete tokens; a decoder network reconstructs audio. Bitrates are tiny compared with classic codecs. The tokens are also what many generative audio models are built on, which is part of why this research moves so fast. Double-check the exact bitrate ranges against the papers before presenting.

## 31. Language models in codecs

~1.5 min. Neural codecs turn audio into discrete tokens, and tokens are what language models predict. That connects the two fields in two directions. First, a language model inside the codec: EnCodec's paper reports that a lightweight Transformer compresses its output by up to 40% more while staying faster than real time; LMCodec (Google, 2023) is causal and uses one Transformer to generate the fine tokens from the coarse ones, so they never need to be sent, and another to drive entropy coding. Second, a codec built as the tokenizer for a language model: Mimi is the codec inside Kyutai's Moshi (2024), running at 12.5 frames per second and about 1.1 kbps, with the first codebook carrying meaning; Moshi's paper reports 160 ms theoretical and 200 ms practical latency. ZipCodec (arXiv, September 2026) pushes to 0.80 kbps at 6.25 frames per second with an 842M-parameter model, real-time for one stream on a consumer CPU. The Mimi frame rate and bitrate are from memory of the paper; verify. Honest take for games: a generative decoder fills in plausible detail, which is risky when you need an actor's exact performance back; cost per stream is high; and nearly all of it is speech. Where it could matter is AI-driven character voices, where the model generates tokens directly and the codec is only the last stage.

## 32. Barriers in games

~2 min. The honest part. The killer is cost per voice: classic codecs decode many streams cheaply on CPU; a neural decoder runs a model per stream. Latency and training data are the next two. Determinism matters for replays, networking and QA. None of these are permanent, but together they explain why you won't see a neural codec in your middleware dropdown for a while.

## 33. Where neural audio shows up first

~2 min. Now: Opus 1.5 (March 2024) added ML features, Deep Redundancy (DRED) for packet-loss recovery and LACE/NoLACE decoder enhancement, so ML is already shipping inside a classic codec. Next: StreamCodec (2025 paper) reports 20 ms fixed latency, ~20× real time on CPU, a 7M-parameter model, at 1.5 kbps for 16 kHz speech. Speculative: clearly label this as opinion. If generative audio becomes common in games, storing tokens instead of waveforms could change how we think about asset budgets.

## 34. Takeaways

~1 min. Recap and hand off to Q&A.

## 35. Thank you

Q&A. Point to the QR codes: LinkedIn, email, GitHub. Likely questions: "What bitrate do you use for X?" (answer with your asset-class defaults), "Is Opus decode too heavy on Switch/mobile?" (profile at peak voice count), "When will neural codecs be in Wwise/FMOD?" (point back to the barriers slide).
