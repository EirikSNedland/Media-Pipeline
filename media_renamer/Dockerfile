FROM python:3.11-slim

WORKDIR /app

# Copy python script and structural directories 
COPY filename_reader.py .
COPY helpers/ ./helpers/

# We don't copy the whole 'items' folder permanently into the image 
# because docker-compose will mount your live host files over this directory.
RUN mkdir /app/items

CMD ["python", "filename_reader.py"]