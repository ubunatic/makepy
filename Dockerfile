FROM alpine:3.7 as builder
LABEL maintainer @ubunatic
ENV ALPINE_VERSION 3.7

ENV LANG C.UTF-8

ADD docker-requirements.txt /reqs.txt
ADD docker-packages.txt     /apks.txt

RUN apk add -U --no-cache `cat /apks.txt`

RUN pip2 freeze
RUN pip2 install -r /reqs.txt

RUN pip3 freeze
RUN pip3 install -r /reqs.txt

# add extras
RUN apk add py-pygments
RUN apk add gcc libc-dev python2-dev
RUN echo "alias ccat=pygmentize" >> /root/.bashrc

ENV WORKDIR /workspace/makepy
RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR

ADD makepy        $WORKDIR/makepy
ADD tests/py/*.py $WORKDIR/tests/py/
ADD examples $WORKDIR/examples
ADD .gitignore LICENSE.txt README.md $WORKDIR/
ADD setup.cfg setup.py tox.ini $WORKDIR/

# test installation
RUN python -m makepy dists
RUN python -m makepy backport
RUN python -m makepy --version --debug
RUN python -m makepy install  # initial install

# test Py2 makepy
RUN makepy install   -P 2    # reinstall for Python 2
RUN makepy --version --debug | grep py2
RUN makepy lint test -P 2    # test Py2 using makepy Py2
RUN makepy lint test -P 3    # test Py3 using makepy Py2

# test Py3 makepy
RUN makepy install -P 3      # reinstall for Python 3
RUN makepy --version --debug | grep py3
RUN makepy lint test -P 2    # test Py2 using makepy Py3
RUN makepy lint test -P 3    # test Py3 using makepy Py3

RUN tox -e py27
RUN tox -e py36

# run integraton testb suite
ADD tests/*.rc $WORKDIR/tests/
ADD tests/test_makepy.sh   $WORKDIR/tests/
ADD tests/test_versions.sh $WORKDIR/tests/
RUN tests/test_versions.sh
 
ADD tests/test_project.sh $WORKDIR/tests/
RUN tests/test_project.sh demo

FROM alpine:3.7

COPY --from=builder /workspace/makepy/dist  /dist
COPY --from=builder /apks.txt               /apks.txt
COPY --from=builder /reqs.txt               /reqs.txt

RUN apk update && apk add -U --no-cache `cat /apks.txt` \
 && pip3 install --no-cache-dir -r /reqs.txt /dist/*py3-none-any.whl \
 && pip2 install --no-cache-dir -r /reqs.txt /dist/*py2-none-any.whl

ENTRYPOINT ["bash", "-ic"]
