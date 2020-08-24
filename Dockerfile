FROM python:3.8

RUN pip install flask
RUN mkdir /app
COPY rrex.py /app
CMD ["python", "/app/rrex.py"]
