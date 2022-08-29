FROM python:3.10-bullseye

COPY requirements.txt .
# RUN pip download --cache-dir ./tmp/pipcache -r requirements.txt
RUN pip install --cache-dir ./tmp/pipcache -r requirements.txt

COPY . .
CMD ["python", "-m", "bot"]
