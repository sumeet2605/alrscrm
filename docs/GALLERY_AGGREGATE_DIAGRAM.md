# Gallery Aggregate Diagram

```mermaid
classDiagram
    direction LR

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
      decimal final_amount
    }

    class Gallery {
      UUID id
      UUID organization_id
      UUID branch_id
      UUID booking_id
      UUID booking_item_id
      string gallery_name
      GalleryStatus gallery_status
      UUID created_by_user_id
      string password_hash
      datetime expires_at
    }

    class GalleryPhoto {
      UUID id
      UUID gallery_id
      string file_name
      string storage_path
      string thumbnail_path
      int file_size
      int image_width
      int image_height
      int sort_order
      bool is_active
      datetime uploaded_at
    }

    class FavoriteSelection {
      UUID id
      UUID gallery_id
      UUID gallery_photo_id
      string selected_by_name
      string selected_by_email
      datetime selected_at
    }

    Booking "1" *-- "*" BookingItem : owns
    BookingItem "1" --> "0..1" Gallery : owns gallery
    Gallery "1" *-- "*" GalleryPhoto : owns
    Gallery "1" *-- "*" FavoriteSelection : owns
    GalleryPhoto "1" --> "*" FavoriteSelection : selected photo
```

## Boundary Notes

- `Gallery` is the aggregate root for Sprint 5.
- `GalleryPhoto` and `FavoriteSelection` do not have independent lifecycles.
- `BookingItem` remains in the Booking domain and is referenced by Gallery.
- Family customer profile data is not stored in Gallery tables.
