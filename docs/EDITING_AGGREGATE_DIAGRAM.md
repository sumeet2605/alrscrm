# Editing Aggregate Diagram

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

    class BookingItem {
      UUID id
      UUID booking_id
      UUID package_id
      string service_type
    }

    class Gallery {
      UUID id
      UUID booking_id
      UUID booking_item_id
      GalleryStatus gallery_status
      datetime selection_submitted_at
      bool selection_locked
    }

    class FavoriteSelection {
      UUID id
      UUID gallery_id
      UUID gallery_photo_id
      datetime selected_at
    }

    class EditingJob {
      UUID id
      UUID organization_id
      UUID branch_id
      UUID booking_id
      UUID booking_item_id
      UUID gallery_id
      UUID assigned_editor_id
      EditingPriority priority
      EditingStatus editing_status
      int selected_photo_count
      int completed_photo_count
      date due_date
      datetime started_at
      datetime completed_at
      string notes
    }

    class EditingReview {
      UUID id
      UUID editing_job_id
      UUID reviewed_by_user_id
      EditingReviewStatus review_status
      string review_notes
      datetime reviewed_at
    }

    Family "1" <-- "*" Booking : references
    Booking "1" *-- "*" BookingItem : owns
    BookingItem "1" --> "0..1" Gallery : source selection
    Gallery "1" *-- "*" FavoriteSelection : owns
    Gallery "1" --> "0..1" EditingJob : creates production work
    EditingJob "1" *-- "*" EditingReview : owns
```

## Boundary Notes

- `EditingJob` is the Sprint 6 aggregate root.
- `EditingReview` is owned by EditingJob.
- `Gallery`, `GalleryPhoto`, and `FavoriteSelection` remain in the Gallery
  aggregate.
- `Booking` and `BookingItem` remain in the Booking aggregate.
- `Family` remains the owner of customer profile data.
- `ReadyForDelivery` is represented by `EditingJob.editing_status`, not a
  separate aggregate in Sprint 6.
- One row per selected photo is intentionally not modeled.

## Persistence Notes

Implemented tables:

- `editing_jobs`
- `editing_reviews`

Implemented uniqueness:

```text
unique(gallery_id)
```

Implemented count model:

```text
selected_photo_count
completed_photo_count
```

Recommended indexes:

- `editing_jobs(organization_id, branch_id, editing_status)`
- `editing_jobs(branch_id)`
- `editing_jobs(assigned_editor_id)`
- `editing_jobs(due_date)`
- `editing_reviews(editing_job_id)`
