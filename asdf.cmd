SET APP_SETTINGS=project.config.DevelopmentConfig
SET DATABASE_URL=postgres://postgres:postgres@localhost:5432/users_dev
SET DATABASE_TEST_URL=postgres://postgres:postgres@localhost:5432/users_test
SET SECRET_KEY=secret

REM set REACT_APP_USERS_SERVICE to docker ip
REM set TEST_URL to docker ip for testcafe

test