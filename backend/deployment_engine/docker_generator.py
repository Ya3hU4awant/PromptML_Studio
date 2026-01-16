def generate_dockerfile(output_dir: str):
    dockerfile_content = """FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir flask joblib scikit-learn pandas numpy pycaret

EXPOSE 5000
CMD ["python", "app.py"]
"""

    with open(f"{output_dir}/Dockerfile", "w") as f:
        f.write(dockerfile_content)
