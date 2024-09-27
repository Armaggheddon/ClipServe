FROM python:3

WORKDIR /api

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# run the gunicon server
CMD ["fastapi", "run", "src/main.py"]