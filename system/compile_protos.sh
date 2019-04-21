#!/bin/bash
#protoc -I=. --python_out=. proto/commit-protocol.proto
protoc -I=. --python_out=. two_phase_commit/proto/commit-protocol.proto

