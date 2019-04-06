#!/bin/bash
protoc -I=. --python_out=. proto/commit-protocol.proto
