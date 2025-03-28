ARG PYTHON_VERSION=3.9.4-slim
FROM python:${PYTHON_VERSION}

LABEL maintainer="TQHOA <tqhoa8th@gmail.com>"

# set work directory
WORKDIR /zkit

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ="Asia/Ho_Chi_Minh"

COPY ./requirements.txt /zkit/requirements.txt

# install system dependencies
#RUN apt-get update
#RUN pip install --upgrade pip


# install dependencies
RUN pip install --no-cache-dir -r /zkit/requirements.txt

COPY ./src /zkit

ENTRYPOINT ["sh", "/zkit/prestart.sh"]

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
