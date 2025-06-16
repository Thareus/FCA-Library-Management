import pandas as pd
import logging
from time import time
from celery import shared_task
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from .serializers import BookImportSerializer

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, time_limit=3600)  # 1 hour time limit
def process_csv_task(self, file_path, user_email=None):
    """
    Process a CSV file containing book data asynchronously.
    
    Args:
        file_path (str): Path to the CSV file to process
        user_email (str, optional): Email address to notify when processing is complete
        
    Returns:
        dict: Processing results with success/error counts
    """
    logger.info("Starting CSV processing task")
    start_time = time()
    task_id = self.request.id
    logger.info(f"Starting CSV processing task {task_id} for file: {file_path}")
    
    results = {
        "success": 0,
        "errors": [],
        "total_processed": 0,
        "task_id": task_id,
        "file": file_path
    }
    
    try:
        with default_storage.open(file_path, mode='r') as f:
            try:
                df = pd.read_csv(f)

                # Quickly check the CSV header
                required_fields = ['id', 'authors', 'publication year', 'title', 'language']
                df.columns = [str(i).lower() for i in df.columns]
                if not all(field in df.columns for field in required_fields):
                    raise ValueError(f'CSV must contain the following fields: {", ".join(required_fields)}')

                results["total_processed"] = len(df)
                
                # Standardize column names
                df.columns = df.columns.str.strip().str.lower()
                
                # Rename columns to match model fields
                df.rename(columns={
                    "id": "library_id",
                    "publication year": "publication_year",
                }, inplace=True, errors='ignore')  # Ignore if columns don't exist
                
                # Preprocess: strip whitespace, drop NA, standardize
                initial_count = len(df)
                df = df.dropna(subset=["isbn", "title"])
                if len(df) < initial_count:
                    logger.warning(f"Dropped {initial_count - len(df)} rows with missing ISBN or title")
                    results["errors"].append({
                        "row": "",
                        "errors": f"Dropped {initial_count - len(df)} rows with missing ISBN or title"
                    })
                
                # Clean and standardize data
                df["isbn"] = df["isbn"].astype(str).str.strip()
                df["language"] = df["language"].str.lower().str.strip()
                df["authors"] = df["authors"].fillna("Unknown")
                
                # Process in chunks for better memory management
                chunk_size = 100
                for i in range(0, len(df), chunk_size):
                    chunk = df[i:i + chunk_size]
                    with transaction.atomic():
                        for index, row in chunk.iterrows():
                            try:
                                serializer = BookImportSerializer(data=row.to_dict())
                                if serializer.is_valid():
                                    serializer.save()
                                    results["success"] += 1
                                else:
                                    results["errors"].append({
                                        "row": index + 2,
                                        "errors": serializer.errors
                                    })
                            except Exception as e:
                                logger.error(f"Error processing row {index}: {str(e)}")
                                results["errors"].append({
                                    "row": index + 2,
                                    "errors": str(e)
                                })
                
                # Calculate processing time
                processing_time = time() - start_time
                results["processing_time_seconds"] = round(processing_time, 2)
                
                # Log completion
                logger.info(
                    f"Completed processing {results['success']} books "
                    f"with {len(results['errors'])} errors in {processing_time:.2f} seconds"
                )
                
                # Send email notification if email provided
                if user_email:
                    try:
                        send_processing_completion_email.delay(
                            user_email,
                            file_path,
                            results["success"],
                            len(results["errors"]),
                            task_id
                        )
                    except Exception as email_error:
                        logger.error(f"Failed to send email notification: {str(email_error)}")
                
                return results
                
            except pd.errors.EmptyDataError:
                error_msg = f"The file {file_path} is empty or not a valid CSV"
                logger.error(error_msg)
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"Error reading CSV file: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg) from e
                
    except Exception as e:
        logger.error(f"Failed to process file {file_path}: {str(e)}")
        # Retry with exponential backoff if we have retries left
        if self.request.retries < self.max_retries:
            retry_delay = 60 * (2 ** self.request.retries)  # 1, 2, 4 minutes
            logger.info(f"Retrying task in {retry_delay} seconds... (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=retry_delay)
        else:
            # If we've exhausted retries, send a failure notification
            if user_email:
                try:
                    send_mail(
                        'CSV Processing Failed',
                        f'Failed to process file {file_path} after {self.max_retries} attempts.\n\nError: {str(e)}',
                        settings.DEFAULT_FROM_EMAIL,
                        [user_email],
                        fail_silently=True,
                    )
                except Exception as email_error:
                    logger.error(f"Failed to send failure email: {str(email_error)}")
            raise

@shared_task
def send_processing_completion_email(user_email, file_path, success_count, error_count, task_id):
    """Send an email notification when CSV processing is complete."""
    subject = 'CSV Processing Complete'
    message = (
        f'Your file {file_path} has been processed.\n\n'
        f'Successfully processed: {success_count} books\n'
        f'Errors: {error_count}\n\n'
        f'Task ID: {task_id}'
    )
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Sent completion email to {user_email}")
    except Exception as e:
        logger.error(f"Failed to send completion email to {user_email}: {str(e)}")
        raise