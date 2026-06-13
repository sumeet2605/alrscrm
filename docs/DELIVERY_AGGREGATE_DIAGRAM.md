# Delivery Aggregate Diagram

```mermaid
classDiagram
    direction LR

    class Family {
      UUID id
      string family_code
      string primary_contact_name
    }

    class Booking {
      UUID id
      UUID family_id
      string booking_number
    }

    class Gallery {
      UUID id
      UUID booking_id
      string gallery_status
    }

    class EditingJob {
      UUID id
      UUID gallery_id
      EditingStatus editing_status
      int completed_photo_count
    }

    class DeliveryJob {
      UUID id
      UUID family_id
      UUID booking_id
      UUID gallery_id
      UUID editing_job_id
      string delivery_number
      DeliveryStatus delivery_status
      int edited_photo_count
      date delivery_date
      date expiry_date
      int download_count
      int max_downloads
      ZipGenerationStatus zip_generation_status
    }

    class DeliveryDownload {
      UUID id
      UUID delivery_job_id
      datetime downloaded_at
      string ip_address
      string user_agent
    }

    class DeliveryAudit {
      UUID id
      UUID delivery_job_id
      string event_type
      datetime event_timestamp
      string event_details
    }

    Family "1" <-- "*" Booking : references
    Booking "1" <-- "*" Gallery : source
    Gallery "1" <-- "0..1" EditingJob : creates production work
    EditingJob "1" --> "0..1" DeliveryJob : creates after ready
    DeliveryJob "1" *-- "*" DeliveryDownload : owns
    DeliveryJob "1" *-- "*" DeliveryAudit : owns
```

## Boundary Notes

- `DeliveryJob` is the Sprint 7 aggregate root.
- `DeliveryDownload` and `DeliveryAudit` are DeliveryJob-owned child entities.
- `GalleryPhoto` remains owned by Gallery.
- `EditingReview` remains owned by EditingJob.
- Family customer profile fields are not duplicated in DeliveryJob.

## Persistence Notes

Implemented tables:

- `delivery_jobs`
- `delivery_downloads`
- `delivery_audits`

Implemented uniqueness:

```text
unique(delivery_number)
unique(gallery_id)
unique(editing_job_id)
```

