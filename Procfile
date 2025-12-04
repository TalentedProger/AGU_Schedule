# Procfile for Railway/Render deployment
# Runs database initialization then starts combined bot + admin panel service
web: python scripts/init_cloud_db.py && python -m app.main combined
