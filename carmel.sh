#!/bin/bash
sudo apt install libboost-dev
sudo apt install libboost-all-dev

git clone https://github.com/isi-nlp/carmel
cd carmel
mkdir build
cd build
cmake ..
make
make install


