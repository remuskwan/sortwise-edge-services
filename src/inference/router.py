from fastapi import APIRouter

router = APIRouter(
    prefix="/inference",
    tags=["inference"],
    responses={404: {"description": "Not found"}},
)


@router.get("/all/{user_id}")
async def get_all_inference_results(user_id: str):
    """Get all inference results for a user."""


@router.get("/{object_key}")
async def get_inference_result(object_key: str):
    """Get a specific inference result."""
