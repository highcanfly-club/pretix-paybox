FROM highcanfly/pretix:latest

COPY . /pretix-paybox
RUN cd /pretix-paybox && python setup.py develop

VOLUME ["/etc/pretix", "/data"]
EXPOSE 80
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["all"]
