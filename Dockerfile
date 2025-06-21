FROM python:3.12.11-slim-bookworm
WORKDIR /weapi
COPY wea.py weapi.py requirements.txt ./

#### for user; comment this section for root
RUN groupadd eng && \
    useradd -m -g eng eng && \
    chown eng:eng /weapi
USER eng
ENV PATH=/home/eng/.local/bin:$PATH

ENV TZ=Asia/Taipei \
    LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1
RUN pip3 install --no-cache-dir -r requirements.txt gunicorn
# CMD ["bash", "-c", "gunicorn a:app -b :${PORT:-8080} --workers ${WORKERS:-1} --threads ${THREADS:-1}"]
CMD gunicorn weapi:app -b :${PORT:-8080} --workers ${WORKERS:-1} --threads ${THREADS:-1}
