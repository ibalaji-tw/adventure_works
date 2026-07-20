# Local Spark test runtime for the Adventure Works project.
# This is a Spark runtime, not a licensed Databricks Runtime image.
FROM spark:3.5.1-python3

USER root
WORKDIR /workspace

RUN pip install --no-cache-dir \
    delta-spark==3.2.0 \
    pytest==8.3.5

COPY adventure_final_project /workspace/adventure_final_project
COPY adventure-spark/Dataset /workspace/adventure-spark/Dataset

ENV PYTHONPATH=/workspace/adventure_final_project
ENV SPARK_LOCAL_IP=127.0.0.1

CMD ["pytest", "-q", "adventure_final_project/tests"]
