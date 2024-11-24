from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models import LineUser
from app.enum.province import Province

router = APIRouter()


@router.post("/set-province")
async def set_province(user_id: str, province_name: str, session: AsyncSession = Depends(deps.get_session)):
    """
    Set the province for a LINE user.

    Parameters:
    - user_id (str): LINE User ID
    - province_name (str): Province name (in Thai or English)

    Returns:
    - JSON response with a success or failure message.
    """
    matched_province = next(
        (
            province
            for province in Province
            if province.value.name_th == province_name or province.value.name_en == province_name
        ),
        None,
    )

    if not matched_province:
        raise HTTPException(status_code=400, detail="Invalid province name. Please try again.")

    result = await session.get(LineUser, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found in the database.")

    result.province = matched_province.value.name_th
    session.add(result)
    await session.commit()

    return {"message": f"Province successfully set to: {matched_province.value.name_th}"}
