# Speaker notes

From ADPCM to AI: The Past, Present and Future of Game Audio Codecs

## 1. From ADPCM to AI

~30 sec. Name and title only; the bio is the next slide. The promise: by the end, the codec dropdown in your middleware stops being a black box, and you leave with a framework you can apply on Monday.

## 2. About me

~30 sec. Keep it quick: Unity and Wwise at Gas Powered Games, proprietary engine tech on Call of Duty at High Moon, and Unreal Audio and Wwise at Riot today. The point for this audience: you've dealt with codecs in both commercial middleware and proprietary engines, which sets up the next slide.

## 3. Why this talk

~45 sec. Why you're giving this talk. Codec tech can feel intimidating, especially on a team without a big audio programming group: people pick one from a dropdown without knowing what it does, yet that choice has a real impact on the project. You've seen this in both proprietary engines and commercial ones (Unreal, Wwise). Then the roadmap in five beats: how codecs work, the problems they solve, how they came about, how they're used today, and how they might be used in the near future. End on the promise: they leave with a better understanding, and a decision order they can apply to their own project on Monday. The next slide is a real example of that: Titanfall. [Optional: a specific moment where you saw this gap, e.g. a question a teammate asked or a bug that came from a default setting.]

## 4. A tradeoff in the wild: Titanfall

~1 min. A real example of a codec decision shaping how a game ships and runs. Titanfall shipped on PC in March 2014 with a 48 GB install, and 35 GB of that was uncompressed audio. Respawn's lead engineer Richard Baker told Eurogamer why: decoding compressed audio costs CPU, and on a two-core minimum-spec PC they couldn't spare it. He also said it would not have been an issue on a mid-range or high-end PC. So they traded disk for CPU: file size got much worse so that decode cost could go to zero. The point is not that it was right or wrong; it was a deliberate choice that moved file size, CPU cost and the min-spec experience all at once. The basics section comes back to the general version of that tradeoff. Source: The Escapist, 14 March 2014, reporting on a Eurogamer interview: https://www.escapistmagazine.com/titanfall-dev-explains-the-games-35-gb-of-uncompressed-audio/

## 5. The basics

Transition. About 16 minutes for this section: what raw PCM is, how big it gets and why streaming it from disk or over a network is hard, codec basics and the kinds of codec, what a codec setting affects, the path of a voice, and how a perceptual codec works. Then the problems codecs had to solve in games: samples, memory, voice chat, streaming and hardware.

## 6. Raw PCM audio

~1 min. Start from zero. Raw PCM (pulse-code modulation) is the waveform written down as numbers: it is what a WAV file holds, and what the mixer works on. Three settings define it. Sample rate is how often the wave is measured, bit depth is how precisely each measurement is stored, and channel count is how many waveforms play together. The diagram shows the grey wave, the dots where it is measured, and each dot rounded to the nearest level (real 16-bit audio has 65,536 levels, far too fine to draw). Nothing is thrown away, which is why PCM is the quality reference, and also why it is huge. The next slide puts numbers on that.

## 7. The cost of PCM: memory

~1.5 min. How massive it gets. Multiply the three settings from the previous slide: 48 kHz × 16-bit × stereo = 1,536 kbps. Divide by 8 for bytes: 192 KB every second, 11.5 MB a minute, 691 MB an hour; 5.1 has six channels, so 576 KB a second and 2.07 GB an hour. Sizes here use decimal units (1 MB = 1,000,000 bytes); in the binary units Windows shows, a minute is 11.0 MB and an hour is 659 MB. Then multiply by variations, localized VO and platforms. For scale: the PlayStation 2 launched in 2000 with 2 MB of sound RAM for everything a game had loaded. One minute of today's 48 kHz 16-bit stereo PCM is 11.5 MB, more than five times that (about 5.5×), and the PS2's sound RAM would hold only about 11 seconds of it (its 2 MB is 2,097,152 bytes, at 192,000 bytes per second). The PS2 itself stored 4-bit ADPCM, which comes back later in this section. This is also how Titanfall reached 35 GB of audio. The next slide covers the usual workaround, streaming, and why it only moves the problem.

## 8. The cost of PCM: streaming

~1.5 min. "Streaming" means two different things in games, and raw PCM is a problem for both. First, from disk: the obvious answer to "PCM is too big for RAM" is to read it from disk as it plays. That fixes RAM and not much else. One stereo stream of 48 kHz 16-bit PCM is a constant 192 KB per second; eight of them (music layers, ambiences, a VO line) is about 1.5 MB per second on the same I/O queue the game uses for textures and geometry. On hard drives and optical discs the bigger cost is seeking between streams. Each stream also needs a RAM buffer (2 seconds of stereo PCM is 384 KB), and a late read is an audible dropout. Disk and patch size are unchanged: this is the Titanfall trade from the intro, 35 GB of audio in exchange for zero decode CPU. Second, over a network: voice chat, livestreams, cloud gaming. One mono voice at 48 kHz 16-bit is 768 kbps, and every talker sends that upstream alongside the game's own traffic. A 20 ms frame of mono PCM is 1,920 bytes (960 samples at 2 bytes each), more than the roughly 1,500 bytes a typical internet packet carries, so every frame is split across packets and is easier to lose. PCM has no built-in way to hide a lost packet, and no way to drop to a lower bitrate when the connection gets worse. Speech codecs are designed for exactly those two things; the voice chat slide comes back to this. The eight-stream figure is an illustration, not a measurement, and the 1,500-byte packet size is from general knowledge; verify before presenting. [Add: your own project's typical stream count, or a streaming problem you have hit.]

## 9. Codec basics

~2.5 min. Shared vocabulary, nothing more. The goal is that everyone in the room can follow the rest of the talk, whether or not they write code. A codec is a coder plus a decoder. For game assets the encode happens once, on a build machine, and the decode happens on the player's device every time the sound plays, which is why decode cost matters far more than encode cost. (Voice chat is the exception: it encodes live.) Then the kinds. Lossless (FLAC) predicts each sample and stores the error exactly, so everything comes back but the savings are modest. Lossy codecs come in two families. Predictive ones like ADPCM do the same prediction but store only a rough, 4-bit version of the error: a fixed 4:1, a little noise, and almost no CPU to decode. Perceptual ones like Vorbis, Opus and AAC move to the frequency domain and spend bits according to what the ear can hear, so they get much smaller and cost more CPU and latency. The mental model for the rest of the talk: every codec trades bits for something. Bitrate: 1,536 kbps for stereo PCM against roughly 64 to 160 kbps for a perceptual codec; 128 kbps works out to about 1 MB a minute, a compression ratio of 12:1. Many tools show a "quality" slider instead of a bitrate, which is variable bitrate under the hood: more bits where the sound is busy. Three more terms come up later and are easier to explain where they matter: frame size (samples per coded block; it sets latency and how finely playback can seek), encoder delay (extra samples at the start; left untrimmed, they break seamless loops) and seek tables (an index so playback can start mid-file).

## 10. What a codec setting affects

~1.5 min. After the size of raw PCM and the limits of streaming it, that pressure is why codecs exist. This is the general version of the Titanfall trade. Start with the question to the room: who has changed codec settings per asset rather than per project? Usually few hands. Then walk the five consequences quickly. That's the gap this talk fills.

## 11. The path of one voice

~1.5 min. Top row: the path of one voice through the engine each buffer. A voice is one playing sound. (The engine produces audio in small blocks called buffers, typically 1,024 samples, about 21 ms at 48 kHz, and every step here has to finish inside that time or players hear a click or dropout.) The codec lives in the Decode step, turning compressed bytes back into PCM before anything else can touch it; resampling, effects, spatialization and mixing all work on PCM. Bottom row: the three places a source can live, which is the other half of the codec decision. Decoded in memory = pay RAM, no CPU. Compressed in memory = decode while playing, cost scales with voice count. Streamed = smallest footprint, but adds disk I/O and start-up latency. Engines name these differently (Wwise: in-memory vs. streamed; Unreal: loading behavior on the sound wave), but the tradeoff is the same. This sets up the decision framework later.

## 12. Inside a perceptual codec

~1.5 min. How Vorbis, Opus, AAC, XMA and ATRAC9 all work at heart. 1) Frame: chop the signal into overlapping blocks. 2) Transform: MDCT turns each block into frequency coefficients. 3) Quantize: a psychoacoustic model decides how coarsely each frequency band can be stored; this is the only step that throws information away. 4) Pack: entropy coding (Huffman or range coding) squeezes the numbers losslessly into the bitstream. Masking is why step 3 works: a loud tone hides quieter sounds near it in frequency, and briefly before and after it in time. Encoding is asymmetric by design: the encoder does the hard thinking offline, the decoder just reverses the steps (unpack, rescale, inverse transform, overlap-add), which ties back to the voice path slide. ADPCM skips all of this: it predicts each sample and stores the error in 4 bits.

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

## 18. The past

Transition. About 3 minutes for this section: a short history of the codecs games have used, then what ADPCM and MP3 left behind.

## 19. A short history

~1.5 min. Don't linger on dates. The arc: predictive coding (ADPCM) → perceptual coding (MP3, AAC) → royalty-free perceptual (Vorbis) → platform-native hardware codecs (XMA, ATRAC9) → a single flexible open codec (Opus). Dates: ADPCM research at Bell Labs early 1970s; MPEG-1 Layer III 1993; AAC 1997; Vorbis 1.0 2002; XMA with Xbox 360 2005; ATRAC9 with PS Vita 2011; Opus as RFC 6716 in 2012.

## 20. ADPCM and MP3

~1.5 min. ADPCM is 4 bits per sample, so a fixed 4:1, with trivial decode and exact random access. That's why it's still the default for footsteps, impacts, UI. MP3's frame-based encoder adds delay and padding, so loops click or gap unless your tools trim it; plus licensing until patents lapsed around 2017. Lesson carries forward: the ratio is only one column of the scorecard. Fun aside: ADPCM is also alive in emulation. A PlayStation emulator has to re-implement the console's sound chip, ADPCM decoder included, to play the original game data; jsgroth's blog post on the PS1 SPU walks through it: https://jsgroth.dev/blog/posts/ps1-spu-part-1/ [Skim the post before presenting so you can describe what it covers.]

## 21. The modern toolbox

Transition. About 13 minutes for this section.

## 22. Codecs in use today

~2.5 min. This is the slide people photograph. Walk row by row but keep it brisk; the next slides go deeper on Opus vs Vorbis and the platform codecs. Unreal's sound asset options are Bink Audio, RAD Audio, ADPCM, PCM, Opus, Platform Specific and Project Defined; Vorbis is no longer a first-class choice there. Platform Specific maps to each console's native format and doesn't support seeking. Wwise column is from experience; double-check Opus/AAC/XMA/ATRAC9 availability against the Wwise version and platforms you ship on.

## 23. Vorbis and Opus

~2.5 min. Opus was built for real-time comms, which is why it's so strong on speech and at low bitrates; CELT handles music, SILK handles speech, and hybrid mode blends them. Vorbis is still perfectly good at higher bitrates and is everywhere. The honest framing: Opus is the better default for new work, but switching a shipped pipeline isn't free. [Add: your own listening-test results or bitrates if you have them.]

## 24. Platform codecs

~2 min. The pattern: platform codecs win on decode cost because hardware or a tuned native decoder does the work, and lose on portability. On console, that freed CPU can mean more simultaneous voices. [Check and state current-gen specifics for your platforms here; these vary by console generation and SDK, and some details are under NDA.]

## 25. Codecs you didn't choose

~1 min. Your mix is rarely the last encode. Bluetooth headsets re-encode the final mix (SBC, AAC, aptX, LDAC; LE Audio standardizes on LC3) and add latency. TVs and soundbars: when a console is set to bitstream output, it encodes the mix live as Dolby Digital or DTS. Capture, livestreams and cloud gaming encode it again as AAC or Opus. Each lossy generation compounds artifacts (tandem coding), so a mix that's already squeezed hard in-engine can fall apart downstream. [Optional: a personal example, e.g. hearing your mix through a Bluetooth headset or on a stream.]

## 26. Choose a codec per asset class, not per project.

~30 sec. Pause here. This is the one sentence you want people to repeat. Footsteps, music, VO and ambience have different needs; one global setting serves none of them well.

## 27. A decision order

~3 min. The framework attendees take home. Walk an example asset through each question: a footstep stops at 1; a VO line stops at 2; a music stem stops at 3; and on a CPU-starved console, 4 can override 3. Emphasize the final step: numbers get you close, ears decide. [Optional: show a real before/after from your project here.]

## 28. What to measure

~2 min. A checklist version of the framework, for people who want to audit an existing project. Don't read every card; pick the two that bite most often (decode CPU at peak voices, and loop points).

## 29. The frontier

Transition. About 12 minutes for this section. Set expectations: we're separating what's useful now from what's research.

## 30. Apple's APAC

~2.5 min. APAC quietly appeared in iOS 13 / macOS Catalina and was formally defined with iOS 18 (iPhone 16 spatial capture). At WWDC25 Apple introduced ASAF, delivered as APAC, and made APAC required for Apple Immersive Video on Vision Pro. Apple's spec covers scene-based (Ambisonics) and channel layouts, HLS segmentation, and embedded loudness/DRC metadata. The 768 kbps ceiling is from press coverage, not Apple's spec; say "reported". Honest take: a delivery codec for pre-rendered spatial content, not a replacement for your runtime codec. Sources: Apple's APAC developer PDF; WWDC25 coverage.

## 31. QOA: the Quite OK Audio format

~1.5 min. The frontier is not only neural. QOA (Quite OK Audio) goes the other way: a deliberately simple time-domain codec in the ADPCM tradition, by Dominic Szablewski, who also made the QOI image format. Twenty samples of 16-bit PCM go into one 64-bit slice: a 4-bit scale factor and twenty 3-bit residuals, predicted with a 4-tap LMS filter. That is 3.2 bits per sample, a fixed 5:1 (ADPCM is 4 bits per sample, 4:1). At 48 kHz stereo that works out to about 310 kbps once frame headers are included. The project site quotes 278 kbit/s for 44.1 kHz stereo, which is the same arithmetic counted in units of 1,024 bits. The author's claims are better quality than ADPCM and decoding about 3× faster than Ogg Vorbis. The reference encoder and decoder are about 400 lines of C under the MIT licence, and the spec is a single page. Adoption so far is in open-source projects: Godot 4.3 and later, raylib, and a range of players and language ports. Honest take: a possible ADPCM replacement for short SFX, not a competitor to Opus for music or VO, because the ratio is fixed. Caveats: the quality and speed figures are the author's own, not independent measurements, and the README warns that the reference implementation has not been fuzzed, so it should not be fed untrusted input. I did not find QOA in Wwise, FMOD or Unreal, but did not check exhaustively; verify before saying so on stage. The QOI connection is from general knowledge. Sources: https://github.com/phoboslab/qoa and https://qoaformat.org/

## 32. Neural codecs

~2.5 min. Instead of hand-designed transforms and psychoacoustic models, an encoder network learns a compact representation; residual vector quantization turns it into discrete tokens; a decoder network reconstructs audio. Bitrates are tiny compared with classic codecs. The tokens are also what many generative audio models are built on, which is part of why this research moves so fast. Double-check the exact bitrate ranges against the papers before presenting.

## 33. Language models in codecs

~1.5 min. Neural codecs turn audio into discrete tokens, and tokens are what language models predict. That connects the two fields in two directions. First, a language model inside the codec: EnCodec's paper reports that a lightweight Transformer compresses its output by up to 40% more while staying faster than real time; LMCodec (Google, 2023) is causal and uses one Transformer to generate the fine tokens from the coarse ones, so they never need to be sent, and another to drive entropy coding. Second, a codec built as the tokenizer for a language model: Mimi is the codec inside Kyutai's Moshi (2024), running at 12.5 frames per second and about 1.1 kbps, with the first codebook carrying meaning; Moshi's paper reports 160 ms theoretical and 200 ms practical latency. ZipCodec (arXiv, September 2026) pushes to 0.80 kbps at 6.25 frames per second with an 842M-parameter model, real-time for one stream on a consumer CPU. The Mimi frame rate and bitrate are from memory of the paper; verify. Honest take for games: a generative decoder fills in plausible detail, which is risky when you need an actor's exact performance back; cost per stream is high; and nearly all of it is speech. Where it could matter is AI-driven character voices, where the model generates tokens directly and the codec is only the last stage.

## 34. Barriers in games

~2 min. The honest part. The killer is cost per voice: classic codecs decode many streams cheaply on CPU; a neural decoder runs a model per stream. Latency and training data are the next two. Determinism matters for replays, networking and QA. None of these are permanent, but together they explain why you won't see a neural codec in your middleware dropdown for a while.

## 35. Opus 1.6: neural tools inside a classic codec

~2 min. After the barriers, the path that is actually shipping: neural networks helping a classic codec instead of replacing it. Opus 1.6 was released on December 15, 2025 and stays fully compatible with RFC 6716, the 2012 standard. Four things to mention. One, speech bandwidth extension (BWE): Opus codes speech as wideband (0 to 8 kHz) at low bitrates, and a neural network on the decoder side generates the 8 to 20 kHz band. It works on speech from any earlier Opus version. Combined with the NoLACE enhancer from 1.5, the Opus team reports that 9 kbps speech reaches similar quality to Opus 1.4 fullband at 18 kbps, and that at 9 kbps and above Opus now exceeds a purely neural codec like EnCodec. Those are the team's own listening-test results, so say so. Two, DRED (deep redundancy, the neural packet-loss recovery added in 1.5) is more robust to noisy and reverberant speech, and its models are about 3 times smaller: 600 kB, down from 1,800 kB. The new DRED model is not compatible with 1.5's, and the mismatch is handled gracefully. Three, Opus HD, experimental: 96 kHz audio with bandwidth beyond 20 kHz, bitrates up to 2 Mb/s, quantizer depth up to 20 bits. Four, a new 24-bit encode and decode API. For games: this matters first for voice chat. The neural pieces are opt-in (BWE needs the --enable-osce build option and a raised decoder complexity; Opus HD needs its own build option), so check what your middleware's Opus build actually enables. That extra decoder cost is an inference from those settings, not a number from the release notes. Source: https://opus-codec.org/demo/opus-1.6/

## 36. Where neural audio shows up first

~2 min. Now: Opus 1.5 (March 2024) added ML features, Deep Redundancy (DRED) for packet-loss recovery and LACE/NoLACE decoder enhancement, so ML is already shipping inside a classic codec; Opus 1.6 (December 2025, previous slide) added neural bandwidth extension on top. Next: StreamCodec (2025 paper) reports 20 ms fixed latency, ~20× real time on CPU, a 7M-parameter model, at 1.5 kbps for 16 kHz speech. Speculative: clearly label this as opinion. If generative audio becomes common in games, storing tokens instead of waveforms could change how we think about asset budgets.

## 37. Takeaways

~1 min. Recap and hand off to Q&A.

## 38. Thank you

Q&A. Point to the QR codes: LinkedIn, email, GitHub. Likely questions: "What bitrate do you use for X?" (answer with your asset-class defaults), "Is Opus decode too heavy on Switch/mobile?" (profile at peak voice count), "When will neural codecs be in Wwise/FMOD?" (point back to the barriers slide).
