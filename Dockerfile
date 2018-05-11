FROM alpine:3.7
LABEL maintainer @ubunatic
ENV ALPINE_VERSION 3.7

ENV LANG C.UTF-8

ENV REQUIREMENTS "tox<=2.5.0" \
                 "flake8<=3.5.0" \
                 "pytest<=3.5.0" \
                 "wheel<=0.31.0"

ENV WORKDIR /workspace/makepy
ENV PATH    $PATH:$HOME/root/.local/bin

RUN apk add --no-cache -U \
       bash bash-completion git make ca-certificates \
       python2    python3 \
       py2-future py3-future \
       py2-pip    py3-pip \
       && pip2 install $REQUIREMENTS \
       && pip3 install $REQUIREMENTS

# add extras
RUN apk add py-pygments
RUN echo "alias ccat=pygmentize" >> /root/.bashrc

RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR

ADD makepy   $WORKDIR/makepy
ADD tests    $WORKDIR/tests
ADD examples $WORKDIR/examples
ADD .gitignore LICENSE.txt README.md $WORKDIR/
ADD project.cfg setup.cfg setup.py tox.ini $WORKDIR/

RUN python2 -m makepy install
RUN python3 -m makepy install

# makepy is now installed, we can remove the source from the image
RUN rm -rf $WORKDIR
 
WORKDIR /

ENTRYPOINT ["bash", "-ic"]
