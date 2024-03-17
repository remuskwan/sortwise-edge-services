FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" --upgrade --no-cache-dir

COPY src/ ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]
