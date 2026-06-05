# Strategy-lab image — own build, decoupled from the shared ../Freqtrade/Dockerfile.
#
# Base: freqtradeorg FreqAI-RL image (Freqtrade stable + torch/CUDA for GPU).
# Adds: pyzmq (sidecar messaging).
#
# pandas_ta is intentionally NOT installed here: it is unused in this repo, and
# its only PyPI releases (0.4.x) hard-pin numba==0.61.2, which cannot build on
# the base image's Python 3.14. Re-add it here once numba supports 3.14.
FROM freqtradeorg/freqtrade:stable_freqairl

# Switch to root to install packages
USER root

RUN pip install pyzmq

# Back to the unprivileged user
USER ftuser
