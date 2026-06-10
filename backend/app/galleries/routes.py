from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.galleries.enums import GalleryStatus
from app.galleries.schemas import (
    FavoriteSelectionCreate,
    FavoriteSelectionRead,
    GalleryCreate,
    GalleryDetailRead,
    GalleryMetricsRead,
    GalleryPhotoCreate,
    GalleryPhotoRead,
    GalleryRead,
    GalleryUpdate,
)
from app.galleries.services import gallery_service
from app.galleries.storage import StorageProvider, get_storage_provider

router = APIRouter(prefix="/galleries", tags=["Galleries"])


def _gallery(item) -> dict:
    return GalleryRead.model_validate(gallery_service.gallery_to_read(item)).model_dump(mode="json")


def _gallery_detail(item) -> dict:
    return GalleryDetailRead.model_validate(gallery_service.gallery_to_detail(item)).model_dump(
        mode="json"
    )


def _photo(item) -> dict:
    return GalleryPhotoRead.model_validate(item).model_dump(mode="json")


def _favorite(item) -> dict:
    return FavoriteSelectionRead.model_validate(item).model_dump(mode="json")


@router.get("/metrics", response_model=APIResponse)
def get_gallery_metrics(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:read")),
):
    metrics = GalleryMetricsRead(**gallery_service.get_metrics(db, context))
    return api_response("Gallery metrics retrieved", metrics.model_dump(mode="json"))


@router.get("", response_model=APIResponse)
def list_galleries(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    branch_id: UUID | None = Query(default=None),
    gallery_status: GalleryStatus | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:read")),
):
    result = gallery_service.list_galleries(
        db,
        context,
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        gallery_status=gallery_status.value if gallery_status else None,
        search=search,
    )
    return api_response(
        "Galleries retrieved",
        [_gallery(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_gallery(
    payload: GalleryCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:write")),
):
    item = gallery_service.create_gallery(db, payload, context)
    return api_response("Gallery created", _gallery_detail(item))


@router.get("/{gallery_id}", response_model=APIResponse)
def get_gallery(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:read")),
):
    item = gallery_service.get_gallery(db, gallery_id, context)
    return api_response("Gallery retrieved", _gallery_detail(item))


@router.put("/{gallery_id}", response_model=APIResponse)
def update_gallery(
    gallery_id: UUID,
    payload: GalleryUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:write")),
):
    item = gallery_service.update_gallery(db, gallery_id, payload, context)
    return api_response("Gallery updated", _gallery_detail(item))


@router.get("/{gallery_id}/photos", response_model=APIResponse)
def list_gallery_photos(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:photos:read")),
):
    return api_response(
        "Gallery photos retrieved",
        [_photo(item) for item in gallery_service.list_photos(db, gallery_id, context)],
    )


@router.post(
    "/{gallery_id}/photos", status_code=status.HTTP_201_CREATED, response_model=APIResponse
)
def add_gallery_photo(
    gallery_id: UUID,
    payload: GalleryPhotoCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:photos:write")),
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    item = gallery_service.add_photo(db, gallery_id, payload, context, storage_provider)
    return api_response("Gallery photo uploaded", _photo(item))


@router.delete("/{gallery_id}/photos/{photo_id}", response_model=APIResponse)
def delete_gallery_photo(
    gallery_id: UUID,
    photo_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:photos:write")),
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    gallery_service.delete_photo(db, gallery_id, photo_id, context, storage_provider)
    return api_response("Gallery photo deleted", {})


@router.get("/{gallery_id}/favorites", response_model=APIResponse)
def list_gallery_favorites(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:favorites:read")),
):
    return api_response(
        "Gallery favorites retrieved",
        [_favorite(item) for item in gallery_service.list_favorites(db, gallery_id, context)],
    )


@router.post(
    "/{gallery_id}/favorites", status_code=status.HTTP_201_CREATED, response_model=APIResponse
)
def add_gallery_favorite(
    gallery_id: UUID,
    payload: FavoriteSelectionCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:favorites:write")),
):
    item = gallery_service.add_favorite(db, gallery_id, payload, context)
    return api_response("Gallery favorite selected", _favorite(item))


@router.delete("/{gallery_id}/favorites/{favorite_id}", response_model=APIResponse)
def delete_gallery_favorite(
    gallery_id: UUID,
    favorite_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:favorites:write")),
):
    gallery_service.delete_favorite(db, gallery_id, favorite_id, context)
    return api_response("Gallery favorite deleted", {})


@router.get("/{gallery_id}/public", response_model=APIResponse)
def get_public_gallery(gallery_id: UUID, db: Session = Depends(get_db)):
    item = gallery_service.get_public_gallery(db, gallery_id)
    return api_response("Public gallery retrieved", _gallery_detail(item))


@router.post(
    "/{gallery_id}/public/favorites",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse,
)
def add_public_gallery_favorite(
    gallery_id: UUID,
    payload: FavoriteSelectionCreate,
    db: Session = Depends(get_db),
):
    item = gallery_service.add_favorite(db, gallery_id, payload, None)
    return api_response("Gallery favorite selected", _favorite(item))


@router.delete("/{gallery_id}/public/favorites/{favorite_id}", response_model=APIResponse)
def delete_public_gallery_favorite(
    gallery_id: UUID,
    favorite_id: UUID,
    db: Session = Depends(get_db),
):
    gallery_service.delete_favorite(db, gallery_id, favorite_id, None)
    return api_response("Gallery favorite deleted", {})
