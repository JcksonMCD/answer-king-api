# answer-king-api
## Future Improvements ~ *Not in priority order*:
- Use connection pooling/reuse, since there's already a shared layer for DB connections.
- Add a decorator (as a Lambda layer) for centralized error handling.
- Remove the need to import psycopg2.binary in every Lambda via a requirments.txt; find a cleaner solution.
- Drop unnecessary conn.commit() calls — already using context managers.
- Potentially look at how to utilise caching or pagination with python lambdas for some of the larger read heavy endpoints.
- Store DB credentials in AWS Secrets Manager instead of environment variables.
- Set up a GitHub Actions pipeline for automatic deployment.
- Improve unit test coverage after Friday's refactor.
- Remove IP access restriction to my local machine for security and portability.
- General refactor focusing on code readability and in particular utilising consistent, descriptive naming conventions.
- Add authentication for API calls.
