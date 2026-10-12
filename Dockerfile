FROM python:3.11-slim
WORKDIR /workspace
COPY . .
RUN pip install --no-cache-dir -e .
CMD ["python","-m","achitic.cli","--help"]
