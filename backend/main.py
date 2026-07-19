from fastapi import FastAPI

# Create the FastAPI application
app = FastAPI(
    title="AI Code Review Bot",
    description="An AI-powered GitHub Pull Request Review Bot",
    version="1.0.0"
)


@app.get("/")
def root():
    """
    Health check endpoint.
    Used to verify that the server is running.
    """
    return {
        "status": "success",
        "message": "AI Code Review Bot is running!",
        "version": "1.0.0"
    }