# Owner's Math reel generator

Data-driven 9:16 explainer reels (Kokoro TTS + Pillow + ffmpeg) and 1000x1500 Pinterest pins.

    pip install kokoro-onnx num2words pillow numpy
    # model files: github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0)
    KOKORO_DIR=/path/to/models python3 render.py week1 lm_ig1 out/
    python3 render.py week1 --pins out/pins

Content lives in a module like `week1.py`: every figure is tied to a named source,
and derived numbers are labelled "my math" on screen.
