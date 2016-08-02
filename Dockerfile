FROM floydhub/dl-docker:gpu
RUN pip install h5py joblib
RUN git clone https://github.com/DmitryUlyanov/online-neural-doodle
RUN luarocks install hdf5
WORKDIR online-neural-doodle
RUN mkdir /root/data
RUN mkdir /root/doodle
VOLUME ["/root/data"]
VOLUME ["/root/doodle"]
ENTRYPOINT ["python"]
