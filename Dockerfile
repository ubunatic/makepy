FROM alpine:3.7 as builder
LABEL maintainer @ubunatic
ENV ALPINE_VERSION 3.7

ENV LANG C.UTF-8

ADD docker-requirements.txt /reqs.txt
ADD docker-packages.txt     /apks.txt

RUN apk add -U `cat /apks.txt`

RUN pip2 freeze
RUN pip2 install -r /reqs.txt

RUN pip3 freeze
RUN pip3 install -r /reqs.txt

# add extras
RUN apk add py-pygments
RUN echo "alias ccat=pygmentize" >> /root/.bashrc

ENV WORKDIR /workspace/makepy
RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR

ADD makepy   $WORKDIR/makepy
ADD tests    $WORKDIR/tests
ADD examples $WORKDIR/examples
ADD .gitignore LICENSE.txt README.md $WORKDIR/
ADD setup.cfg setup.py tox.ini $WORKDIR/

RUN python3 -m makepy install  # install from local module
RUN makepy install -P 2        # install backport via makepy from local module
RUN tests/test_makepy.sh
# RUN tests/test_namespace.sh
# RUN tests/test_versions.sh
# RUN tests/test_project.sh demo


# FROM alpine:3.7
# 
# COPY --from=builder /workspace/makepy/dist  /dist
# COPY --from=builder /apks.txt               /apks.txt
# COPY --from=builder /reqs.txt               /reqs.txt
# 
# RUN apk update && apk add -U --no-cache `cat /apks.txt` \
# 	&& pip3 install --no-cache-dir -r /reqs.txt /dist/*py3-none-any.whl \
# 	&& pip2 install --no-cache-dir -r /reqs.txt /dist/*py2-none-any.whl

ENTRYPOINT ["bash", "-ic"]
