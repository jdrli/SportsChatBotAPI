from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ScrapingJob, ScrapedData
from .etl_pipeline import SportsETLPipeline
from .ncaa_scraper import NCAAScraper
from .data_loader import load_processed_data_to_db
import threading
import os
import urllib.parse
from django.conf import settings


def get_database_url():
    """
    Helper function to construct database URL from Django settings
    """
    db_config = settings.DATABASES['default']
    
    if db_config['ENGINE'] == 'django.db.backends.postgresql':
        return f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
    elif db_config['ENGINE'] == 'django.db.backends.mysql':
        return f"mysql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
    elif db_config['ENGINE'] == 'django.db.backends.sqlite3':
        # For SQLAlchemy to work with SQLite, we need the full path
        db_path = db_config['NAME']
        if not os.path.isabs(db_path):
            from django.conf import settings as django_settings
            db_path = os.path.join(django_settings.BASE_DIR, db_path)
        return f"sqlite:///{db_path}"
    else:
        # Default to SQLite
        return "sqlite:///db.sqlite3"

@api_view(['GET'])
def run_scraper(request):
    """
    Run the complete ETL pipeline for NCAA data
    """
    try:
        # Create a scraping job record
        job = ScrapingJob.objects.create(
            name="NCAA ETL Pipeline",
            description="Automated scraping and processing of NCAA data"
        )
        
        # Update job status to running
        job.status = 'running'
        job.save()
        
        # Start the ETL process in a separate thread
        thread = threading.Thread(target=execute_etl_process, args=(job.id,))
        thread.start()
        
        return Response({
            "message": "ETL pipeline started successfully",
            "job_id": job.id,
            "status": "running"
        })
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def execute_etl_process(job_id):
    """
    Execute the ETL process in a separate thread
    """
    try:
        job = ScrapingJob.objects.get(id=job_id)
        
        # Initialize the ETL pipeline using Django's database connection
        db_url = get_database_url()
        
        pipeline = SportsETLPipeline(db_url)
        
        # Initialize the NCAA scraper
        scraper = NCAAScraper()
        
        # Scrape different types of data
        total_records = 0
        
        # Scrape basketball stats
        basketball_stats = scraper.scrape_multiple_categories('basketball', season='2023')
        for category, df in basketball_stats.items():
            if not df.empty:
                # Load basketball data
                load_processed_data_to_db(df, 'basketball_stats', db_url, season='2023')
                total_records += len(df)
        
        # Scrape football stats
        football_stats = scraper.scrape_multiple_categories('football', season='2023')
        for category, df in football_stats.items():
            if not df.empty:
                # Load football data
                load_processed_data_to_db(df, 'football_stats', db_url, season='2023')
                total_records += len(df)
        
        # Update job status to completed
        job.status = 'completed'
        job.records_processed = total_records
        job.save()
        
    except Exception as e:
        # Update job status to failed
        job = ScrapingJob.objects.get(id=job_id)
        job.status = 'failed'
        job.error_message = str(e)
        job.save()

@api_view(['GET'])
def get_job_status(request, job_id):
    """
    Get the status of a specific scraping job
    """
    try:
        job = ScrapingJob.objects.get(id=job_id)
        return Response({
            "job_id": job.id,
            "name": job.name,
            "status": job.status,
            "records_processed": job.records_processed,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message
        })
    except ScrapingJob.DoesNotExist:
        return Response({
            "error": "Job not found"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def run_ncaa_basketball_scraper(request):
    """
    Run the NCAA basketball scraper specifically
    """
    try:
        # Create a scraping job record
        job = ScrapingJob.objects.create(
            name="NCAA Basketball Scraper",
            description="Scraping NCAA basketball statistics"
        )
        
        # Update job status to running
        job.status = 'running'
        job.save()
        
        # Start the basketball scraping in a separate thread
        thread = threading.Thread(target=execute_basketball_scraping, args=(job.id,))
        thread.start()
        
        return Response({
            "message": "NCAA basketball scraping started successfully",
            "job_id": job.id,
            "status": "running"
        })
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def execute_basketball_scraping(job_id):
    """
    Execute the basketball scraping process in a separate thread
    """
    try:
        job = ScrapingJob.objects.get(id=job_id)
        
        # Initialize the NCAA scraper
        scraper = NCAAScraper()
        
        # Scrape basketball stats
        basketball_stats = scraper.scrape_multiple_categories('basketball', season='2023')
        
        total_records = 0
        for category, df in basketball_stats.items():
            if not df.empty:
                # Load basketball data
                db_url = get_database_url()
                
                load_processed_data_to_db(df, 'basketball_stats', db_url, season='2023')
                total_records += len(df)
        
        # Update job status to completed
        job.status = 'completed'
        job.records_processed = total_records
        job.save()
        
    except Exception as e:
        # Update job status to failed
        job = ScrapingJob.objects.get(id=job_id)
        job.status = 'failed'
        job.error_message = str(e)
        job.save()

@api_view(['GET'])
def run_ncaa_football_scraper(request):
    """
    Run the NCAA football scraper specifically
    """
    try:
        # Create a scraping job record
        job = ScrapingJob.objects.create(
            name="NCAA Football Scraper",
            description="Scraping NCAA football statistics"
        )
        
        # Update job status to running
        job.status = 'running'
        job.save()
        
        # Start the football scraping in a separate thread
        thread = threading.Thread(target=execute_football_scraping, args=(job.id,))
        thread.start()
        
        return Response({
            "message": "NCAA football scraping started successfully",
            "job_id": job.id,
            "status": "running"
        })
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def execute_football_scraping(job_id):
    """
    Execute the football scraping process in a separate thread
    """
    try:
        job = ScrapingJob.objects.get(id=job_id)
        
        # Initialize the NCAA scraper
        scraper = NCAAScraper()
        
        # Scrape football stats
        football_stats = scraper.scrape_multiple_categories('football', season='2023')
        
        total_records = 0
        for category, df in football_stats.items():
            if not df.empty:
                # Load football data
                db_url = get_database_url()
                
                load_processed_data_to_db(df, 'football_stats', db_url, season='2023')
                total_records += len(df)
        
        # Update job status to completed
        job.status = 'completed'
        job.records_processed = total_records
        job.save()
        
    except Exception as e:
        # Update job status to failed
        job = ScrapingJob.objects.get(id=job_id)
        job.status = 'failed'
        job.error_message = str(e)
        job.save()