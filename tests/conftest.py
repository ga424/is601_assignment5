import app.exceptions as exceptions


if not hasattr(exceptions, "ConfiguationError"):
    exceptions.ConfiguationError = exceptions.ConfigurationError
