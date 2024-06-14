#!/bin/bash
ffmpeg -i http://172.23.0.190:8080/stream/video-15mbs.mkv -f null - -stats