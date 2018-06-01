#!/usr/bin/env python
# encoding: utf-8

import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '../modules/python/'))
from NodeInterface import NodeInterface
from AudioAnalyzer import AudioAnalyzer

ni = NodeInterface()
aa = AudioAnalyzer(
	nodeInterface = ni,
	audioDir = os.path.join(sys.path[0], '../assets/audio/')
)
aa.play('drums-01.wav')