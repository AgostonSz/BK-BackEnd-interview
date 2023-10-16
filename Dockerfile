FROM python:3.8

COPY authentication.py /app/
COPY main.py /app/
COPY tests.py /app/

# COPY token.json /app/

COPY img1.jpg /app/
COPY img2.jpg /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

EXPOSE 8000

CMD ["python", "main.py"]