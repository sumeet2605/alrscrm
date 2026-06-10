from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Header, Query, UploadFile, status
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
from app.galleries.schemas.gallery import (
    GalleryAuthenticateRequest,
    GalleryAuthenticateResponse,
)
from app.galleries.services import gallery_service
from app.galleries.schemas.gallery import (
    GalleryUpgradeRequestCreate,
    GalleryUpgradeRequestRead,
)
from app.galleries.storage import StorageProvider, get_storage_provider

router = APIRouter(prefix="/galleries", tags=["Galleries"])


def _gallery(item) -> dict:
    return GalleryRead.model_validate(gallery_service.gallery_to_read(item)).model_dump(mode="json")


def _gallery_detail(item, storage_provider: StorageProvider) -> dict:
    return GalleryDetailRead.model_validate(gallery_service.gallery_to_detail(item)).model_dump(
        mode="json"
    ) | {
        "photos": [_photo(photo, storage_provider) for photo in item.photos if photo.is_active],
        "favorites": [_favorite(favorite, storage_provider) for favorite in item.favorites],
    }


def _photo(item, storage_provider: StorageProvider) -> dict:
    data = GalleryPhotoRead.model_validate(item).model_dump(mode="json")
    data["storage_path"] = storage_provider.generate_signed_url(item.storage_path)
    data["thumbnail_path"] = storage_provider.generate_thumbnail_url(item.thumbnail_path)
    return data


def _favorite(item, storage_provider: StorageProvider) -> dict:
    data = FavoriteSelectionRead.model_validate(item).model_dump(mode="json")
    if item.gallery_photo is not None:
        data["gallery_photo"] = _photo(item.gallery_photo, storage_provider)
    return data


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
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    item = gallery_service.create_gallery(db, payload, context)
    return api_response("Gallery created", _gallery_detail(item, storage_provider))


@router.get("/{gallery_id}", response_model=APIResponse)
def get_gallery(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:read")),
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    item = gallery_service.get_gallery(db, gallery_id, context)
    return api_response("Gallery retrieved", _gallery_detail(item, storage_provider))


@router.put("/{gallery_id}", response_model=APIResponse)
def update_gallery(
    gallery_id: UUID,
    payload: GalleryUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:write")),
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    item = gallery_service.update_gallery(db, gallery_id, payload, context)
    return api_response("Gallery updated", _gallery_detail(item, storage_provider))


@router.get("/{gallery_id}/photos", response_model=APIResponse)
def list_gallery_photos(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:photos:read")),
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    return api_response(
        "Gallery photos retrieved",
        [
            _photo(item, storage_provider)
            for item in gallery_service.list_photos(db, gallery_id, context)
        ],
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
    return api_response("Gallery photo uploaded", _photo(item, storage_provider))


@router.post(
    "/{gallery_id}/photos/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse,
)
async def upload_gallery_photo(
    gallery_id: UUID,
    file: UploadFile = File(...),
    image_width: int = Form(default=1, gt=0),
    image_height: int = Form(default=1, gt=0),
    sort_order: int = Form(default=0),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:photos:write")),
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    content = await file.read()
    item = gallery_service.upload_photo_file(
        db,
        gallery_id,
        file_name=file.filename or "gallery-photo",
        content=content,
        content_type=file.content_type,
        image_width=image_width,
        image_height=image_height,
        sort_order=sort_order,
        context=context,
        storage_provider=storage_provider,
    )
    return api_response("Gallery photo uploaded", _photo(item, storage_provider))


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
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    return api_response(
        "Gallery favorites retrieved",
        [
            _favorite(item, storage_provider)
            for item in gallery_service.list_favorites(db, gallery_id, context)
        ],
    )


@router.post(
    "/{gallery_id}/favorites", status_code=status.HTTP_201_CREATED, response_model=APIResponse
)
def add_gallery_favorite(
    gallery_id: UUID,
    payload: FavoriteSelectionCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:favorites:write")),
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    item = gallery_service.add_favorite(db, gallery_id, payload, context)
    return api_response("Gallery favorite selected", _favorite(item, storage_provider))


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
def get_public_gallery(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    storage_provider: StorageProvider = Depends(get_storage_provider),
    authorization: str | None = Header(default=None),
):
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    item = gallery_service.get_public_gallery(db, gallery_id, token)
    return api_response("Public gallery retrieved", _gallery_detail(item, storage_provider))


@router.post(
    "/{gallery_id}/public/favorites",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse,
)
def add_public_gallery_favorite(
    gallery_id: UUID,
    payload: FavoriteSelectionCreate,
    db: Session = Depends(get_db),
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    item = gallery_service.add_favorite(db, gallery_id, payload, None)
    return api_response("Gallery favorite selected", _favorite(item, storage_provider))


@router.delete("/{gallery_id}/public/favorites/{favorite_id}", response_model=APIResponse)
def delete_public_gallery_favorite(
    gallery_id: UUID,
    favorite_id: UUID,
    db: Session = Depends(get_db),
):
    gallery_service.delete_favorite(db, gallery_id, favorite_id, None)
    return api_response("Gallery favorite deleted", {})



@router.post("/public/{gallery_id}/authenticate", response_model=APIResponse)
def authenticate_public_gallery(
    gallery_id: UUID,
    payload: GalleryAuthenticateRequest,
    db: Session = Depends(get_db),
):
    token = gallery_service.authenticate_public_gallery(db, gallery_id, payload.password)
    return api_response("Gallery authenticated", GalleryAuthenticateResponse(access_token=token).model_dump())


@router.post("/{gallery_id}/public/submit-selection", response_model=APIResponse)
def submit_public_selection(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    storage_provider: StorageProvider = Depends(get_storage_provider),
    authorization: str | None = Header(default=None),
):
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    item = gallery_service.submit_public_selection(db, gallery_id, token)
    return api_response(
        "Selection submitted",
        GalleryDetailRead.model_validate(gallery_service.gallery_to_detail(item)).model_dump(mode="json"),
    )


@router.post("/{gallery_id}/submit-selection", response_model=APIResponse)
def submit_selection(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:write")),
):
    item = gallery_service.submit_selection(db, gallery_id, context)
    return api_response("Selection submitted", GalleryDetailRead.model_validate(gallery_service.gallery_to_detail(item)).model_dump(mode="json"))


@router.post("/{gallery_id}/upgrade-request", response_model=APIResponse)
def create_upgrade_request(
    gallery_id: UUID,
    payload: GalleryUpgradeRequestCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:write")),
):
    item = gallery_service.create_upgrade_request(db, gallery_id, payload, context)
    return api_response("Upgrade request created", GalleryUpgradeRequestRead.model_validate(item).model_dump(mode="json"))


@router.get("/{gallery_id}/upgrade-requests", response_model=APIResponse)
def list_upgrade_requests(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:read")),
):
    items = gallery_service.list_upgrade_requests(db, gallery_id, context)
    return api_response("Upgrade requests retrieved", [GalleryUpgradeRequestRead.model_validate(i).model_dump(mode="json") for i in items])


@router.put("/upgrade-requests/{request_id}/approve", response_model=APIResponse)
def approve_upgrade_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:write")),
):
    item = gallery_service.approve_upgrade_request(db, request_id, context)
    return api_response("Upgrade request approved", GalleryUpgradeRequestRead.model_validate(item).model_dump(mode="json"))


@router.put("/upgrade-requests/{request_id}/reject", response_model=APIResponse)
def reject_upgrade_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:write")),
):
    item = gallery_service.reject_upgrade_request(db, request_id, context)
    return api_response("Upgrade request rejected", GalleryUpgradeRequestRead.model_validate(item).model_dump(mode="json"))


@router.put("/upgrade-requests/{request_id}/mark-paid", response_model=APIResponse)
def mark_upgrade_paid(
    request_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:write")),
):
    item = gallery_service.mark_upgrade_paid(db, request_id, context)
    return api_response("Upgrade request marked paid", GalleryUpgradeRequestRead.model_validate(item).model_dump(mode="json"))


@router.post("/{gallery_id}/reopen-selection", response_model=APIResponse)
def reopen_selection(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("galleries:reopen")),
):
    item = gallery_service.reopen_selection(db, gallery_id, context)
    return api_response("Gallery selection reopened", GalleryDetailRead.model_validate(gallery_service.gallery_to_detail(item)).model_dump(mode="json"))
