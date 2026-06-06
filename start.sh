#!/bin/bash

# bind to Render's dynamic port, fallback to 8501 for local dev
APP_PORT=${PORT:-8501}

echo "starting app on port $APP_PORT"

# start the main streamlit process
streamlit run app.py --server.port=$APP_PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false

# if streamlit exits or crashes (OOM), serve the static fallback page
echo "app crashed. serving fallback"
python -m http.server $APP_PORT
