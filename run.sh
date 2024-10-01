#!/bin/bash
AWS_PROFILE=acdong
STACK_NAME=FGI-daily-trader

# 빌드
sam build --profile $AWS_PROFILE

# 로컬 실행
# sam local invoke LambdaFunction --profile $AWS_PROFILE

# 배포
sam deploy

sam logs -n LambdaFunction --stack-name $STACK_NAME --tail --profile $AWS_PROFILE