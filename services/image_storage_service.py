"""Storage helpers for listing images."""

from pathlib import Path
from typing import Optional
from uuid import uuid4

from flask import current_app, url_for
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class ImageStorageService:
    """Save, delete, and resolve listing images through S3 or local storage."""

    def save_listing_image(self, image_file: FileStorage) -> str:
        """Store one listing image and return the saved reference."""

        filename = secure_filename(image_file.filename or "")
        unique_name = "{0}_{1}".format(uuid4().hex, filename)
        if self._use_s3_storage():
            self._upload_to_s3(image_file, unique_name)
            return unique_name

        self._save_to_local_uploads(image_file, unique_name)
        return "uploads/{0}".format(unique_name)

    def delete_listing_image(self, image_reference: Optional[str]) -> None:
        """Remove a stored image when a listing photo is replaced or deleted."""

        if not image_reference:
            return

        if image_reference.startswith(("http://", "https://")):
            return

        normalized_name = self.normalize_image_reference(image_reference)
        if self._use_s3_storage():
            self._delete_from_s3(normalized_name)
            return

        self._delete_from_local_uploads(normalized_name)

    def resolve_listing_image_url(self, image_reference: str) -> str:
        """Return a browser-safe image URL for the active image storage mode."""

        if not image_reference:
            return url_for("static", filename="images/listing-placeholder.svg")

        if image_reference.startswith(("http://", "https://")):
            return image_reference

        normalized_name = self.normalize_image_reference(image_reference)
        if self._use_s3_storage():
            return self._build_s3_public_url(normalized_name)

        if self._local_file_exists(normalized_name):
            return url_for("uploaded_file", filename=normalized_name)
        return url_for("static", filename="images/listing-placeholder.svg")

    @staticmethod
    def normalize_image_reference(value: str) -> str:
        """Normalize stored image values across legacy and S3-backed records."""

        prefix = "uploads/"
        if value.startswith(prefix):
            return value[len(prefix):]
        return value

    def _build_s3_public_url(self, object_key: str) -> str:
        """Build the public URL used by templates to display an S3 image."""

        public_base_url = current_app.config["S3_PUBLIC_BASE_URL"]
        if public_base_url:
            return "{0}/{1}".format(public_base_url, object_key)

        bucket_name = current_app.config["S3_BUCKET_NAME"]
        region = current_app.config["S3_REGION"]
        return "https://{0}.s3.{1}.amazonaws.com/{2}".format(
            bucket_name,
            region,
            object_key,
        )

    @staticmethod
    def _use_s3_storage() -> bool:
        """Return whether the runtime is configured to use S3 storage."""

        return bool(current_app.config["S3_BUCKET_NAME"])

    def _save_to_local_uploads(self, image_file: FileStorage, filename: str) -> None:
        """Save one uploaded image into the configured local uploads folder."""

        upload_path = self._local_upload_path(filename)
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        image_file.stream.seek(0)
        image_file.save(upload_path)

    def _delete_from_local_uploads(self, filename: str) -> None:
        """Delete one locally stored image if it exists."""

        for file_path in self._candidate_local_paths(filename):
            if file_path.exists():
                file_path.unlink()

    def _local_file_exists(self, filename: str) -> bool:
        """Return whether a local image exists in an active or legacy folder."""

        return any(file_path.exists() for file_path in self._candidate_local_paths(filename))

    def _candidate_local_paths(self, filename: str):
        """Return local file locations checked for one listing image."""

        return [
            self._local_upload_path(filename),
            self._legacy_upload_path(filename),
        ]

    @staticmethod
    def _local_upload_path(filename: str) -> Path:
        """Return the primary local uploads path for one filename."""

        return current_app.config["UPLOAD_FOLDER"] / filename

    @staticmethod
    def _legacy_upload_path(filename: str) -> Path:
        """Return the legacy static uploads path for one filename."""

        return current_app.config["LEGACY_UPLOAD_FOLDER"] / filename

    def _upload_to_s3(self, image_file: FileStorage, object_key: str) -> None:
        """Upload one image object into the configured S3 bucket."""

        bucket_name = current_app.config["S3_BUCKET_NAME"]
        if not bucket_name:
            raise RuntimeError("S3_BUCKET_NAME is required for listing image storage.")

        image_file.stream.seek(0)
        client = self._build_s3_client()
        client.upload_fileobj(
            image_file.stream,
            bucket_name,
            object_key,
            ExtraArgs={
                "ContentType": image_file.mimetype or "application/octet-stream",
            },
        )

    def _delete_from_s3(self, object_key: str) -> None:
        """Delete one S3 object if it exists."""

        bucket_name = current_app.config["S3_BUCKET_NAME"]
        if not bucket_name:
            return

        client = self._build_s3_client()
        client.delete_object(Bucket=bucket_name, Key=object_key)

    @staticmethod
    def _build_s3_client():
        """Create an S3 client lazily so local development stays lightweight."""

        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError(
                "boto3 is required for S3 image storage. Install dependencies from requirements.txt."
            ) from exc

        client_kwargs = {
            "service_name": "s3",
            "region_name": current_app.config["S3_REGION"] or None,
        }
        if current_app.config["AWS_ACCESS_KEY_ID"]:
            client_kwargs["aws_access_key_id"] = current_app.config["AWS_ACCESS_KEY_ID"]
        if current_app.config["AWS_SECRET_ACCESS_KEY"]:
            client_kwargs["aws_secret_access_key"] = current_app.config["AWS_SECRET_ACCESS_KEY"]
        if current_app.config["AWS_SESSION_TOKEN"]:
            client_kwargs["aws_session_token"] = current_app.config["AWS_SESSION_TOKEN"]
        return boto3.client(**client_kwargs)


image_storage_service = ImageStorageService()
